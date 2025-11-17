import { tokenStorage } from "./tokenStorage";

// Class to help with ApiErrors when calling
export class ApiError extends Error {
	status?: number;
	constructor(message: string, status?: number) {
		super(message);
		this.status = status;
	}
}

// Handle response with generic Type 'T'
export async function handleResponse<T>(response: Response): Promise<T> {
	if (response.ok) {
		return response.json() as Promise<T>;
	}

	const fallback = await response.text();
	let message = fallback || "Request failed";
	try {
		const data = JSON.parse(fallback);
		message = data.detail ?? data.message ?? message;
	} catch {
		// ignore json parse issues
	}
	throw new ApiError(message, response.status);
}

export async function checkToken() {
	const authToken = tokenStorage.getToken();
		if (!authToken) {
			throw new ApiError("Authorization Required.", 401);
		}

		return authToken;
}