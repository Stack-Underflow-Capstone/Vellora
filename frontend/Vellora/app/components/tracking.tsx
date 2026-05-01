// import React from 'react'
// import {  View, Text, Button  } from "react-native";
// import { useState, useEffect } from "react";
// import * as Location from 'expo-location';
// import * as TaskManager from 'expo-task-manager';
// import Mapbox from '@rnmapbox/maps';
// import { fetch } from 'expo/fetch';


// // Constants
// const LOCATION_TASK_NAME = 'background_location_tracking';
// let coordinates = '';                                  
// const PROFILE = 'mapbox/driving';                              // profile for mapbox api
// const MIN_DATA = 5;                                         // Minimum data for stationary check
// const STATIONARY_CHECK_INTERVAL = 10000;                    // Check for stationary every 3 seconds
// const STATIONARY_THRESHOLD = 3                              // Check for not moving / not driving 3 times minimum
// const SPEED_THRESHOLD = 1;                                  // Threshold for Stationary speed
// let stationaryCount = 0;
// let lastCheckTime = 0;
// let recentLocations: Location.LocationObject[] = [];
// const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;
// let totalTripDistance = 0;
// let tripGeoJSON: object | null = null;

// Mapbox.setAccessToken(`${MAPBOX_KEY}`);

// TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
//         if (error) {
//             console.log('Background Location tasks Error: ', error.message)
//             return;
//         }

//         try {
//             if (data) {
//                 const { locations } = data as { locations: Location.LocationObject[] }; 
//                 recentLocations = [...recentLocations, ...locations];           // add locations to recent locations
//                 console.log(locations);

//                 if (coordinates.length <= 500) { // API Limitation
//                     // parse location to add to coordinates
//                     let lat = locations[0].coords.latitude.toString();
//                     let long = locations[0].coords.longitude.toString();
//                     coordinates += long + ',' + lat + ';'; // Making the semi colon separated list for the API Call
//                     console.log('Coordinate String: ', coordinates);

//                 }

//             // Periodic Checking for Stationary Activity
//               const now = Date.now();
            
//               if (now - lastCheckTime >= STATIONARY_CHECK_INTERVAL) {
//                 lastCheckTime = now;        

//                 if (isStationary(recentLocations)) {
//                     stationaryCount++; 
//                     console.log(`Stationary count: ${stationaryCount}`);

//                     if (stationaryCount >= STATIONARY_THRESHOLD) {
//                         stopTracking();
//                         console.log("Location tracking stopped. User appears to be stationary.");
//                     }
//                 }
//               } else {
//                 stationaryCount = 0;            // reset count if movement detected
//                 // console.log("User seems to still be moving.");
//               }
//             }

//         } catch (err) {
//             console.error('Error with location update:', err);
//         }               
//     });

// function isStationary(locations: Location.LocationObject[]) {
//     if (locations.length < MIN_DATA) { // Not enough data
//         return false; 
//     } 

//     let recentPoints = locations.slice(-MIN_DATA);          // Get the 5 latest point
//     let totalSpeed = 0;
 
//     for (let i = 0; i < recentPoints.length; i++) {
//         totalSpeed += (recentPoints[i]?.coords?.speed ?? 0);    // Add speed, if null add 0
//     }
     
//     const avgSpeed = totalSpeed / recentPoints.length;          
//     // Consider stationary if average speed is below walking pace
//     return avgSpeed < SPEED_THRESHOLD;
// }

// // Move permission and tracking start/stop functions to top-level to avoid nested functions
// async function getPermissions(setErrorMessage: (msg: string | null) => void): Promise<boolean> {
//     try {
//         const { status: foregroundPermissions } = await Location.requestForegroundPermissionsAsync(); // have to request Foreground before BG
//         if (!foregroundPermissions) {
//             setErrorMessage('Permission to access location was denied. Please enable location.');
//             return false;
//         }

//         let { status: backgroundPermssions } = await Location.requestBackgroundPermissionsAsync(); // Request Background Location for Tracking
//         if (backgroundPermssions !== "granted" ) {
//             setErrorMessage('Permission to access background location was denied, Please enable background location for best performance.');
//             return false;
//         }
//         return true;

//     } catch (error) {
//         console.error('Error getting permissions: ', error)
//         return false;
//     }
// }

// async function startTracking(setIsTracking: (isTracking: boolean) => void, setErrorMessage: (errorMessage: string | null) => void) {
//     try {
//         const hasPermissions = await getPermissions(setErrorMessage);
//         if (!hasPermissions) return;

//         await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
//             accuracy: Location.Accuracy.Balanced,
//             timeInterval: 10,
//             distanceInterval:  1000, // 1 km
//             // For android to allow background location services
//             foregroundService: {
//                 notificationTitle: 'Location Tracking is Active',
//                 notificationBody: 'Your Location is being tracked in the background.',
//             },
//         });

//         setIsTracking(true);

//     } catch (error) {
//         console.error('Error to start tracking: ', error);
//         setIsTracking(false);
//         return;
//     }
// }

// async function stopTracking(setIsTracking?: (isTracking: boolean) => void) {    // optional state change param
//     try {
//         // If location updates were never started, skip stopping to avoid errors
//         const started = await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
//         if (!started) {
//             console.log('stopTracking: location updates not started, nothing to stop.');
//             if (setIsTracking) setIsTracking(false);
//             return;
//         }

//         await Location.stopLocationUpdatesAsync(LOCATION_TASK_NAME);
//         console.log("Tracking stopped.");
//         if (setIsTracking) setIsTracking(false);
//         // remove trailing semicolon before using coordinates if needed
//         if (coordinates.endsWith(';')) coordinates = coordinates.slice(0, -1);

//         await getTripDistance(coordinates);

//         console.log('Total Trip Distance:', totalTripDistance);
//         console.log('geometry: ', tripGeoJSON);
        
//         // CALL API TO STORE HERE 
        
//         // reset variables
//         coordinates = '';
//         stationaryCount = 0;
//         recentLocations = [];
//         totalTripDistance = 0;
//         tripGeoJSON = null;
//         return;

//     } catch (error) {
//         console.error('Error to stop tracking: ', error);
//         if (setIsTracking) setIsTracking(false);
//         return;
//     }
// }

// async function getTripDistance(coordinates: string | null) {
//     if (coordinates === null) {
//         return; 
//     }
    
//     try {
//         await fetch(`https://api.mapbox.com/matching/v5/${PROFILE}/${coordinates}?geometries=geojson&access_token=${MAPBOX_KEY}`, 
//             { method: 'GET' })
//         .then(response => response.json())
//         .then(tripData => {
//             totalTripDistance += tripData.matchings?.[0]?.distance;
//             tripGeoJSON = tripData.matchings?.[0].geometry;
//         })
//         .catch(error => {
//             console.error('Error fetching mapbox: ', error);
//         });
//     } catch (error) {
//         console.error('Error getting trip distance: ', error);
//     }   
// }

// function LocationTracker() {
//     const [errorMessage, setErrorMessage] = useState<string | null>(null);
//     const [isTracking, setIsTracking] = useState(false);

//     useEffect(() => {
//        // start on mount
//        startTracking(setIsTracking, setErrorMessage);

//        return () => { // useEffect Cleanup Function to stop tracking location when Component dismounts
//             stopTracking(setIsTracking); // Call stopTracking with UI state setter
//        };
//     }, []);

//     return (
//         <View>
//             <Button title="Start Tracking" onPress={() => startTracking(setIsTracking, setErrorMessage)} />
//             <Button title="Stop Tracking" onPress={() => stopTracking(setIsTracking)} />
//             {isTracking ? (
//                 <Text>Tracking is active</Text>
//             ) : (
//                 <Text>Tracking is inactive</Text>
//             )}
//         </View>
//     )
// }


// export default LocationTracker;