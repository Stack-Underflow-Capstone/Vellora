import { Stack } from "expo-router";
import "./globals.css";
import { TripDataProvider } from "./contexts/TripDataContext";

export default function RootLayout() {
	return (
		<TripDataProvider>
			<Stack>
				<Stack.Screen name="login" options={{ headerShown: false }} />
				<Stack.Screen name="(tabs)" options={{ headerShown: false }} />
			</Stack>
		</TripDataProvider>
	);
}

