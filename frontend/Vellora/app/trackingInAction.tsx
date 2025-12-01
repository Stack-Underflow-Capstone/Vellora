import { Image, Text, View } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'expo-router';
import ScreenLayout from './components/ScreenLayout';
import NoteInput from './components/NoteInput';
import CurrencyInput from './components/CurrencyInput';
import Button from './components/Button';
import { useLocationTracking } from './hooks/useLocationTracking';
import { useTripData } from './contexts/TripDataContext';

const TrackingInAction = () => {
    // use trip data context
    const { tripData, updateTripData } = useTripData();

    // state variables
    const [notes, setNotes] = useState(tripData.notes);
    const [parking, setParking] = useState<string>(tripData.parking);
    const [gas, setGas] = useState<string>(tripData.gas);
    const [isStopping, setIsStopping] = useState(false);
    const [displayDistance, setDisplayDistance] = useState(0);

    // navigation router
    const router = useRouter();

    // receive values from tracking logic
    const { stopTracking, totalTripDistance } = useLocationTracking();

    // update context when form data changes
    useEffect(() => {
        updateTripData({
            notes,
            parking,
            gas
        });
    }, [notes, parking, gas]);

    // convert meters to miles. updates whenever totaltripDistance changes
    useEffect(() => {
        const miles = (totalTripDistance / 1609.34).toFixed(2);
        setDisplayDistance(parseFloat(miles));

        updateTripData({ distance: miles });
    }, [totalTripDistance]);


    // end trip event handler
    const handleEndTrip = async () => {

        console.log('ENDING');

        // set loading step to prevent multiple stops
        setIsStopping(true);
        
        // stop the location tracking and get final trip data
        const tripData = await stopTracking();

        // check if distance collected is valid
        if (tripData.distance > 0) {
            const miles = (tripData.distance / 1609.34).toFixed(2);

            // navigate to finished screen and pass down the parameters
            router.push({
                pathname: '/trackingFinished',
                params: {
                    distance: miles,
                    distance_meters: tripData.distance.toString(),
                    geometry: JSON.stringify(tripData.geometry)
                }
            });
        } else{
            // no valid trip data collected. Default to zero
            router.push({
                pathname: '/trackingFinished',
                params: {
                    distance: '0',
                    distance_meters: '0',
                    geometry: null
                }
            });
        }
        setIsStopping(false);

    };
    
    return (
        <ScreenLayout       // screen layout as the main wrapper
            footer={
                <Button 
                    title='End Trip'
                    onPress={handleEndTrip}     // end the trip when footer button is pressed
                    className='py-4 px-5'                // for additional styling
                />
            }
        >

            <Text className="text-3xl text-primaryPurple font-bold p-6">Live tracking your trip...</Text>

            {/* Display the car gif */}
            <View style={{justifyContent: 'center', alignItems: 'center'}}>
                <Image source={require('./assets/car.gif')} style={{width: 200, height: 200}}/>
            </View>

            <Text className="text-3xl text-black font-bold p-6 text-center w-full">Have a safe trip!</Text>

            <View style={{padding: 25, gap: 16}}>

                {/* Container for displaying unadjustable live trip values and distance */}
                <View className='flex-row justify-between'>
                    <Text className='text-xl'>
                        Value: {' '}

                        {/* Cost value. TO BE CHANGED TO REAL TIME COLLECTED AMOUNT */}
                        <Text className='font-bold'>$0</Text>
                    </Text>
                    <Text className='text-xl'>
                        Distance: {' '}

                        {/* Distance value. TO BE CHANGED TO REAL TIME COLLECTED AMOUNT */}
                        <Text className='font-bold'>{displayDistance} mi</Text>
                    </Text>
                </View>

                {/* render notes input */}
                <NoteInput 
                    placeholder="Add your crazy notes"
                    value={notes}
                    onChangeText={setNotes}
                    className=''
                />

                {/* Render input boxes for currency types */}
                <View className='flex-row gap-4'>
                    <CurrencyInput 
                        label='Parking'
                        value={parking}
                        onChangeText={setParking}
                        className="flex-1"
                    />

                    <CurrencyInput 
                        label='Gas'
                        value={gas}
                        onChangeText={setGas}
                        className="flex-1"
                    />
                </View>


            </View>    

        </ScreenLayout>

    );
}

export default TrackingInAction
