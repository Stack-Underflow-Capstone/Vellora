export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const AUTH_ROUTES = {
	register: `${API_BASE_URL}/auth/register`,
	login: `${API_BASE_URL}/auth/login`,
	providerAuthorize: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/authorize`,
	providerCallback: (provider: string) =>
		`${API_BASE_URL}/auth/providers/${provider}/callback`,
};

export const TRIP_ROUTES = {
	createTrip: `${API_BASE_URL}/trips/manual`
}
