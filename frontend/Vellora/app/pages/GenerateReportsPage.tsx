import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import DateTimePicker, {
	DateTimePickerEvent,
} from "@react-native-community/datetimepicker";
import ScreenLayout from "../components/ScreenLayout";
import Button from "../components/Button";
import { reportStyles } from "../styles/ReportStyles";
import { generateReport } from "../services/reports";
import { tokenStorage } from "../services/tokenStorage";

export default function GenerateReportPage() {
	const [fromDate, setFromDate] = useState<Date>(new Date());
	const [toDate, setToDate] = useState<Date>(new Date());
	const [showFromPicker, setShowFromPicker] = useState(false);
	const [showToPicker, setShowToPicker] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	const handleFromDateChange = (
		event: DateTimePickerEvent,
		selectedDate?: Date
	) => {
		setShowFromPicker(false);
		if (selectedDate) {
			setFromDate(selectedDate);
		}
	};

	const handleToDateChange = (
		event: DateTimePickerEvent,
		selectedDate?: Date
	) => {
		setShowToPicker(false);
		if (selectedDate) {
			setToDate(selectedDate);
		}
	};

	const formatDate = (date: Date): string => {
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric",
		});
	};

	const formatDateForAPI = (date: Date): string => {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, "0");
		const day = String(date.getDate()).padStart(2, "0");
		return `${year}-${month}-${day}`;
	};

	const handleGenerate = async () => {
		if (fromDate > toDate) {
			setError("End date must be after start date");
			return;
		}

		const token = tokenStorage.getToken();
		if (!token) {
			router.replace("/login");
			return;
		}

		setError(null);
		setLoading(true);

		try {
			const report = await generateReport(
				formatDateForAPI(fromDate),
				formatDateForAPI(toDate),
				token
			);

			router.push({
				pathname: "/generating-report",
				params: {
					reportId: report.id,
				},
			} as any);
		} catch (err) {
			const errorMessage =
				err instanceof Error
					? err.message
					: "Failed to generate report. Please try again.";
			setError(errorMessage);
			console.error("Failed to generate report:", err);
		} finally {
			setLoading(false);
		}
	};

	return (
		<ScreenLayout
			footer={
				<View>
					<Pressable
						style={reportStyles.historyButton}
						onPress={() => router.push("/report-details" as any)}>
						<Text style={reportStyles.historyText}>View Report History</Text>
					</Pressable>
					<Button
						title={loading ? "Generating..." : "Generate Report"}
						onPress={handleGenerate}
						className="mt-3 py-4 px-5"
						disabled={loading}
					/>
				</View>
			}>
			<View className="flex-1 px-6 pt-6">
				<Text style={reportStyles.title}>Generate Report</Text>

				<Text style={reportStyles.sectionLabel}>Select Date Range</Text>

				{error && (
					<View
						style={{
							backgroundColor: "#FEE2E2",
							padding: 12,
							borderRadius: 8,
							marginBottom: 16,
						}}>
						<Text style={{ color: "#DC2626", fontSize: 14 }}>{error}</Text>
					</View>
				)}

				<View style={reportStyles.card}>
					<Text style={reportStyles.inputLabel}>From Date</Text>
					<Pressable
						style={reportStyles.inputBox}
						onPress={() => setShowFromPicker(true)}>
						<Text style={reportStyles.inputText}>{formatDate(fromDate)}</Text>
					</Pressable>
					{showFromPicker && (
						<DateTimePicker
							value={fromDate}
							mode="date"
							display="default"
							onChange={handleFromDateChange}
						/>
					)}

					<Text style={[reportStyles.inputLabel, { marginTop: 16 }]}>
						To Date
					</Text>
					<Pressable
						style={reportStyles.inputBox}
						onPress={() => setShowToPicker(true)}>
						<Text style={reportStyles.inputText}>{formatDate(toDate)}</Text>
					</Pressable>
					{showToPicker && (
						<DateTimePicker
							value={toDate}
							mode="date"
							display="default"
							onChange={handleToDateChange}
						/>
					)}
				</View>
			</View>
		</ScreenLayout>
	);
}
