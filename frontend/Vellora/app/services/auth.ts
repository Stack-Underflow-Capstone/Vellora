import { AUTH_ROUTES } from "../constants/api";

export type AuthTokens = {
	access_token: string;
	refresh_token: string;
	token_type: string;
	access_token_expires_in: number;
	refresh_token_expires_in: number;
};

export type AuthUser = {
	id: string;
	email: string;
	role: string;
	full_name?: string | null;
};

export type AuthResponse = {
	user: AuthUser;
	tokens: AuthTokens;
};

class ApiError extends Error {
	status?: number;
	constructor(message: string, status?: number) {
		super(message);
		this.status = status;
	}
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (response.ok) {
		return response.json() as Promise<T>;
	}

	const fallback = await response.text();
	let message = fallback || "Request failed";
	try {
		const data = JSON.parse(fallback);
		message = data.detail ?? data.message ?? message;
	} catch {}
	throw new ApiError(message, response.status);
}

export async function login(
	email: string,
	password: string
): Promise<AuthResponse> {
	const body = new URLSearchParams({
		username: email,
		password,
	});

	const response = await fetch(AUTH_ROUTES.login, {
		method: "POST",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		},
		body: body.toString(),
	});

	return handleResponse<AuthResponse>(response);
}

type RegisterPayload = {
	email: string;
	password: string;
	full_name?: string;
};

export async function register(
	payload: RegisterPayload
): Promise<AuthResponse> {
	const response = await fetch(AUTH_ROUTES.register, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			email: payload.email,
			password: payload.password,
			full_name: payload.full_name ?? payload.email.split("@")[0],
			role: "employee",
		}),
	});

	return handleResponse<AuthResponse>(response);
}

export type ProviderAuthorizeResponse = {
	provider: string;
	authorization_url: string;
	state: string;
	redirect_uri: string;
};

export async function getProviderAuthorizeUrl(
	provider: string,
	redirect_uri?: string
): Promise<ProviderAuthorizeResponse> {
	const url = new URL(AUTH_ROUTES.providerAuthorize(provider));
	if (redirect_uri) {
		url.searchParams.set("redirect_uri", redirect_uri);
	}
	const response = await fetch(url.toString());
	return handleResponse<ProviderAuthorizeResponse>(response);
}

export async function handleOAuthCallback(
	provider: string,
	code: string,
	state: string,
	redirect_uri?: string
): Promise<AuthResponse> {
	const url = new URL(AUTH_ROUTES.providerCallback(provider));
	url.searchParams.set("code", code);
	url.searchParams.set("state", state);
	if (redirect_uri) {
		url.searchParams.set("redirect_uri", redirect_uri);
	}
	const response = await fetch(url.toString(), {
		headers: {
			Accept: "application/json",
		},
	});
	return handleResponse<AuthResponse>(response);
}
