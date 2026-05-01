import { useState, useEffect } from "react";
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import Mapbox from '@rnmapbox/maps';
import { fetch } from 'expo/fetch';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { notifyStartedMoving, notifyStoppedMoving, Notification } from "../services/Notifications";

// Constants
const LOCATION_TASK_NAME = 'background_location_tracking';
let coordinates = '';                                  
const PROFILE = 'mapbox/driving';                              // profile for mapbox api
const MIN_DATA = 5;                                         // Minimum data for stationary check
const STATIONARY_CHECK_INTERVAL = 10000;                    // Check for stationary every 3 seconds
const STATIONARY_THRESHOLD = 3                              // Check for not moving / not driving 3 times minimum
const SPEED_THRESHOLD = 1;                                  // Threshold for Stationary speed
let stationaryCount = 0;
let lastCheckTime = 0;
let recentLocations: Location.LocationObject[] = [];
const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;

// flag to track if we should auto-stop because of inactivity (shared between task and hook)
let shouldAutoStop = false;

// define the trip data return type for type safety
interface TripData {
    distance: number;           // trip distance in meters
    geometry: object | null;    // geojson geometry of the route
}

Mapbox.setAccessToken(`${MAPBOX_KEY}`);

TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
        if (error) {
            console.log('Background Location tasks Error: ', error.message)
            return;
        }

        try {
            if (data) {
                const { locations } = data as { locations: Location.LocationObject[] }; 
                recentLocations = [...recentLocations, ...locations];           // add locations to recent locations
                console.log(locations);

                if (coordinates.length <= 500) { // API Limitation
                    // parse location to add to coordinates
                    let lat = locations[0].coords.latitude.toString();
                    let long = locations[0].coords.longitude.toString();
                    coordinates += long + ',' + lat + ';'; // Making the semi colon separated list for the API Call
                    console.log('Coordinate String: ', coordinates);

                }

            // Periodic Checking for Stationary Activity
              const now = Date.now();
            
              if (now - lastCheckTime >= STATIONARY_CHECK_INTERVAL) {
                lastCheckTime = now;        

                if (isStationary(recentLocations)) {
                    stationaryCount++; 
                    console.log(`Stationary count: ${stationaryCount}`);

                    if (stationaryCount >= STATIONARY_THRESHOLD) {
                        shouldAutoStop = true; // set flag to trigger stop in the hook
                        console.log("Location tracking stopped. User appears to be stationary.");
                    }
                }
              } else {
                stationaryCount = 0;            // reset count if movement detected
                console.log("User seems to still be moving.");
                shouldAutoStop = false;         // reset auto-stop flag
              }
            }

        } catch (err) {
            console.error('Error with location update:', err);
        }               
    });

function isStationary(locations: Location.LocationObject[]) {
    if (locations.length < MIN_DATA) { // Not enough data
        return false; 
    } 

    let recentPoints = locations.slice(-MIN_DATA);          // Get the 5 latest point
    let totalSpeed = 0;
 
    for (let i = 0; i < recentPoints.length; i++) {
        totalSpeed += (recentPoints[i]?.coords?.speed ?? 0);    // Add speed, if null add 0
    }
     
    const avgSpeed = totalSpeed / recentPoints.length;          
    // Consider stationary if average speed is below walking pace
    return avgSpeed < SPEED_THRESHOLD;
}

async function notifyEvent(notification: Notification) {
        await Notifications.scheduleNotificationAsync({
            content: {
                title: notification.title,
                body: notification.message,
            },
            trigger: null,
        });
    }

// Move permission and tracking start/stop functions to top-level to avoid nested functions
async function getPermissions(setErrorMessage: (msg: string | null) => void): Promise<boolean> {
    try {
        const { status: foregroundPermissions } = await Location.requestForegroundPermissionsAsync(); // have to request Foreground before BG
        if (!foregroundPermissions) {
            setErrorMessage('Permission to access location was denied. Please enable location.');
            return false;
        }

        let { status: backgroundPermssions } = await Location.requestBackgroundPermissionsAsync(); // Request Background Location for Tracking
        if (backgroundPermssions !== "granted" ) {
            setErrorMessage('Permission to access background location was denied, Please enable background location for best performance.');
            return false;
        }
        return true;

    } catch (error) {
        console.error('Error getting permissions: ', error)
        return false;
    }
}


async function getTripDistance(coordinates: string | null): Promise<TripData> {     // returns an object containing distance and geometry
    
    // return empty data if no coordinates provided
    if (coordinates === null) {
        return { distance: 0, geometry: null }; 
    }
    
    try {
        let response = await fetch(`https://api.mapbox.com/matching/v5/${PROFILE}/${coordinates}?geometries=geojson&access_token=${MAPBOX_KEY}`, 
            { method: 'GET' });
        
        // check if response was successful
        if (!response.ok) {
            throw new Error(`HTTP error. Status: ${response.status}`);
        }

        // parse the JSON response from mapbox
        let tripData = await response.json();

        // extract distance and geometry from the first matching route
        let distance = tripData.matchings?.[0]?.distance || 0;
        let geometry = tripData.matchings?.[0]?.geometry || null;

        return { distance, geometry };
 
    } catch(error) {
            console.error('Error getting trip distance: ', error);
            return { distance: 0, geometry: null};
    }

}

export const useLocationTracking = () => {
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [isTracking, setIsTracking] = useState(false);
    const [totalTripDistance, setTotalTripDistance] = useState(0);
    const [tripGeoJSON, setTripGeoJSON] = useState<object | null>(null);

    const startTracking = async(): Promise<boolean> => {
        try {
            console.log('Starting tracking...');
            const hasPermissions = await getPermissions(setErrorMessage);
            if (!hasPermissions) return false;

            await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
                accuracy: Location.Accuracy.Balanced,
                timeInterval: 10,
                distanceInterval:  1000, // 1 km
                // For android to allow background location services
                foregroundService: {
                    notificationTitle: 'Location Tracking is Active',
                    notificationBody: 'Your Location is being tracked in the background.',
                },
            });

            setIsTracking(true);
            return true;
        
        } catch (error) {
            console.error('Error to start tracking: ', error);
            setIsTracking(false);
            return false;
        }
    };

    const stopTracking = async (): Promise<TripData> => {
        try {
            console.log('Stopping tracking...');
            // If location updates were never started, skip stopping to avoid errors
            const started = await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
            if (!started) {
                console.log('stopTracking: location updates not started, nothing to stop.');
                if (setIsTracking) setIsTracking(false);
                return { distance: 0, geometry: null};
            }

            await Location.stopLocationUpdatesAsync(LOCATION_TASK_NAME);
            console.log("Tracking stopped.");
            if (setIsTracking) setIsTracking(false);
            // remove trailing semicolon before using coordinates if needed
            if (coordinates.endsWith(';')) coordinates = coordinates.slice(0, -1);

            const coordinatePairs = coordinates.split(';');
            if (coordinatePairs.length < 2) {
                console.warn('Not enough coordinates to get trip distance. Need at least 2.');
                
                // Reset variables
                coordinates = '';
                stationaryCount = 0;
                recentLocations = [];
                shouldAutoStop = false;

                return { distance: 0, geometry: null }; // Return empty data
            }
            
            // process collected coordinates if provided
            if (coordinates) {

                // get final trip data 
                const tripData = await getTripDistance(coordinates);

                // update states with trip results
                setTotalTripDistance(tripData?.distance);
                setTripGeoJSON(tripData?.geometry);

                console.log('Total Trip Distance:', tripData?.distance);
                console.log('geometry: ', tripData?.geometry);

                // CALL API TO STORE HERE

                // reset variables
                coordinates = '';
                stationaryCount = 0;
                recentLocations = [];
                shouldAutoStop = false;

                return tripData;
            }

            return { distance: 0, geometry: null };     // return empty data if no coordinates collected

        } catch (error) {
            console.error('Error to stop tracking: ', error);
            if (setIsTracking) setIsTracking(false);
            return { distance: 0, geometry: null };
        }
    };

    // effect that monitors shouldAutoStop flag and automatically stops tracking when user is stationary
    useEffect(() => {
        if (!isTracking) return;

        const checkAutoStop = async () => {
            if (shouldAutoStop && isTracking) {
                console.log('Auto-stop triggered: user is stationary');
                let notifcation = await notifyStoppedMoving();

                notifyEvent(notifcation);
                stopTracking();
            }
        };

        // check for auto-stop FLAG every 10 seconds 
        const interval = setInterval(checkAutoStop, 10000);

        return () => clearInterval(interval);
    }, [isTracking]);

    
    // unmount cleanup
    useEffect(() => {
        return () => {
            if (isTracking) {
                stopTracking();
            }
        };
    }, []);

    return {
        isTracking,         // current tracking status
        errorMessage,       // any error messages
        totalTripDistance,  // distance
        tripGeoJSON,        // geometry of the route
        startTracking,      // function to start tracking
        stopTracking,       // function to stop tracking
    };
};