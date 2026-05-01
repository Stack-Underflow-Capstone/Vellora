import { API_BASE_URL } from "../constants/api";
import { tokenStorage } from "./tokenStorage";
import { ApiError, handleResponse } from "./helpers";

export type Vehicle = {
    id: string;
    name: string;
    license_plate: string;
    model: string;
    year?: number;
    color?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
};

export type CreateVehiclePayload = {
    name: string;
    license_plate: string;
    model: string;
    year?: number;
    color?: string;
};

export type EditVehiclePayload = Partial<CreateVehiclePayload> & {
    is_active?: boolean;
};

type VehicleListResponse = {
    vehicles: Vehicle[];
    total: number;
};

// api functions
export async function getVehicles(token?: string): Promise<Vehicle[]> {
    const authToken = token || tokenStorage.getToken();
    if (!authToken) {
        throw new ApiError("Authentication token is missing");
    }

    const response = await fetch(`${API_BASE_URL}/vehicles/`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
    });

    const data = await handleResponse<any>(response);

    console.log("Backend GET Vehicles Response:", data); // Debug log\

    if (Array.isArray(data)) {
        // Handle case where backend returns a plain array
        return data;
    }
    return data?.vehicles || [];
}

export async function getVehicle(id: string, token?: string): Promise<Vehicle> {
    const authToken = token || tokenStorage.getToken();
    if (!authToken) {
        throw new ApiError("Authentication token is missing");
    }
    const response = await fetch(`${API_BASE_URL}/vehicles/${id}/`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
    });

    return handleResponse<Vehicle>(response);
}
export async function createVehicle(payload: CreateVehiclePayload, token?: string): Promise<Vehicle> {
    const authToken = token || tokenStorage.getToken();
    if (!authToken) {
        throw new ApiError("Authentication token is missing");
    }

    const response = await fetch(`${API_BASE_URL}/vehicles/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<Vehicle>(response);
}

export async function updateVehicle(id: string, payload: EditVehiclePayload, token?: string): Promise<Vehicle> {
    const authToken = token || tokenStorage.getToken();
    if (!authToken) {
        throw new ApiError("Authentication token is missing");
    }

    const response = await fetch(`${API_BASE_URL}/vehicles/${id}/`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<Vehicle>(response);
}

export async function deleteVehicle(id: string, token?: string): Promise<void> {
    const authToken = token || tokenStorage.getToken();
    if (!authToken) {
        throw new ApiError("Authentication token is missing");
    }

    const response = await fetch(`${API_BASE_URL}/vehicles/${id}/`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
    });

    if (response.status !== 204) return;
    if (!response.ok) await handleResponse(response);
}