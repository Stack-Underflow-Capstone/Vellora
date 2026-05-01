import { API_BASE_URL } from "../constants/api";
import { ApiError, handleResponse, checkToken } from "./helpers";


export type Expense = {
    id?: string;
    type: string;
    amount: number;
}

export enum TripStatus {
    active = "active",
    scheduled = "scheduled",
    completed = "completed",
    cancelled = "cancelled"
}

export type Trip = {
    id: string;
    status: TripStatus;
    start_address: string;
    end_address?: string | null;
    purpose?: string | null;
    reimbursement_rate?: number | null;
    miles?: number | null;
    geometry?: object | null;
    mileage_reimbursement_total?: number | null;
    expense_reimbursement_total?: number | null;
    started_at: Date;
    ended_at?: Date | undefined;
    updated_at: Date;
    rate_customization_id: string;
    rate_category_id: string;
    expenses?: Expense[] | null;
    vehicle?: string | null;
    vehicle_id?: string | null;

    scheduled_start_at?: string | null;
    scheduled_end_at?: string | null;
}

export type scheduleTripPayload = {
    start_address?: string;
    end_address?: string;
    scheduled_start_at: string; // ISO  datetime string
    scheduled_end_at?: string; // ISO datetime string
    purpose?: string | null;
    vehicle_id?: string | null;
    rate_customization_id: string;
    rate_category_id: string;
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

export type expenseReceipt = {
    id?: string,
    trip_id: string,
    user_id?: string, 
    bucket?: string,
    object_key?: string,
    file_name: string,
    content_type?: string,
    size_bytes?: string,
    created_at?: Date
}

export type filteredTripData = {
    month: number,
    total_drives: number,
    total_expense_reimbursement: number,
    total_mileage_reimbursement: number,
    total_miles: number,
    total_reimbursement: number,
    trips: Trip[],
    year: number
}

export type MonthlyStats = {
    month: number;
    year: number;
    total_drives: number;
    total_miles: number;
    total_reimbursement: number;
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

export async function getTripByMonthYear(month: number, year: number): Promise <Trip[]> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/monthly-stats/${month}/${year}`, {
        method: 'GET',
        headers: {
            'Content-Type': "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return await handleResponse<Trip[]>(response);
}

export async function getTripsByMonthYear(month: number, year: number): Promise <filteredTripData> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/monthly-details/${month}/${year}`, {
        method: 'GET',
        headers: {
            'Content-Type': "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return await handleResponse<filteredTripData>(response);
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

    const response = await globalThis.fetch(`${API_BASE_URL}/trips/active`, {
        method: 'GET',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
    });

    // silence "no active trip found" error since this is expected if user doesn't have an active trip
    if (response.status === 404) {
        return null;
    }

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

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/expenses/`, {
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

export async function addReceipt(tripId: string, receipt: FormData, token?: string): Promise<expenseReceipt[]> {
  
    const authToken = token || await checkToken();
  
    const response = await globalThis.fetch(`${API_BASE_URL}/trips/${tripId}/receipts`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${authToken}`
        },
        body: receipt
    });

    if (!response.ok) {
        const errortxt = await response.text();
        console.error('Upload failed:', {
            status: response.status,
            statusText: response.statusText,
            body: errortxt
        });
        throw new Error(`Upload failed: ${response.status} ${errortxt}`);
    }

    return handleResponse<expenseReceipt[]>(response);    
}

export async function getReceipts(tripId: string, token?: string): Promise<expenseReceipt[]> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/receipts`, {
        method: "GET",
        headers: {
            "Content-Type": ``,
            Authorization: `Bearer ${authToken}`
        }
    });

    return handleResponse<expenseReceipt[]>(response);
}

export async function scheduleTrip(payload: scheduleTripPayload, token?: string): Promise<Trip> {
    const authToken = token || await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/scheduled`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(payload),
    });

    return handleResponse<Trip>(response);
}

export async function getMonthlyStats(month: number, year: number): Promise<MonthlyStats> {
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips/monthly-stats/${month}/${year}`, {
        method: 'GET',
        headers: {
            'Content-Type': "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return await handleResponse<MonthlyStats>(response);
}