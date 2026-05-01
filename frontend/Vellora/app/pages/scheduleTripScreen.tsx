import { Text, View, TouchableOpacity, Platform, Alert } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { DateTimePickerAndroid } from '@react-native-community/datetimepicker';

// component and data imports
import ScreenLayout from '../components/ScreenLayout';
import TripDetailsForm from '../components/TripDetailsForm';
import Button from '../components/Button';
import { useRateOptions } from '../hooks/useRateOptions';
import { useTripData } from '../contexts/TripDataContext';
import { useCommonPlaces } from '../hooks/useCommonPlaces';
import { useVehicles } from '../hooks/useVehicles';
//  import service
import { scheduleTrip, scheduleTripPayload } from '../services/Trips';

const ScheduleTripScreen = () => {
    const router = useRouter();

    // use trip data context
    const { tripData, updateTripData, resetTripData } = useTripData();

    // use rate options hook for dynamic rates
    const { rateItems, categoryItems, loading, error, updateSelectedRate } = useRateOptions();

    // use common places hook to get all the common places
    const { places: commonPlaces } = useCommonPlaces();

    // import vehicles
    const { vehicleItems: dynamicVehicleItems } = useVehicles();
    // state variables
    // end date is one hour after start date by default
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date(new Date().getTime() + 60 * 60 * 1000));

    const [showStartIOS, setShowStartIOS] = useState(false);
    const [showEndIOS, setShowEndIOS] = useState(false);

    const [startAddress, setStartAddress] = useState('');
    const [endAddress, setEndAddress] = useState('');
    const [notes, setNotes] = useState('');
    const [vehicle, setVehicle] = useState<string | null>(null);
    const [type, setType] = useState<string | null>(null);
    const [rate, setRate] = useState<string | null>(null);



    // handle rate selection to update categories
    const handleRateChange = (selectedRateId: string | null) => {
        setRate(selectedRateId);
        setType(null); // reset category when rate changes
        updateSelectedRate(selectedRateId);
    };


    // OPEN ANDROID PICKER
    const openAndroidDateTimePicker = (
        currentDate: Date,
        onChange: (event: DateTimePickerEvent, date?: Date) => void
        ) => {
        DateTimePickerAndroid.open({
            value: currentDate,
            onChange: (event, date) => {
            if (date) {
                // first pick date
                DateTimePickerAndroid.open({
                value: date,
                mode: 'time',
                onChange, // final combined result
                });
            }
            },
            mode: 'date',
        });
    };

    // HANDLER TO OPEN START PICKER
    const handleStartPress = () => {
        if (Platform.OS === 'ios') {
            setShowStartIOS(!showStartIOS);
        } else {
            openAndroidDateTimePicker(startDate, (event, selectedDate) => {
                if (event.type === "set" && selectedDate) {
                    setStartDate(selectedDate);
                }
            });
        }
    };

    // HANDLER TO OPEN END PICKER
    const handleEndPress = () => {
        if (Platform.OS === 'ios') {
            setShowEndIOS(!showEndIOS);
        } else {
             openAndroidDateTimePicker(startDate, (event, selectedDate) => {
                if (event.type === "set" && selectedDate) {
                    setEndDate(selectedDate);
                }
            });
        }
    };

    const handleSchedule = async () => {
        try {

            // validate required fields
            if (!rate || !type) {
                Alert.alert('Error', 'Please select a rate and category');
                return;
            }

            if (!endAddress.trim()) {
                Alert.alert('Error', 'Please enter an end address');
                return;
            }

            // prepare payload
            const payload: scheduleTripPayload = {
                start_address: startAddress || undefined,
                end_address: endAddress.trim(),
                scheduled_start_at: startDate.toISOString(),
                scheduled_end_at: endDate.toISOString(),
                purpose: notes.trim() || undefined,
                vehicle_id: vehicle || undefined,
                rate_customization_id: rate,
                rate_category_id: type
            };

            console.log("Scheduling trip with payload:", payload);

            // call API to schedule trip    
            await scheduleTrip(payload);

            // success
            Alert.alert('Success', 'Trip scheduled successfully', [
                { text: "OK", onPress: () => router.push('/(tabs)') }
            ]);
        } catch (error: any) {
            console.error('Failed to schedule trip:', error);
            Alert.alert('Error', error.message || 'Failed to schedule trip. Please try again.');
        }

    }
    // icons style object
    const iconProps = { size: 18 };


    return (
        <ScreenLayout       // screen layout as the main wrapper

            // return calculated value and distance with an option for user to edit them
            footer={
                <View className='pt-4'>
                    <Button
                        title='Schedule Trip'
                        onPress={handleSchedule}
                        className='w-full py-4 px-5'
                    />
                </View>
            }
        >
            <Text className='text-3xl text-primaryPurple font-bold p-6'>Schedule Trip</Text>


            <View style={{ paddingHorizontal: 25, gap: 16 }}>

                {/* date pickers */}

                <Text className='text-sm text-gray-500 mb-1'>Scheduled Start</Text>

                {/* button for picking a date and time */}
                <TouchableOpacity onPress={handleStartPress}>
                    {/* style it to look like a dropdown to match the general visuals */}
                    <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                        <View className='w-6 items-center'>
                            <FontAwesome name='calendar' {...iconProps} />
                        </View>
                        <Text style={{fontSize: 16, color: 'black', marginLeft: 10}}>
                            {startDate.toLocaleString()}
                        </Text>

                    </View>

                </TouchableOpacity>

                {/* iOS inline picker */}
                {Platform.OS === 'ios' && showStartIOS && (
                    <DateTimePicker
                        value={startDate}
                        mode='datetime'
                        display='spinner'
                        onChange={(event, date) => date && setStartDate(date)}
                    />
                )}

                <Text className='text-sm text-gray-500 mb-1'>Scheduled End</Text>
                {/* button for picking a date and time */}
                <TouchableOpacity onPress={handleEndPress}>
                    {/* style it to look like a dropdown to match the general visuals */}
                    <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                        <View className='w-6 items-center'>
                            <FontAwesome name='calendar' {...iconProps} />
                        </View>
                        <Text style={{fontSize: 16, color: 'black', marginLeft: 10}}>
                            {endDate.toLocaleString()}
                        </Text>

                    </View>

                </TouchableOpacity>

                {/* picker where you choose date and time. Hidden until showpicker is set true*/}
                {/* iOS inline picker */}
                {Platform.OS === 'ios' && showEndIOS && (
                    <DateTimePicker
                        value={endDate}
                        mode='datetime'
                        display='spinner'
                        onChange={(event, date) => date && setEndDate(date)}
                    />
                )}
            </View>
                <TripDetailsForm 

                    // state variables
                    notes={notes} setNotes={setNotes}
                    vehicle={vehicle} setVehicle={setVehicle}
                    type={type} setType={setType}
                    rate={rate} setRate={handleRateChange}
                    startAddress={startAddress} setStartAddress={setStartAddress}
                    endAddress={endAddress} setEndAddress={setEndAddress}

                   
                    // mock data arrays
                    vehicleItems={dynamicVehicleItems}
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
    )
}

export default ScheduleTripScreen
