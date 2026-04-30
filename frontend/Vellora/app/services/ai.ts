import { AI_ROUTES } from "../constants/api";
import { ApiError, handleResponse, checkToken } from "./helpers";

// Types matching the backend schemas
export type TripAssistantRequestDTO = {
	message: string;
	trip_id?: string | null;
	current_location?: RoutePointDTO | null;
	destination_location?: RoutePointDTO | null;
	metadata?: { [key: string]: any };
};

export type RoutePointDTO = {
	lat: number;
	lon: number;
};

export type TripAssistantResponseDTO = {
	assistant_message: string;
	suggested_category?: string | null;
	missing_details?: string[];
	weather_summary?: string | null;
	ai_enabled: boolean;
};

export async function askTripAssistant(
	message: string,
	tripId?: string | null,
	currentLocation?: RoutePointDTO | null,
	destinationLocation?: RoutePointDTO | null,
	metadata?: { [key: string]: any }
): Promise<TripAssistantResponseDTO> {
	const authToken = await checkToken();

	const payload: TripAssistantRequestDTO = {
		message,
		trip_id: tripId || null,
		current_location: currentLocation || null,
		destination_location: destinationLocation || null,
		metadata: metadata || {},
	};

	const response = await fetch(AI_ROUTES.tripAssistant, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Authorization: `Bearer ${authToken}`,
		},
		body: JSON.stringify(payload),
	});

	return handleResponse<TripAssistantResponseDTO>(response);
}