import { Text, View, Keyboard, TouchableOpacity, TextInput, Alert, ActivityIndicator } from 'react-native'
import React, { useEffect, useState } from 'react'
import Mapbox from '@rnmapbox/maps';
import { useRouter, useLocalSearchParams } from 'expo-router';
import * as Location from 'expo-location';
import { FontAwesome } from '@expo/vector-icons';

import ScreenLayout from './components/ScreenLayout';
import AddressInput from './components/AddressInput';
import Button from './components/Button';
import { createCommonPlace, updateCommonPlace, deleteCommonPlace } from './services/commonPlaces';

const MAPBOX_TOKEN = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;
Mapbox.setAccessToken(`${MAPBOX_TOKEN}`);

const AddCommonPlaceScreen = () => {
    const router = useRouter();
    const params = useLocalSearchParams();

    // determine if we are editing the location
    const isEditing = !!params.id;


    // if editing use passed params. if not use empty strings
    const [name, setName] = useState(isEditing ? (params.title as string) : '');
    const [address, setAddress] = useState(isEditing ? (params.address as string) : '');

    // parse coordinates if they were passed as dtrings
    const [coordinates, setCoordinates] = useState<[number, number] | null>(null);

    const [isGeocoding, setIsGeocoding] = useState(false);

    // helper function for geocode address
    const geocodeAddressString = async (addressText: string) => {
        if (!addressText) return;

        setIsGeocoding(true);

        try {
            const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(addressText)}.json?access_token=${MAPBOX_TOKEN}&limit=1`;
            const response = await fetch(url);
            const data = await response.json();

            if (data.features && data.features.length > 0) {
                setCoordinates(data.features[0].center);
            }
        } catch (error) {
            console.error('Failed to geocode address: ', error);
        } finally {
            setIsGeocoding(false);
        }
    };

    // initial location logic
    // make the map show user's current location if they didn't type an address yet
    // RUNS ONLY IF NOT EDITING
    
    useEffect(() => {
        const init = async () => {
            if (isEditing) {
                // edit: if we have an address but no coordinates yet, fetch them
                if (address && !coordinates) {
                    await geocodeAddressString(address);
                }
            } else {
                
                // add mode: try to get gps, but don't crash if it fails
                try {

                    // add: get current GPS location
                    let { status } = await Location.requestForegroundPermissionsAsync();
                    if (status !== 'granted') {
                        return;
                    }

                    let lastKnown = await Location.getLastKnownPositionAsync({});
                    if (lastKnown && !coordinates) {
                        setCoordinates([lastKnown.coords.longitude, lastKnown.coords.latitude]);
                    }

                    // if we didnt get a location try the current position with a timeout
                    if (!lastKnown) {
                        try{
                            let loc = await Location.getCurrentPositionAsync({
                                accuracy: Location.Accuracy.Balanced,
                            });
                            if (!coordinates) {
                                setCoordinates([loc.coords.longitude, loc.coords.latitude]);
                            }
                        } catch (gpsError) {
                            // ignore the error. User can still type an address
                            console.log("GPS signal weak or emulator stuck. Ignoring.");

                        }
                       
                    }
                } catch (e) {
                    console.log('Location permission/service error: ', e);
                }
            }
        };
            
        init();
    }, []);

    const handleAddressSelect = (addressData: any) => {
        if (addressData && addressData.center) {
            setAddress(addressData.place_name);
            setCoordinates(addressData.center);
            Keyboard.dismiss(); 
        }
    };

    const handleSavePlace = async () => {
        
        if (!name || !address || !coordinates) {
            alert('Please provide all details');
            return;
        }

        // prepare data payload
        const placePayload = {
            // id: isEditing ? (params.id as string) : undefined,      // send id if editing
            // title: name,
            // address: address,
            // geometry: {
                //     type: 'Point',
                //     coordinates: coordinates
                // },
            name: name,
            address: address,
        };

        // console.log('Saving common place: ', placePayload);

        try {
            // logic to save the common place
            // change to backend API later
            
            if (isEditing) {
                // update existing place logic here
                await updateCommonPlace(params.id as string, placePayload);
                console.log('Updating place with id ', params.id, ' to: ', placePayload);
            } else {
                // create new place logic here
                await createCommonPlace(placePayload);
                console.log('Creating new place: ', placePayload);
            }
            router.back();
        } catch (error: any) {
            alert(`Error: ${error.message}`);
            console.error('Error saving common place: ', error);
        }
    };


    const handleDeletePlace = async () => { 
        Alert.alert(
            "Delete Place",
            "Are you sure you want to delete this place?",
            [
                { text: "Cancel", style: "cancel" },
                { text: "Delete", style: "destructive", onPress: async () => {
                        // deletion logic here
                        try {
                            await deleteCommonPlace(params.id as string);
                            router.back();
                        } catch (error) {
                            alert('Error deleting place');
                        }
                        
                    } 
                }
            ]
        );
    };

    return (
        <ScreenLayout
            footer={
                <Button 
                    title={isEditing ? 'Save Changes' : 'Save Place'}
                    onPress={handleSavePlace}
                    className='py-4 px-5'
                />
            }
        >
            <View className='px-6 pt-4 flex-row items-center justify-between'>

                <TouchableOpacity
                    onPress={() => router.back()}
                    className='bg-gray-100 p-2 rounded-full'
                >
                    <FontAwesome name="close" size={20} color="#404CCF" />

                </TouchableOpacity>

                {/* show the delete button only in edit mode */}
                {
                    isEditing ? (
                        <TouchableOpacity onPress={handleDeletePlace} className='p-2'>
                            <FontAwesome name='trash' size={20} color="#ED4444"/>
                        </TouchableOpacity>
                    ) : (
                        <View style={{width: 40}}></View>   // placeholder to keep the title centered
                    )
                }
            </View>

            <Text className='text-2xl font-bold text-primaryPurple text-center mt-2 mb-8'>
                {isEditing ? 'Edit Common Place' : 'Add Common Place'}
            </Text>

            {/* form fields */}
            <View className='px-6 gap-6'>

                {/* location name input */}
                <View>
                    <Text className="text-primaryPurple font-bold text-base mb-2">Name</Text>
                    <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                        <TextInput 
                            style={{ flex: 1, fontSize: 16, marginLeft: 10, color: 'black' }}
                            placeholder='Name this place (e.g. Office)'
                            value={name}
                            onChangeText={setName}
                        />
                    </View>
                </View>

                {/* address input */}
                <View>
                    <Text className="text-primaryPurple font-bold mb-2 text-base">Address</Text>
                    <AddressInput 
                        placeholder="Enter the address"
                        value={address}
                        onChangeText={setAddress}
                        onAddressSelect={handleAddressSelect}
                        mapboxAccessToken={MAPBOX_TOKEN || ''}
                        icon={<FontAwesome name="search" size={16} color="#6B7280" />}
                    />
                </View>
            </View>

            {/* map preview */}
            <View className='mt-6 w-full h-80 overflow-hidden'>

                {/* show loading if we are fetching the coordinates for the address */}
                {isGeocoding? (
                    <ActivityIndicator size="large" color="#404CCF"/>
                ) : (
                    <Mapbox.MapView
                        style={{ flex: 1, width: '100%' }}
                        styleURL={Mapbox.StyleURL.Street}
                        logoEnabled={false}
                        attributionEnabled={true}
                    >

                        <Mapbox.Camera
                            zoomLevel={14}
                            centerCoordinate={coordinates || [0, 0]}
                            animationMode='flyTo'
                            animationDuration={1000}
                        />

                        {/* show a pin at the coordinates */}
                        {coordinates && (
                            <Mapbox.PointAnnotation
                                id="selectedLocation"
                                coordinate={coordinates}
                            >
                                <View className='bg-primaryPurple p-2 rounded-full border-2 border-white shadow-sm'>
                                    <FontAwesome name="map-marker" size={20} color="white" />
                                </View>
                            </Mapbox.PointAnnotation>
                        )}
                    </Mapbox.MapView>

                )}
            </View>
        </ScreenLayout>

    )
}

export default AddCommonPlaceScreen
