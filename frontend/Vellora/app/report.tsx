import { useState } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { router } from "expo-router";
import DateTimePicker, {
	DateTimePickerEvent,
} from "@react-native-community/datetimepicker";
import ScreenLayout from "./components/ScreenLayout";
import Button from "./components/Button";

export default function ReportPage() {
	const [fromDate, setFromDate] = useState<Date>(new Date());
	const [toDate, setToDate] = useState<Date>(new Date());
	const [showFromPicker, setShowFromPicker] = useState(false);
	const [showToPicker, setShowToPicker] = useState(false);

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

	const handleConfirm = () => {
		if (fromDate > toDate) {
			return;
		}
		router.push({
			pathname: "/report-results",
			params: {
				fromDate: fromDate.toISOString(),
				toDate: toDate.toISOString(),
			},
		} as any);
	};

	const formatDate = (date: Date): string => {
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric",
		});
	};

	return (
		<ScreenLayout
			footer={<Button title="Confirm Report" onPress={handleConfirm} />}>
			<View className="flex-1 px-6 pt-6">
				<Text className="text-2xl font-bold text-textBlack mb-6">
					Generate Report
				</Text>

				<View className="mb-6">
					<Text className="text-base font-semibold text-textBlack mb-3">
						Select Date Range
					</Text>

					<View className="mb-4">
						<Text className="text-sm text-gray-600 mb-2">From Date</Text>
						<TouchableOpacity
							onPress={() => setShowFromPicker(true)}
							className="bg-backgroundGrey p-4 rounded-xl border border-gray-300">
							<Text className="text-base text-textBlack">
								{formatDate(fromDate)}
							</Text>
						</TouchableOpacity>
						{showFromPicker && (
							<DateTimePicker
								value={fromDate}
								mode="date"
								display="default"
								onChange={handleFromDateChange}
							/>
						)}
					</View>

					<View className="mb-4">
						<Text className="text-sm text-gray-600 mb-2">To Date</Text>
						<TouchableOpacity
							onPress={() => setShowToPicker(true)}
							className="bg-backgroundGrey p-4 rounded-xl border border-gray-300">
							<Text className="text-base text-textBlack">
								{formatDate(toDate)}
							</Text>
						</TouchableOpacity>
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

				<View className="flex-1 justify-center items-center py-8">
					<Text className="text-gray-500 text-center">
						Select a date range and confirm to generate your report.
					</Text>
				</View>
			</View>
		</ScreenLayout>
	);
}
