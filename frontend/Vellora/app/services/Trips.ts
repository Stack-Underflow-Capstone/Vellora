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
    Active,
    Completed,
    Cancelled
}

export type Trip = {
    id: string;
    userId: string;
    status: TripStatus;
    startAddress: string;
    endAddress?: string;
    purpose?: string;
    reimbursementRate?: number | null;
    miles?: number | null;
    geometry?: object | null;
    mileageReimbursementTotal?: number | null;
    expenseReimbursementTotal?: number | null;
    startAt: Date;
    endAt?: Date | undefined;
    updatedAt: Date;
    rateCustomizationId: string;
    rateCategoryId: string;
    expenses?: Expense[] | null;
}

 // Types for payloads for Backend API calls
export type createTripPayload = {
    startAddress: string;
    purpose?: string | null;
    vechicle?: string | null;
    rateCustomizationId: string;
    rateCategoryId: string;
}


export type createManualTripPayload = {
    startAddress: string;
    endAddress: string;
    startedAt: Date;
    endedAt: Date;
    miles: number;
    geometry?: object | null;
    rateCustomizationId: string;
    rateCategoryId: string;
    expenses?: Expense[];
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
    const authToken = await checkToken();

    const response = await fetch(`${API_BASE_URL}/trips`, {
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