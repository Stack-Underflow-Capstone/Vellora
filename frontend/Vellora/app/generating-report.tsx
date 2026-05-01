import { useState, useEffect, useRef } from "react";
import { View, Text, ActivityIndicator } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import ScreenLayout from "./components/ScreenLayout";
import Button from "./components/Button";
import { Colors } from "./Colors";
import {
	getReportStatus,
	downloadReport,
	downloadAndOpenReport,
	ReportStatus,
} from "./services/reports";
import { tokenStorage } from "./services/tokenStorage";
import {
	reportPageStyles,
	getStatusColor,
	getProgressPercent,
} from "./styles/ReportPageStyles";

export default function GeneratingReportPage() {
	const params = useLocalSearchParams();
	const [status, setStatus] = useState<ReportStatus>("pending");
	const [error, setError] = useState<string | null>(null);
	const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
		null
	);
	const isMountedRef = useRef(true);
	const pollingStartTimeRef = useRef<number>(Date.now());
	const MAX_POLLING_TIME = 5 * 60 * 1000;

	useEffect(() => {
		isMountedRef.current = true;
		const reportId = params.reportId as string;

		if (!reportId) {
			router.back();
			return;
		}

		const startPolling = async () => {
			const token = tokenStorage.getToken();
			if (!token) {
				router.replace("/login");
				return;
			}

			const poll = async () => {
				try {
					const elapsedTime = Date.now() - pollingStartTimeRef.current;

					if (elapsedTime > MAX_POLLING_TIME) {
						if (pollingIntervalRef.current) {
							clearInterval(pollingIntervalRef.current);
						}
						setError(
							"Report generation is taking too long. The worker may not be running. Please try again later."
						);
						return;
					}

					const statusResponse = await getReportStatus(reportId, token);
					if (!isMountedRef.current) return;

					setStatus(statusResponse.status);

					if (statusResponse.status === "completed") {
						if (pollingIntervalRef.current) {
							clearInterval(pollingIntervalRef.current);
						}
						setTimeout(() => {
							if (isMountedRef.current) {
								handleDownload(reportId, token);
							}
						}, 2500);
					} else if (
						statusResponse.status === "failed" ||
						statusResponse.status === "expired"
					) {
						if (pollingIntervalRef.current) {
							clearInterval(pollingIntervalRef.current);
						}
						setError(`Report generation ${statusResponse.status}`);
					} else if (
						statusResponse.status === "pending" &&
						elapsedTime > 30000
					) {
						console.warn(
							"Report has been pending for over 30 seconds. Worker may not be running."
						);
					}
				} catch (err) {
					if (!isMountedRef.current) return;
					console.error("Polling error:", err);
				}
			};

			await poll();

			pollingIntervalRef.current = setInterval(poll, 2500);
		};

		startPolling();

		return () => {
			isMountedRef.current = false;
			if (pollingIntervalRef.current) {
				clearInterval(pollingIntervalRef.current);
			}
		};
	}, [params]);

	const handleDownload = async (reportId: string, token: string) => {
		try {
			const downloadResponse = await downloadReport(reportId, token);
			if (downloadResponse.download_url) {
				await downloadAndOpenReport(downloadResponse.download_url, reportId);
			}
			setTimeout(() => {
				router.replace("/report-details" as any);
			}, 1000);
		} catch (err) {
			setError(
				err instanceof Error ? err.message : "Failed to download report"
			);
		}
	};

	const getStatusText = () => {
		switch (status) {
			case "pending":
				return "Pending";
			case "processing":
				return "Processing";
			case "completed":
				return "Completed";
			case "failed":
				return "Failed";
			case "expired":
				return "Expired";
		}
	};

	const isDownloadDisabled = status === "pending" || status === "processing";

	return (
		<ScreenLayout
			footer={
				status === "completed" ? (
					<Button
						title="View History"
						onPress={() => router.replace("/report-details" as any)}
					/>
				) : (
					<Button
						title="Download"
						onPress={() => {
							const reportId = params.reportId as string;
							const token = tokenStorage.getToken();
							if (reportId && token) {
								handleDownload(reportId, token);
							}
						}}
						disabled={isDownloadDisabled}
					/>
				)
			}>
			<View style={reportPageStyles.generatingContainer}>
				<Text style={reportPageStyles.generatingTitle}>Generating</Text>

				{status !== "failed" && status !== "expired" && (
					<ActivityIndicator
						size="large"
						color={Colors.primaryPurple}
						style={{ marginBottom: 32 }}
					/>
				)}

				{error && <Text style={reportPageStyles.errorMessage}>{error}</Text>}

				<View style={reportPageStyles.progressBarContainer}>
					<View style={reportPageStyles.progressBarBackground}>
						<View
							style={[
								reportPageStyles.progressBarFill,
								{
									width: `${getProgressPercent(status)}%`,
									backgroundColor: getStatusColor(status),
								},
							]}
						/>
					</View>
				</View>

				<View style={reportPageStyles.statusLabelsContainer}>
					<Text
						style={[
							reportPageStyles.statusLabel,
							status === "pending"
								? reportPageStyles.statusLabelActive
								: reportPageStyles.statusLabelInactive,
						]}>
						Pending
					</Text>
					<Text
						style={[
							reportPageStyles.statusLabel,
							status === "processing"
								? reportPageStyles.statusLabelActive
								: reportPageStyles.statusLabelInactive,
						]}>
						Processing
					</Text>
					<Text
						style={[
							reportPageStyles.statusLabel,
							status === "completed"
								? reportPageStyles.statusLabelCompleted
								: reportPageStyles.statusLabelInactive,
						]}>
						Completed
					</Text>
				</View>

				<Text style={reportPageStyles.statusText}>{getStatusText()}...</Text>
			</View>
		</ScreenLayout>
	);
}
