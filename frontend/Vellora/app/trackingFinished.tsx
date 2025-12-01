import { View, Text } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter, useLocalSearchParams } from 'expo-router';

// Import reusable components
import ScreenLayout from './components/ScreenLayout';
import TripDetailsForm from './components/TripDetailsForm';
import EditableNumericDisplay from './components/EditableNumericDisplay';
import Button from './components/Button';
import { vehicleItems  } from '../app/constants/dropdownOptions';
import GeometryMap from './components/GeometryMap';
import { useTripData } from './contexts/TripDataContext';
import { useRateOptions } from './hooks/useRateOptions';
import { endTrip, TripStatus } from './services/Trips';
import { useCommonPlaces } from './hooks/useCommonPlaces';

const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;

const TrackingFinished = () => {
    // use trip data context
    const { tripData, updateTripData, resetTripData} = useTripData();

    // use rate options hook for dynamic rates
    const { rateItems, categoryItems, loading, error, updateSelectedRate } = useRateOptions();

    const { places: commonPlaces } = useCommonPlaces();

    // state variables
    const [notes, setNotes] = useState(tripData.notes);
    const [vehicle, setVehicle] = useState<string | null>(tripData.vehicle);
    const [type, setType] = useState<string | null>(tripData.type);
    const [rate, setRate] = useState<string | null>(tripData.rate);
    const [parking, setParking] = useState(tripData.parking || '0.00');
    const [tolls, setTolls] = useState(tripData.tolls || '0.00');
    const [gas, setGas] = useState(tripData.gas || '0.00');
    const [tripValue, setTripValue] = useState(tripData.value || '0.00');
    const [tripDistance, setTripDistance] = useState(tripData.distance || '0');
    const [startAddress, setStartAddress] = useState<string>(tripData.startAddress || 'Loading address...');
    const [endAddress, setEndAddress] = useState<string>(tripData.endAddress || 'Loading address...');
    const [tripGeometry, setTripGeometry] = useState<object | null>(null);
    const [isLoadingAddresses, setIsLoadingAddresses] = useState(false);
    const [expenseValue, setExpenseValue] = useState(tripData.gas + tripData.tolls + tripData.parking || '0.00');

    // get trip data from navigation params
    const params = useLocalSearchParams();
    const routeDistance = params.distance as string;
    const routeDistanceMeters = params.distance_meters as string;
    const routeGeometry = params.geometry as string;
    const tripId = params.id as string;

    // initialize router hook for navigation
    const router = useRouter();

    // handle rate selection to update categories
    const handleRateChange = (selectedRateId: string | null) => {
        setRate(selectedRateId);

        if (selectedRateId !== rate) {
            setType(null);
        }
        updateSelectedRate(selectedRateId);
    };

    const handleTypeChange = (newType: string | null) => {
        setType(newType);
        updateTripData({ ...tripData, type: newType });
    };
    // update context when any data changes
    useEffect(() => {
        updateTripData({
        notes,
        vehicle,
        type,
        rate,
        parking,
        gas,
        tolls,
        startAddress,
        endAddress,
        distance: tripDistance,
        value: tripValue
        });
    }, [notes, vehicle, type, rate, parking, gas, tolls, startAddress, endAddress, tripDistance, tripValue]);

    // update selected rate when component mounts or when rate from context changes
    useEffect(() => {
        if (tripData.rate) {
            updateSelectedRate(tripData.rate);
            setRate(tripData.rate); 
        }
    }, []);

    // calculate trip value when rate or distance changes
    useEffect(() => {
        if (rate && tripDistance) {
            // extract the actual numeric value from rateItems
            const selectedRateItem = rateItems.find(item => item.value === rate);
            if (selectedRateItem && selectedRateItem.originalRate) {
    
                // find the selected category's cost per mile
                const selectedCategory = categoryItems.find(item => item.value === type);
    
                if (selectedCategory && selectedCategory.originalCategory) {
    
                    const rateValue = selectedCategory.originalCategory.cost_per_mile;
                    let distanceValue = parseFloat(tripDistance);
                    const calculatedValue = (rateValue * distanceValue).toFixed(2);
                    setTripValue(calculatedValue);

                    console.log('Rate:', rate);
                    console.log('Type:', type);
                    console.log('Trip Distance:', tripDistance);
                    console.log('Calculated Value:', calculatedValue);
    
                }
            }
        }
        
    }, [rate, type, tripDistance, rateItems, categoryItems]);

    // convert coordinates to address using mapbox
    const findGeocode = async (longitude: number, latitude: number): Promise<string> => {
        try {

            // call mapbox geocoding api
            const response = await fetch(
                `https://api.mapbox.com/geocoding/v5/mapbox.places/${longitude},${latitude}.json?access_token=${MAPBOX_KEY}`
            );

            // handle errors from api
            if (!response.ok) {
                throw new Error(`Geocoding failed: ${response.status}`);
            }

            // parse response
            const data = await response.json();

            // extract address
            if (data.features && data.features.length > 0) {
                return data.features[0].place_name;             // return address
            } else {
                return 'Address not found';
            }
        } catch (error) {
            console.error('Error geocoding: ', error);
            return 'Unable to get address';
        }
    };

    // extract start and end coordinates from the geometry and convert them to addresses
    const getAddressFromGeometry = async (geometry: any) => {

        // check geometry validity
        if (!geometry || !geometry.coordinates || !Array.isArray(geometry.coordinates)) {
            console.log('No valid geometry found');
            return;
        }

        setIsLoadingAddresses(true);

        try {
            const coordinates = geometry.coordinates;

            // process coordinates if available
            if (coordinates.length > 0) {

                // get start address from first coordinate in the route
                const startPoint = coordinates[0];
                const startAddress = await findGeocode(startPoint[0], startPoint[1]);
                setStartAddress(startAddress);

                // get end address from last coordinate in the route
                const endPoint = coordinates[coordinates.length - 1];
                const endAddress = await findGeocode(endPoint[0], endPoint[1]);
                setEndAddress(endAddress);

                // debugging
                console.log('Start address: ', startAddress);
                console.log('End address: ', endAddress);
            }
        } catch (error) {
            console.error('Error updating addresses: ', error);
            setStartAddress('Error loading address');
            setEndAddress('Error loading address');
        } finally {
            setIsLoadingAddresses(false);
        }
    };

    // parse route geometry qhen component mounts or geometry changes
    useEffect(() => {
        if (routeGeometry) {
            try {
                const parsedGeometry = JSON.parse(routeGeometry);
                setTripGeometry(parsedGeometry);
                console.log('Parsed trip geometry: ', parsedGeometry);

                // start address lookup
                getAddressFromGeometry(parsedGeometry);
            } catch (error) {
                console.error('Error parsing geometry: ', error);
            }
        }
    }, [routeGeometry]);

    // set distance from route parameters
    useEffect(() => {
        if (routeDistance) {
            setTripDistance(routeDistance);
        }
    }, [routeDistance]);
    
    // calculate trip value when rate or distance changes
    useEffect(() => {
        if (rate && tripDistance) {
            let rateValue = parseFloat(rate.replace('$', ''));
            let distanceValue = parseFloat(tripDistance);
            const calculatedValue = (rateValue * distanceValue).toFixed(2);
            setTripValue(calculatedValue);
        }
    }, [rate, tripDistance]);

    // calculate total expense reimursement rate if expenses change
    useEffect(() => {
        if (gas || tolls || parking) {
            let totalGas = parseFloat(gas);
            let totalTolls = parseFloat(tolls);
            let totalParking = parseFloat(parking);
            let totalExpenses = totalGas + totalTolls + totalParking;
            setExpenseValue(totalExpenses.toString());
        }
    }, [gas, tolls, parking]);

    // end end trip event handler
    const handleSaveTrip = async () => {
        console.log('Saving trip...');

        
        const finalTripData = {
            notes: notes,
            vehicle: vehicle,

            rate_customization_id: rate || undefined,
            rate_category_id: type || undefined,

            parking: parking,
            gas: gas,
            tolls: tolls,

            miles: parseFloat(tripDistance),
            distance_meters: parseFloat(routeDistanceMeters),

            mileage_reimbursement_total: parseFloat(tripValue),
            expense_reimbursement_total: parseFloat(expenseValue),

            start_address: startAddress,
            end_address: endAddress,

            geometry: tripGeometry,                            
            end_at: new Date().toISOString(),
            status: TripStatus.completed
        };

        console.log('Final trip data to save: ', finalTripData);

        // Store the Trip

        if (!tripData.tripId) {
            alert("Unable to save trip: missing trip id.");
            return;
        }

        try {
            const response = await endTrip(tripData.tripId, finalTripData);

            if (!response) {
                alert("Failed to save trip. Please try again.");
                return;
            }
        } catch (error) {
            console.error('Error saving trip: ', error);
            alert("Failed to save trip. Please try again.");
            return;
        }

        resetTripData();
        router.push('/(tabs)/history');
    };

    return (
        <ScreenLayout       // screen layout as the main wrapper

            // return calculated value and distance with an option for user to edit them
            footer={
                <>
                    <View className='flex-row justify-between mb-4'>
                        <EditableNumericDisplay
                            label='Value'
                            value={tripValue}
                            onChangeText={setTripValue}
                            unit='$'
                        />
                        <EditableNumericDisplay
                            label='Distance'
                            value={tripDistance}
                            onChangeText={setTripDistance}
                            unit='mi'
                        />
                    </View>
                    <Button
                        title='Save trip'
                        onPress={handleSaveTrip}
                        style={{top: 10}}
                        className='py-4 px-5'
                    />
                </>
            }
        >
            {/* GEOMETRY PATH */}
            <View style={{ height: 300, width: '100%', borderRadius: 16, overflow: 'hidden' }}>
                <GeometryMap geometry={tripGeometry}/> 

            </View>
            <Text className='text-3xl text-primaryPurple font-bold pt-6 pl-6'>You arrived!</Text>
            <Text className='text-xl text-black p-6'>Make sure to update trip details:</Text>

            <TripDetailsForm 

                // mapbox token
                mapboxAccessToken={MAPBOX_KEY || ""}

                // state variables
                notes={notes} setNotes={setNotes}
                vehicle={vehicle} setVehicle={setVehicle}
                type={type} setType={handleTypeChange}
                rate={rate} setRate={handleRateChange}
                parking={parking} setParking={setParking}
                gas={gas} setGas={setGas}
                tolls={tolls} setTolls={setTolls}
                startAddress={startAddress} setStartAddress={setStartAddress}
                endAddress={endAddress} setEndAddress={setEndAddress}

                // mock data arrays
                vehicleItems={vehicleItems}
                typeItems={categoryItems}
                rateItems={rateItems}

                // common places
                commonPlaces={commonPlaces.map(p => ({
                    id: p.id,
                    title: p.name,
                    address: p.address
                }))}
                
            />

        </ScreenLayout>

    );
}

export default TrackingFinished;

