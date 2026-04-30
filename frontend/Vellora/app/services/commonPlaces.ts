import { API_BASE_URL } from "../constants/api";
import { handleResponse, checkToken } from "./helpers";

// define the shape for common place
export type CommonPlace = {
    id: string;
    user_id: string;
    name: string;
    address: string;
    created_at: string;
    updated_at: string;
};

export type CommonPlacePayload = {
    name: string;
    address: string;
    // latitude: number;
    // longitude: number;
};

// api functions
export async function getCommonPlaces(): Promise<CommonPlace[]> {
    const token = await checkToken();

    const response = await fetch(`${API_BASE_URL}/common-places/`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
        },
    });
    return handleResponse<CommonPlace[]>(response);
}

export async function createCommonPlace(payload: CommonPlacePayload): Promise<CommonPlace> {
    const token = await checkToken();
    const response = await fetch(`${API_BASE_URL}/common-places/`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<CommonPlace>(response);
}

export async function updateCommonPlace(id: string, payload: CommonPlacePayload): Promise<CommonPlace> {
    const token = await checkToken();
    const response = await fetch(`${API_BASE_URL}/common-places/${id}`, {
        method: 'PATCH',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
    });
    return handleResponse<CommonPlace>(response);
}

export async function deleteCommonPlace(id: string): Promise<void> {
    const token = await checkToken();
    const response = await fetch(`${API_BASE_URL}/common-places/${id}`, {
        method: 'DELETE',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error(`Failed to delete common place with id ${id}`);
    }
}