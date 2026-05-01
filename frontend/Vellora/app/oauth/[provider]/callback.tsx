import { useEffect, useState } from "react";
import { View, Text, ActivityIndicator } from "react-native";
import { router, useLocalSearchParams, useSegments } from "expo-router";
import { tokenStorage } from "../../services/tokenStorage";
import { handleOAuthCallback } from "../../services/auth";

export default function OAuthCallback() {
	const params = useLocalSearchParams();
	const segments = useSegments();
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const processCallback = async () => {
			try {
				const accessToken = params.access_token as string;
				const code = params.code as string;
				const state = params.state as string;
				const segmentsArray = segments as readonly string[];
				const provider =
					(params.provider as string) ||
					(segmentsArray.length > 1 ? segmentsArray[1] : undefined) ||
					"google";

				if (accessToken) {
					tokenStorage.setToken(accessToken);
					const redirect = params.redirect as string;
					if (redirect) {
						router.replace(redirect as any);
					} else {
						router.replace("/(tabs)");
					}
					return;
				}

				if (code && state) {
					const redirectUri = params.redirect_uri as string;
					const response = await handleOAuthCallback(
						provider,
						code,
						state,
						redirectUri
					);
					tokenStorage.setToken(response.tokens.access_token);

					const redirect = params.redirect as string;
					if (redirect) {
						router.replace(redirect as any);
					} else {
						router.replace("/(tabs)");
					}
					return;
				}

				setError("Missing authorization code or access token.");
				setLoading(false);
			} catch (err) {
				setError(err instanceof Error ? err.message : "Authentication failed.");
				setLoading(false);
			}
		};

		processCallback();
	}, [params, segments]);

	if (loading) {
		return (
			<View
				style={{
					flex: 1,
					justifyContent: "center",
					alignItems: "center",
					backgroundColor: "#fff",
				}}>
				<ActivityIndicator size="large" color="#000" />
				<Text style={{ marginTop: 16, fontSize: 16 }}>
					Completing sign in...
				</Text>
			</View>
		);
	}

	if (error) {
		return (
			<View
				style={{
					flex: 1,
					justifyContent: "center",
					alignItems: "center",
					backgroundColor: "#fff",
					padding: 20,
				}}>
				<Text style={{ fontSize: 16, color: "#ef4444", textAlign: "center" }}>
					{error}
				</Text>
				<Text
					style={{
						marginTop: 20,
						fontSize: 14,
						color: "#3b82f6",
						textDecorationLine: "underline",
					}}
					onPress={() => router.replace("/login")}>
					Return to Login
				</Text>
			</View>
		);
	}

	return null;
}
