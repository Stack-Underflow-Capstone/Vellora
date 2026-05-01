import { Platform } from "react-native";

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL

export const AUTH_ROUTES = {
	register: `${API_BASE_URL}/auth/register`,
	login: `${API_BASE_URL}/auth/login`,
	me: `${API_BASE_URL}/auth/me`,
	providerAuthorize: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/authorize`,
	providerCallback: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/callback`,
};

export const TRIP_ROUTES = {
	counts: `${API_BASE_URL}/trips/counts`,
};

export const AI_ROUTES = {
	tripAssistant: `${API_BASE_URL}/ai/trip-assistant`,
	routeWeather: `${API_BASE_URL}/ai/route-weather`,
};

export const getOAuthRedirectUri = () => {
	if (Platform.OS === "android") {
		return (
			process.env.EXPO_PUBLIC_ANDROID_REDIRECT_URI ??
			`${API_BASE_URL}/api/v1/auth/providers/google/callback`
		);
	}
	return `${API_BASE_URL}/auth/providers/google/callback`;
};
