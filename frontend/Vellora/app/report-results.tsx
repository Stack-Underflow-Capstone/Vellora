import { View, Text, ScrollView } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import ScreenLayout from "./components/ScreenLayout";
import Button from "./components/Button";

export default function ReportResultsPage() {
	const params = useLocalSearchParams();
	const fromDate = params.fromDate as string;
	const toDate = params.toDate as string;

	const formatDate = (dateString: string): string => {
		const date = new Date(dateString);
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "long",
			day: "numeric",
		});
	};

	return (
		<ScreenLayout
			footer={
				<View>
					<Button title="Generate New Report" onPress={() => router.back()} />
					<Button title="Generate PDF" onPress={() => {}} className="mt-3" />
				</View>
			}>
			<ScrollView className="flex-1 px-6 pt-6">
				<Text className="text-2xl font-bold text-textBlack mb-6">
					Trip Report
				</Text>

				<View className="bg-backgroundGrey p-4 rounded-xl mb-6">
					<Text className="text-sm text-gray-600 mb-2">Report Period</Text>
					<Text className="text-base font-semibold text-textBlack">
						{formatDate(fromDate)} - {formatDate(toDate)}
					</Text>
				</View>

				<View className="mb-6">
					<Text className="text-lg font-semibold text-textBlack mb-4">
						Summary
					</Text>
					<View className="bg-backgroundGrey p-4 rounded-xl">
						<View className="flex-row justify-between mb-3 pb-3 border-b border-gray-300">
							<Text className="text-sm text-gray-600">Total Trips:</Text>
							<Text className="text-sm font-semibold text-textBlack">
								{/* the backend point for the total trips, unless you wanted something else to go here */}
							</Text>
						</View>
						<View className="flex-row justify-between mb-3 pb-3 border-b border-gray-300">
							<Text className="text-sm text-gray-600">Total Miles:</Text>
							<Text className="text-sm font-semibold text-textBlack">
								{/* I have it set for total miles but again im not sure what they are suppose to be but heres another slot */}
							</Text>
						</View>
						<View className="flex-row justify-between">
							<Text className="text-sm text-gray-600">
								Total Reimbursement:
							</Text>
							<Text className="text-sm font-semibold text-accentGreen">
								{/* Another oneeeeeee (you can add more veiws and create more sections or delete sections if you want)*/}
							</Text>
						</View>
					</View>
				</View>

				<View className="mb-6">
					<Text className="text-lg font-semibold text-textBlack mb-4">
						Trips
					</Text>
					<View className="bg-backgroundGrey p-4 rounded-xl">
						<Text className="text-sm text-gray-500 text-center py-4">
							you can put cool extra details here if it calls for it
						</Text>
					</View>
				</View>
			</ScrollView>
		</ScreenLayout>
	);
}
