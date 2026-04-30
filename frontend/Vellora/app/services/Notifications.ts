import { API_BASE_URL } from "../constants/api";
import { ApiError, handleResponse, checkToken } from "./helpers";
import { fetch } from 'expo/fetch';
import * as Notifications from 'expo-notifications';

export type Notification = {
    user_id?: string;
    type: string;
    title: string;
    message: string;
    trip_id?: string;
}


export async function registerDevice(deviceToken: Notifications.ExpoPushToken, token?: string): Promise<Notifications.ExpoPushToken> {
    const authToken = await checkToken() || token;
    
    const response = await fetch(`${API_BASE_URL}/notifications/device-token`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(deviceToken),
    });
    
    return handleResponse<Notifications.ExpoPushToken>(response);
}

export async function notifyStartedMoving(token?: string): Promise<Notification> {
    const authToken = await checkToken() || token;

    const response = await fetch(`${API_BASE_URL}/notifications/events/user-started-moving`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return handleResponse<Notification>(response);
}

export async function notifyStoppedMoving(token?: string): Promise<Notification> {
    const authToken = await checkToken() || token;
    
    const response = await fetch(`${API_BASE_URL}/notifications/events/user-stopped-moving`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`
        }
    });

    return handleResponse<Notification>(response);
}