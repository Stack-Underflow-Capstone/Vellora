import { View, Text } from "react-native";
import React from "react";
import { router } from "expo-router";
import ScreenLayout from "../components/ScreenLayout";
import Button from "../components/Button";

const profile = () => {
	return (
		<ScreenLayout
			footer={
				<Button
					title="Generate Report"
					onPress={() => router.push("/report" as any)}
				/>
			}>
			<View className="flex-1 px-6 pt-6">
				<Text className="text-2xl font-bold text-textBlack mb-6">Profile</Text>
				<Text className="text-base text-gray-600">
					Generate a report of your trips by selecting a date range.
				</Text>
			</View>
		</ScreenLayout>
	);
};

export default profile;
