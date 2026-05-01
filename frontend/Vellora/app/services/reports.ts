import { Linking, Platform } from "react-native";
import { API_BASE_URL } from "../constants/api";
import { tokenStorage } from "./tokenStorage";

export type ReportStatus =
	| "pending"
	| "processing"
	| "completed"
	| "failed"
	| "expired";

export type Report = {
	id: string;
	user_id: string;
	start_date: string;
	end_date: string;
	status: ReportStatus;
	file_name: string | null;
	file_url: string | null;
	requested_at: string;
	completed_at: string | null;
	expires_at: string | null;
};

export type ReportStatusResponse = {
	id: string;
	status: ReportStatus;
	file_url: string | null;
};

export type DownloadResponse = {
	download_url: string;
};

export type RegenerateResponse = {
	status: "available" | "regenerating";
	download_url?: string;
};

export type AnalyticsResponse = {
	category_counts: Record<string, number>;
	total_miles: number;
	grand_total: number;
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
		try {
			const text = await response.text();
			if (!text || text.trim() === "") {
				return [] as unknown as T;
			}
			return JSON.parse(text) as T;
		} catch (e) {
			console.error("Failed to parse JSON response:", e);
			throw new ApiError("Invalid response format", response.status);
		}
	}

	let message = "Request failed";
	let responseText = "";

	try {
		responseText = await response.text();
		message = responseText || `HTTP ${response.status} Error`;

		if (responseText) {
			try {
				const data = JSON.parse(responseText);
				message = data.detail ?? data.message ?? data.error ?? message;
			} catch {
				message = responseText;
			}
		}
	} catch (e) {
		console.error("Failed to read error response:", e);
		message = `HTTP ${response.status} Error`;
	}

	console.error(`API Error [${response.status}]:`, message);
	if (responseText) {
		console.error("Response text:", responseText);
	}

	throw new ApiError(message, response.status);
}

export async function generateReport(
	startDate: string,
	endDate: string,
	token?: string,
): Promise<Report> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const requestBody = {
		start_date: startDate,
		end_date: endDate,
	};

	const response = await fetch(`${API_BASE_URL}/reports`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
		body: JSON.stringify(requestBody),
	});

	return handleResponse<Report>(response);
}

export async function getReportAnalytics(
	month: string,
	token?: string,
): Promise<AnalyticsResponse> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/reports/analytics/${encodeURIComponent(month)}`,
		{
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
		},
	);

	return handleResponse<AnalyticsResponse>(response);
}

export async function getReportStatus(
	reportId: string,
	token?: string,
): Promise<ReportStatusResponse> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/reports/${reportId}/status`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
	});

	return handleResponse<ReportStatusResponse>(response);
}

export async function downloadReport(
	reportId: string,
	token?: string,
): Promise<DownloadResponse> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/reports/${reportId}/download`, {
		method: "GET",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
	});

	if (response.status === 410) {
		const errorData = await response.json().catch(() => ({}));
		throw new ApiError(
			errorData.detail || "Report expired. Please regenerate it.",
			410,
		);
	}

	return handleResponse<DownloadResponse>(response);
}

export async function getReportsHistory(token?: string): Promise<Report[]> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	try {
		const response = await fetch(`${API_BASE_URL}/reports/history`, {
			method: "GET",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
		});

		if (response.status === 500) {
			console.warn("Backend returned 500 for history - returning empty array");
			return [];
		}

		return handleResponse<Report[]>(response);
	} catch (err) {
		if ((err as ApiError).status === 500) {
			console.warn("Internal server error for history - returning empty array");
			return [];
		}
		throw err;
	}
}

export async function retryReport(
	reportId: string,
	token?: string,
): Promise<Report> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(`${API_BASE_URL}/reports/${reportId}/retry`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
	});

	return handleResponse<Report>(response);
}

export async function regenerateReport(
	reportId: string,
	token?: string,
): Promise<RegenerateResponse> {
	const authToken = token || tokenStorage.getToken();
	if (!authToken) {
		throw new ApiError("Authentication required", 401);
	}

	const response = await fetch(
		`${API_BASE_URL}/reports/${reportId}/regenerate`,
		{
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${authToken}`,
			},
		},
	);

	return handleResponse<RegenerateResponse>(response);
}

export async function downloadAndOpenReport(
	downloadUrl: string,
	reportId: string,
): Promise<void> {
	try {
		let fixedUrl = downloadUrl.replace("localstack:4566", "localhost:4566");

		if (Platform.OS === "android" && process.env.EXPO_PUBLIC_LOCALSTACK_URL) {
			const localstackUrl = process.env.EXPO_PUBLIC_LOCALSTACK_URL;
			fixedUrl = fixedUrl.replace("http://localhost:4566", localstackUrl);
			fixedUrl = fixedUrl.replace("https://localhost:4566", localstackUrl);
			fixedUrl = fixedUrl.replace("localhost:4566", localstackUrl);
			console.log("Android PDF URL:", fixedUrl);
		}

		await Linking.openURL(fixedUrl);
	} catch (error) {
		console.error("Error opening report:", error);
		throw error;
	}
}
