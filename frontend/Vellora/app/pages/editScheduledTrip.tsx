import { Text, View, TouchableOpacity, Platform, Alert, ActivityIndicator } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter, useLocalSearchParams } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { DateTimePickerAndroid } from '@react-native-community/datetimepicker';

// component and data imports
import ScreenLayout from '../components/ScreenLayout';
import TripDetailsForm from '../components/TripDetailsForm';
import Button from '../components/Button';
import { useRateOptions } from '../hooks/useRateOptions';
import { useCommonPlaces } from '../hooks/useCommonPlaces';
import { useVehicles } from '../hooks/useVehicles';

// import service
import { getTrip, editTrip, cancelTrip } from '../services/Trips';

const EditScheduledTripScreen = () => {
    const router = useRouter();
    
    // extract ID from URL
    const { id } = useLocalSearchParams();
    const tripId = Array.isArray(id) ? id[0] : id;

    // hooks
    const { rateItems, categoryItems, updateSelectedRate, rates } = useRateOptions();
    const { places: commonPlaces } = useCommonPlaces();
    const { vehicleItems: dynamicVehicleItems, vehicles } = useVehicles();

    // state variables
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
    
    const [loading, setLoading] = useState(true);

    // fetch existing trip details on mount
    useEffect(() => {
        if (!tripId) return;

        const fetchExistingTrip = async () => {
            try {
                const trip = await getTrip(tripId);
                
                setStartAddress(trip.start_address || '');
                setEndAddress(trip.end_address || '');
                setNotes(trip.purpose || '');
                
                if (trip.scheduled_start_at) setStartDate(new Date(trip.scheduled_start_at));
                if (trip.scheduled_end_at) setEndDate(new Date(trip.scheduled_end_at));

                // Safe extraction for vehicle ID
                let extractedVehicleID = trip.vehicle_id;
                if (!extractedVehicleID && trip.vehicle) {
                  extractedVehicleID = typeof trip.vehicle === 'object' ? (trip.vehicle as any).id : trip.vehicle;
                }
                
                setVehicle(extractedVehicleID || null);
                setRate(trip.rate_customization_id || null);
                setType(trip.rate_category_id || null);

            } catch (error) {
                Alert.alert("Error", "Could not load trip details.");
                router.back();
            } finally {
                setLoading(false);
            }
        };

        fetchExistingTrip();
    }, [tripId]);

    // autofill
    useEffect(() => {
        if (rate && rates.length > 0) updateSelectedRate(rate);
    }, [rate, rates]);

    useEffect(() => {
        if (vehicle && vehicles.length > 0) setVehicle(vehicle);
    }, [vehicle, vehicles]);


    // handlers
    const handleRateChange = (selectedRateId: string | null) => {
        if (rate !== selectedRateId) {
            setRate(selectedRateId);
            setType(null); 
            updateSelectedRate(selectedRateId);
        }
    };

    const openAndroidDateTimePicker = (currentDate: Date, onChange: (event: DateTimePickerEvent, date?: Date) => void) => {
        DateTimePickerAndroid.open({
            value: currentDate,
            onChange: (event, date) => {
            if (date) {
                DateTimePickerAndroid.open({ value: date, mode: 'time', onChange });
            }
            },
            mode: 'date',
        });
    };

    const handleStartPress = () => {
        if (Platform.OS === 'ios') setShowStartIOS(!showStartIOS);
        else {
            openAndroidDateTimePicker(startDate, (event, selectedDate) => {
                if (event.type === "set" && selectedDate) setStartDate(selectedDate);
            });
        }
    };

    const handleEndPress = () => {
        if (Platform.OS === 'ios') setShowEndIOS(!showEndIOS);
        else {
             openAndroidDateTimePicker(endDate, (event, selectedDate) => {
                if (event.type === "set" && selectedDate) setEndDate(selectedDate);
            });
        }
    };

    // api call
    const handleUpdate = async () => {
        if (!tripId) return;
        try {
            if (!rate || !type) return Alert.alert('Error', 'Please select a rate and category');
            if (!endAddress.trim()) return Alert.alert('Error', 'Please enter an end address');

            const payload = {
                start_address: startAddress || undefined,
                end_address: endAddress.trim(),
                scheduled_start_at: startDate.toISOString(),
                scheduled_end_at: endDate.toISOString(),
                purpose: notes.trim() || undefined,
                vehicle_id: vehicle || undefined,
                rate_customization_id: rate,
                rate_category_id: type
            };

            await editTrip(tripId, payload);
            Alert.alert('Success', 'Trip updated successfully', [{ text: "OK", onPress: () => router.push('/(tabs)') }]);
        } catch (error: any) {
            Alert.alert('Error', error.message || 'Failed to update trip.');
        }
    }

    // delete api call
    const handleDelete = () => {
        Alert.alert("Cancel Trip", "Are you sure you want to cancel this scheduled trip?", [
            { text: "No", style: "cancel" },
            { 
                text: "Yes, Cancel it", 
                style: "destructive", 
                onPress: async () => {
                    if (!tripId) return;
                    try {
                        await cancelTrip(tripId);
                        router.push('/(tabs)');
                    } catch (error) {
                        Alert.alert("Error", "Failed to cancel trip");
                    }
                } 
            }
        ]);
    };

    if (loading) {
        return <ActivityIndicator size="large" color="#3F46D6" style={{ flex: 1, justifyContent: 'center' }} />;
    }

    const iconProps = { size: 18 };

    return (
        <ScreenLayout 
            footer={
                <View className='pt-4'>
                    <Button title='Save Changes' onPress={handleUpdate} className='w-full py-4 px-5' />
                </View>
            }
        >
            {/* Header with Title and Trash Icon */}
            <View className="flex-row justify-between items-center p-6 pb-2">
                <Text className='text-3xl text-primaryPurple font-bold'>Edit Trip</Text>
                <TouchableOpacity onPress={handleDelete} className="p-2">
                    <FontAwesome name="trash" size={24} color="#EF4444" />
                </TouchableOpacity>
            </View>

            <View style={{ paddingHorizontal: 25, gap: 16 }}>
                <Text className='text-sm text-gray-500 mb-1'>Scheduled Start</Text>
                <TouchableOpacity onPress={handleStartPress}>
                    <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                        <View className='w-6 items-center'>
                            <FontAwesome name='calendar' {...iconProps} />
                        </View>
                        <Text style={{fontSize: 16, color: 'black', marginLeft: 10}}>
                            {startDate.toLocaleString()}
                        </Text>
                    </View>
                </TouchableOpacity>
                {Platform.OS === 'ios' && showStartIOS && (
                    <DateTimePicker value={startDate} mode='datetime' display='spinner' onChange={(e, date) => date && setStartDate(date)} />
                )}

                <Text className='text-sm text-gray-500 mb-1'>Scheduled End</Text>
                <TouchableOpacity onPress={handleEndPress}>
                    <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                        <View className='w-6 items-center'>
                            <FontAwesome name='calendar' {...iconProps} />
                        </View>
                        <Text style={{fontSize: 16, color: 'black', marginLeft: 10}}>
                            {endDate.toLocaleString()}
                        </Text>
                    </View>
                </TouchableOpacity>
                {Platform.OS === 'ios' && showEndIOS && (
                    <DateTimePicker value={endDate} mode='datetime' display='spinner' onChange={(e, date) => date && setEndDate(date)} />
                )}
            </View>
            
            <TripDetailsForm 
                notes={notes} setNotes={setNotes}
                vehicle={vehicle} setVehicle={setVehicle}
                type={type} setType={setType}
                rate={rate} setRate={handleRateChange}
                startAddress={startAddress} setStartAddress={setStartAddress}
                endAddress={endAddress} setEndAddress={setEndAddress}
                
                vehicleItems={dynamicVehicleItems}
                typeItems={categoryItems}
                rateItems={rateItems}
                commonPlaces={commonPlaces.map(p => ({ id: p.id, title: p.name, address: p.address }))}
            />
        </ScreenLayout>
    )
}

export default EditScheduledTripScreen;