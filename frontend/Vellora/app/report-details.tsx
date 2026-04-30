import {
	View,
	Text,
	ScrollView,
	TouchableOpacity,
	Pressable,
} from "react-native";
import { useState, useEffect, useRef } from "react";
import { useNavigation } from "expo-router";
import ScreenLayout from "./components/ScreenLayout";
import {
	getReportsHistory,
	downloadReport,
	retryReport,
	regenerateReport,
	getReportStatus,
	downloadAndOpenReport,
	Report,
	ReportStatus,
} from "./services/reports";
import { tokenStorage } from "./services/tokenStorage";
import { router } from "expo-router";
import { Colors } from "./Colors";
import {
	reportPageStyles,
	getStatusTextColor,
} from "./styles/ReportPageStyles";

export default function ReportDetailsPage() {
	const navigation = useNavigation();
	const [reports, setReports] = useState<Report[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const regeneratingRef = useRef<Set<string>>(new Set());
	const pollingIntervalsRef = useRef<
		Map<string, ReturnType<typeof setInterval>>
	>(new Map());

	useEffect(() => {
		navigation.setOptions({
			headerLeft: () => (
				<Pressable
					onPress={() => router.back()}
					style={{ marginLeft: 16, padding: 8 }}>
					<Text style={{ fontSize: 18, color: Colors.primaryPurple }}>
						{"<"}
					</Text>
				</Pressable>
			),
		});
	}, [navigation]);

	useEffect(() => {
		fetchReports();
		return () => {
			pollingIntervalsRef.current.forEach((interval) =>
				clearInterval(interval)
			);
		};
	}, []);

	const fetchReports = async () => {
		const token = tokenStorage.getToken();
		if (!token) {
			router.replace("/login");
			return;
		}

		setLoading(true);
		setError(null);
		try {
			const reportsData = await getReportsHistory(token);
			setReports(reportsData);
			startPollingForProcessingReports(reportsData, token);
		} catch (err) {
			console.error("Error fetching reports:", err);
			if (
				(err instanceof Error &&
					(err.message.includes("Authentication required") ||
						err.message.includes("Unauthorized"))) ||
				(err as any).status === 401
			) {
				tokenStorage.clearToken();
				router.replace("/login");
				return;
			}
			const errorMessage =
				err instanceof Error
					? err.message
					: (err as any)?.status === 500
					? "Internal server error. Please try again later."
					: "Failed to load reports. Please try again.";
			setError(errorMessage);
		} finally {
			setLoading(false);
		}
	};

	const formatDateRange = (startDate: string, endDate: string): string => {
		const start = new Date(startDate);
		const end = new Date(endDate);
		const startFormatted = start.toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
		});
		const endFormatted = end.toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
		});
		return `${startFormatted} - ${endFormatted}`;
	};

	const formatCreatedDate = (dateString: string): string => {
		const date = new Date(dateString);
		return date.toLocaleDateString("en-US", {
			month: "short",
			day: "numeric",
		});
	};

	const isStuckProcessing = (report: Report): boolean => {
		if (report.status !== "processing") return false;
		const requestedAt = new Date(report.requested_at).getTime();
		const now = Date.now();
		const fiveMinutes = 5 * 60 * 1000;
		return now - requestedAt > fiveMinutes;
	};

	const getActionText = (report: Report): string => {
		switch (report.status) {
			case "completed":
				return "Download";
			case "failed":
				return "Retry";
			case "expired":
				return "Regenerate";
			case "pending":
				return "Processing...";
			case "processing":
				return isStuckProcessing(report) ? "Retry" : "Processing...";
			default:
				return "";
		}
	};

	const isActionDisabled = (report: Report): boolean => {
		if (report.status === "pending") return true;
		if (report.status === "processing" && !isStuckProcessing(report))
			return true;
		return false;
	};

	const handleAction = async (report: Report) => {
		const token = tokenStorage.getToken();
		if (!token) {
			router.replace("/login");
			return;
		}

		try {
			if (report.status === "completed") {
				try {
					const downloadResponse = await downloadReport(report.id, token);
					if (downloadResponse.download_url) {
						await downloadAndOpenReport(
							downloadResponse.download_url,
							report.id
						);
					}
				} catch (downloadError: any) {
					if (downloadError.status === 410) {
						setError("Report has expired. Please regenerate it.");
						await fetchReports();
					} else {
						throw downloadError;
					}
				}
			} else if (
				report.status === "failed" ||
				(report.status === "processing" && isStuckProcessing(report))
			) {
				try {
					await retryReport(report.id, token);
					await fetchReports();
					router.push({
						pathname: "/generating-report",
						params: { reportId: report.id },
					} as any);
				} catch (retryError: any) {
					if (
						retryError.status === 400 ||
						retryError.message.includes("Only failed or expired")
					) {
						setError(
							"Report is stuck in processing. Please wait or contact support."
						);
					} else {
						throw retryError;
					}
				}
			} else if (report.status === "expired") {
				const regenerateResponse = await regenerateReport(report.id, token);
				if (
					regenerateResponse.status === "available" &&
					regenerateResponse.download_url
				) {
					await downloadAndOpenReport(
						regenerateResponse.download_url,
						report.id
					);
					await fetchReports();
				} else if (regenerateResponse.status === "regenerating") {
					await fetchReports();
					router.push({
						pathname: "/generating-report",
						params: { reportId: report.id },
					} as any);
				}
			}
		} catch (err) {
			console.error("Action error:", err);
			const errorMessage =
				err instanceof Error
					? err.message
					: (err as any)?.status === 500
					? "Internal server error. Please try again."
					: "An error occurred. Please try again.";
			setError(errorMessage);
		}
	};

	const startPollingForProcessingReports = (
		reports: Report[],
		token: string
	) => {
		reports.forEach((report) => {
			if (report.status === "pending" || report.status === "processing") {
				startPollingForReport(report.id, token);
			} else {
				stopPollingForReport(report.id);
			}
		});
	};

	const startPollingForReport = (reportId: string, token: string) => {
		if (pollingIntervalsRef.current.has(reportId)) {
			return;
		}

		const interval = setInterval(async () => {
			try {
				const statusResponse = await getReportStatus(reportId, token);
				if (
					statusResponse.status === "completed" ||
					statusResponse.status === "failed" ||
					statusResponse.status === "expired"
				) {
					stopPollingForReport(reportId);
					await fetchReports();
				}
			} catch (err) {
				console.error("Polling error:", err);
				stopPollingForReport(reportId);
			}
		}, 2500);

		pollingIntervalsRef.current.set(reportId, interval);
	};

	const stopPollingForReport = (reportId: string) => {
		const interval = pollingIntervalsRef.current.get(reportId);
		if (interval) {
			clearInterval(interval);
			pollingIntervalsRef.current.delete(reportId);
		}
	};

	const startPollingForRegenerate = (reportId: string, token: string) => {
		if (pollingIntervalsRef.current.has(reportId)) {
			clearInterval(pollingIntervalsRef.current.get(reportId)!);
		}

		const interval = setInterval(async () => {
			try {
				const statusResponse = await getReportStatus(reportId, token);
				if (statusResponse.status === "completed") {
					clearInterval(interval);
					pollingIntervalsRef.current.delete(reportId);
					regeneratingRef.current.delete(reportId);
					await fetchReports();
				} else if (
					statusResponse.status === "failed" ||
					statusResponse.status === "expired"
				) {
					clearInterval(interval);
					pollingIntervalsRef.current.delete(reportId);
					regeneratingRef.current.delete(reportId);
					await fetchReports();
				}
			} catch (err) {
				console.error("Polling error:", err);
				clearInterval(interval);
				pollingIntervalsRef.current.delete(reportId);
				regeneratingRef.current.delete(reportId);
			}
		}, 2500);

		pollingIntervalsRef.current.set(reportId, interval);
	};

	const handleRefresh = () => {
		fetchReports();
	};

	return (
		<ScreenLayout footer={<View />}>
			<View className="flex-1 bg-backgroundGrey">
				<View style={[reportPageStyles.headerContainer, { paddingTop: 16 }]}>
					<View style={{ flex: 1 }} />
					<View style={{ flex: 1, alignItems: "flex-end" }}>
						<Pressable
							onPress={handleRefresh}
							style={reportPageStyles.refreshButton}>
							<Text style={reportPageStyles.refreshButtonText}>Refresh</Text>
						</Pressable>
					</View>
				</View>

				<View style={reportPageStyles.tableHeader}>
					<View style={reportPageStyles.tableCell}>
						<Text style={reportPageStyles.tableHeaderText}>Range</Text>
					</View>
					<View style={reportPageStyles.tableCell}>
						<Text style={reportPageStyles.tableHeaderText}>Status</Text>
					</View>
					<View style={reportPageStyles.tableCell}>
						<Text style={reportPageStyles.tableHeaderText}>Created</Text>
					</View>
					<View style={reportPageStyles.tableCell}>
						<Text style={reportPageStyles.tableHeaderText}>Action</Text>
					</View>
				</View>

				{loading ? (
					<View style={reportPageStyles.loadingContainer}>
						<Text style={reportPageStyles.loadingText}>Loading reports...</Text>
					</View>
				) : error ? (
					<View style={reportPageStyles.errorContainer}>
						<Text style={reportPageStyles.errorText}>{error}</Text>
						<Pressable onPress={handleRefresh}>
							<Text style={reportPageStyles.retryText}>Retry</Text>
						</Pressable>
					</View>
				) : (
					<ScrollView style={{ flex: 1 }}>
						{reports.length === 0 ? (
							<View style={reportPageStyles.emptyContainer}>
								<Text style={reportPageStyles.emptyText}>No reports found</Text>
							</View>
						) : (
							reports.map((report) => (
								<View key={report.id} style={reportPageStyles.tableRow}>
									<View style={reportPageStyles.tableCell}>
										<Text style={reportPageStyles.tableCellText}>
											{formatDateRange(report.start_date, report.end_date)}
										</Text>
									</View>
									<View style={reportPageStyles.tableCell}>
										<Text
											style={[
												reportPageStyles.tableCellText,
												{
													fontWeight: "500",
													color: getStatusTextColor(report.status),
												},
											]}>
											{report.status.charAt(0).toUpperCase() +
												report.status.slice(1)}
										</Text>
									</View>
									<View style={reportPageStyles.tableCell}>
										<Text style={reportPageStyles.tableCellText}>
											{formatCreatedDate(report.requested_at)}
										</Text>
									</View>
									<View style={reportPageStyles.tableCell}>
										<TouchableOpacity
											onPress={() => handleAction(report)}
											disabled={isActionDisabled(report)}>
											<Text
												style={
													isActionDisabled(report)
														? reportPageStyles.actionTextDisabled
														: reportPageStyles.actionText
												}>
												{getActionText(report)}
											</Text>
										</TouchableOpacity>
									</View>
								</View>
							))
						)}
					</ScrollView>
				)}
			</View>
		</ScreenLayout>
	);
}
