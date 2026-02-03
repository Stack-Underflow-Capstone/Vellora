import { Platform } from "react-native";

export const API_BASE_URL =
	process.env.EXPO_PUBLIC_API_BASE_URL ??
	(Platform.OS === "android"
		? "http://10.0.2.2:8000/api/v1"
		: Platform.OS === "web"
		? "http://localhost:8000/api/v1"
		: "http://localhost:8000/api/v1");

export const AUTH_ROUTES = {
	register: `${API_BASE_URL}/auth/register`,
	login: `${API_BASE_URL}/auth/login`,
	providerAuthorize: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/authorize`,
	providerCallback: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/callback`,
};

export const getOAuthRedirectUri = () => {
	if (Platform.OS === "android") {
		return (
			process.env.EXPO_PUBLIC_ANDROID_REDIRECT_URI ??
			"http://localhost:8000/api/v1/auth/providers/google/callback"
		);
	}
	return "http://localhost:8000/api/v1/auth/providers/google/callback";
};
