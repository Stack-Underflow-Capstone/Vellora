import { Stack } from "expo-router";
import "./globals.css";
import { TripDataProvider } from "./contexts/TripDataContext";
export default function RootLayout() {
	return (
		<TripDataProvider>
			<Stack>
				<Stack.Screen name="index" options={{ headerShown: false }} />
				<Stack.Screen name="onboarding" options={{ headerShown: false }} />
				<Stack.Screen name="onboarding2" options={{ headerShown: false }} />
				<Stack.Screen name="welcome" options={{ headerShown: false }} />
				<Stack.Screen name="(tabs)" options={{ headerShown: false }} />
				<Stack.Screen name="chatBot" options={{ headerShown: false }} />
				<Stack.Screen
					name="report-details"
					options={{
						headerShown: true,
						title: "Reports History",
						headerBackTitle: "(tabs)",
					}}
				/>
			</Stack>
		</TripDataProvider>
	);
}
