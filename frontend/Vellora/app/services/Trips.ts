import { API_BASE_URL } from "../constants/api";
import { ApiError, handleResponse, checkToken } from "./helpers";
import { fetch } from 'expo/fetch';


export type Expense = {
    id: string;
    type: string;
    amount: number;
    createdAt: Date;
}

export enum TripStatus {
    active,
    completed,
    cancelled
}

export type Trip = {
    id: string;
    status: TripStatus;
    start_address: string;
    end_address?: string;
    purpose?: string;
    reimbursement_rate?: number | null;
    miles?: number | null;
    geometry?: object | null;
    mileage_reimbursement_total?: number | null;
    expense_reimbursement_total?: number | null;
    start_at: Date;
    ended_at?: Date | undefined;
    updated_at: Date;
    rate_customization_id: string;
    rate_category_id: string;
    expenses?: Expense[] | null;
}

 // Types for payloads for Backend API calls
export type createTripPayload = {
    start_address: string;
    purpose?: string | null;
    vechicle?: string | null;
    rate_customization_id: string;
    rate_category_id: string;
}


export type createManualTripPayload = {
    start_address: string;
    end_address: string;
    started_at: string; // ISO datetime string
    ended_at: string; // ISO datetime string
    miles: number;
    geometry?: string | null;   // backend expects a string or null
    rate_customization_id: string;
    rate_category_id: string;
    expenses?: Expense[];
    purpose?: string | null;
    vehicle?: string | null;
    parking?: number | null;
    gas?: number | null;
    tolls?: number | null;
}


export type createExpensePayload = {
    type: string;
    amount: number;
}


export async function getTrips(token?: string): Promise<Trip[]> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
    });

    const Trips = await handleResponse<Trip[]>(response);

    return Trips;
}

export async function getTrip(id: string, token?: string): Promise<Trip> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${id}`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return handleResponse<Trip>(response);
}

export async function createTrip(payload: createTripPayload, token?: string): Promise<Trip> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload), 
    });

    return handleResponse<Trip>(response);
}

export async function createManualTrip(payload: createManualTripPayload, token?: string): Promise<Trip> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/manual`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<Trip>(response);
}

export async function getActiveTrip(token?: string): Promise<Trip | null> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/active`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
    });

    try {
        return await handleResponse<Trip>(response);
    } catch (error) {
        // if no active trip is found, return null
        if (error instanceof ApiError && error.status === 404) {
            return null;
        }
        throw error;
    }
}

export async function endTrip(tripId: string, payload: Partial<Trip>, token?: string): Promise<Trip> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/end`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload)
    });

    return handleResponse<Trip>(response);
}

export async function editTrip(trip_id: string, payload: Partial<Trip>, token?: string): Promise<Trip> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${trip_id}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<Trip>(response);
}

export async function cancelTrip(trip_id: string, token?: string): Promise<Trip> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${trip_id}/cancel`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify({
            trip_id: trip_id
        })
    });

    return handleResponse<Trip>(response);
}


export async function createTripExpense(tripId: string, payload: createExpensePayload, token?: string): Promise<Expense> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/expenses/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload)
    })

    return handleResponse<Expense>(response);
}

export async function getTripExpenses(tripId: string, token?: string): Promise<Expense[]> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/expenses`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return handleResponse<Expense[]>(response);
}


export async function updateTripExpense(expenseId: string, tripId: string, payload: Partial<Expense>, token?: string): Promise<Expense> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/expenses/${expenseId}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload)
    });

    return handleResponse<Expense>(response);
}

export async function deleteTripExpense(expenseId: string, tripId: string, token?: string): Promise<Expense> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/expenses/${expenseId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        }
    })

    return handleResponse<Expense>(response);
}