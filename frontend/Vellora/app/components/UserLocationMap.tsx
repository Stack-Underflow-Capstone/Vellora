import { StyleSheet, Text, View, ActivityIndicator } from 'react-native'
import React, { useState, useEffect } from 'react'
import Mapbox from '@rnmapbox/maps'
import * as Location from 'expo-location'

// load the public mapbox key
const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;
Mapbox.setAccessToken(`${MAPBOX_KEY}`);

const UserLocationMap = () => {
    const [hasLocationPermission, setHasLocationPermission] = useState(false);                      // tracks if the user has granted location permission
    const [initialCoordinate, setInitialCoordinate] = useState<[number, number] | null>(null);      // stores longitude and latitude


    // run once the component mounts
    useEffect(() => {

        (async () => {

            // request location permission
            let { status } = await Location.requestForegroundPermissionsAsync();
            if (status !== 'granted') {
                console.log('Permission to access location was denied');
                return;
            }
            setHasLocationPermission(true);

            // get user's current location
            let location = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Highest,
            });
            setInitialCoordinate([location.coords.longitude, location.coords.latitude]);
        })();
    }, []);

    // if no permission granted yet or no coordinates found, show a loading screen
    if (!initialCoordinate || !hasLocationPermission){
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#4DBF69" />
                <Text style={{ marginTop: 10 }}>Finding your location...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Mapbox.MapView 
                style={styles.map}
                // logoEnabled={false}
                attributionEnabled={false}      // hide mapbox attribution for clean look
                styleURL={Mapbox.StyleURL.Street}       // set visual style designed for streets
                rotateEnabled={false}                   // do not allow map rotation
            >

                {/* control the view point of the map */}
                <Mapbox.Camera 
                    zoomLevel={16}                              // zoom in
                    centerCoordinate={initialCoordinate}        // center the coordinate
                    animationMode={'none'}                      // instant snap to location
                    // animationDuration={2000}
                    // followUserLocation={true}
                    // followUserMode={Mapbox.UserTrackingMode.Follow}
                
                />

                {/* displays the blue dot for user's current location */}
                <Mapbox.UserLocation
                    visible={true}
                    // Changed this due to incompability with Expo 55
                    animated={false}
                    showsUserHeadingIndicator={true}        // show an arrow for the direction the device is facing
                />
            </Mapbox.MapView>

        </View>
    );
};

const styles = StyleSheet.create({
    container:{
        flex: 1,
        overflow: 'hidden',         // respect border radius
        borderRadius: 16,           // rounded corners
    },
    map: {
        flex: 1,                    // fill the container
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
        borderRadius: 16,
    }


});
export default UserLocationMap
