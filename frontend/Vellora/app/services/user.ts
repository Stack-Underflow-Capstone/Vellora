import { AUTH_ROUTES, TRIP_ROUTES } from "../constants/api";
import { ApiError, handleResponse, checkToken } from "./helpers";

export type User = {
	id: string;
	email: string;
	full_name: string | null;
	username: string | null;
	is_active: boolean;
	role: string;
	created_at: string;
	updated_at: string;
};

export type UserUpdatePayload = {
	full_name?: string | null;
	username?: string | null;
	current_password?: string | null;
	new_password?: string | null;
};

export type TripCounts = {
	total_trips: number;
	total_scheduled: number;
};

export async function getCurrentUser(): Promise<User> {
	const token = await checkToken();

	const response = await fetch(AUTH_ROUTES.me, {
		method: "GET",
		headers: {
			"Authorization": `Bearer ${token}`,
			"Content-Type": "application/json",
		},
	});

	return handleResponse<User>(response);
}

export async function updateUserProfile(payload: UserUpdatePayload): Promise<User> {
	const token = await checkToken();

	const response = await fetch(AUTH_ROUTES.me, {
		method: "PATCH",
		headers: {
			"Authorization": `Bearer ${token}`,
			"Content-Type": "application/json",
		},
		body: JSON.stringify(payload),
	});

	return handleResponse<User>(response);
}

export async function getTripCounts(): Promise<TripCounts> {
	const token = await checkToken();

	const response = await fetch(TRIP_ROUTES.counts, {
		method: "GET",
		headers: {
			"Authorization": `Bearer ${token}`,
			"Content-Type": "application/json",
		},
	});

	return handleResponse<TripCounts>(response);
}