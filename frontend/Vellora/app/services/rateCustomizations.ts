import { API_BASE_URL } from "../constants/api";
import { tokenStorage } from "./tokenStorage";
import { ApiError, handleResponse } from "./helpers";

export type RateCategory = {
	id: string;
	name: string;
	cost_per_mile: number;
	rate_customization_id?: string;
	created_at?: string;
};

export type RateCustomization = {
	id: string;
	name: string;
	description?: string | null;
	year: number;
	created_at?: string;
	categories?: RateCategory[];
};

export type CreateRateCustomizationPayload = {
	name: string;
	description?: string | null;
	year: number;
};

export type CreateRateCategoryPayload = {
	name: string;
	cost_per_mile: number;
};

/* class ApiError extends Error {
	status?: number;
	constructor(message: string, status?: number) {
		super(message);
		this.status = status;
	}
}

/* async function handleResponse<T>(response: Response): Promise<T> {
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
} */

export async function getRateCustomizations(
	token?: string
): Promise<RateCustomization[]> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}
	const response = await fetch(`${API_BASE_URL}/rate-customizations/`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
	});

	const customizations = await handleResponse<RateCustomization[]>(response);

	const customizationsWithCategories = await Promise.all(
		customizations.map(async (customization) => {
			try {
				const categories = await getRateCategories(customization.id, authToken);
				return { ...customization, categories };
			} catch {
				return { ...customization, categories: [] };
			}
		})
	);

	return customizationsWithCategories;
}

export async function getRateCustomization(
	id: string,
	token?: string
): Promise<RateCustomization> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/rate-customizations/${id}`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
	});

	const customization = await handleResponse<RateCustomization>(response);

	try {
		const categories = await getRateCategories(id, authToken);
		return { ...customization, categories };
	} catch (err) {
		return { ...customization, categories: [] };
	}
}

export async function createRateCustomization(
	payload: CreateRateCustomizationPayload,
	token?: string
): Promise<RateCustomization> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/rate-customizations/`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
		body: JSON.stringify(payload),
	});

	return handleResponse<RateCustomization>(response);
}

export async function updateRateCustomization(
	id: string,
	payload: Partial<CreateRateCustomizationPayload>,
	token?: string
): Promise<RateCustomization> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/rate-customizations/${id}`, {
		method: "PATCH",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
		body: JSON.stringify(payload),
	});

	return handleResponse<RateCustomization>(response);
}

export async function deleteRateCustomization(
	id: string,
	token?: string
): Promise<void> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/rate-customizations/${id}`, {
		method: "DELETE",
		headers: {
			Authorization: `Bearer ${authToken}`,
		},
	});

	if (response.status === 204) return;

	if (!response.ok) {
		await handleResponse(response);
	}
}

export async function getRateCategories(
	customizationId: string,
	token?: string
): Promise<RateCategory[]> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/rate-customizations/${customizationId}/categories/`,
		{
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
		}
	);

	return handleResponse<RateCategory[]>(response);
}

export async function createRateCategory(
	customizationId: string,
	payload: CreateRateCategoryPayload,
	token?: string
): Promise<RateCategory> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/rate-customizations/${customizationId}/categories/`,
		{
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
			body: JSON.stringify(payload),
		}
	);

	return handleResponse<RateCategory>(response);
}

export async function updateRateCategory(
	customizationId: string,
	categoryId: string,
	payload: Partial<CreateRateCategoryPayload>,
	token?: string
): Promise<RateCategory> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/rate-customizations/${customizationId}/categories/${categoryId}`,
		{
			method: "PATCH",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
			body: JSON.stringify(payload),
		}
	);

	return handleResponse<RateCategory>(response);
}

export async function deleteRateCategory(
	customizationId: string,
	categoryId: string,
	token?: string
): Promise<void> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/rate-customizations/${customizationId}/categories/${categoryId}`,
		{
			method: "DELETE",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
		}
	);

	if (!response.ok) {
		await handleResponse(response);
	}
}
