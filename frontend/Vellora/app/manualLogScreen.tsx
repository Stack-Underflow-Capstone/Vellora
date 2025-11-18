import { Text, View, TouchableOpacity } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';

// component and data imports
import { vehicleItems  } from '../app/constants/dropdownOptions';
import ScreenLayout from './components/ScreenLayout';
import TripDetailsForm from './components/TripDetailsForm';
import Button from './components/Button';
import EditableNumericDisplay from './components/EditableNumericDisplay';
import { useRateOptions } from './hooks/useRateOptions';
import { useTrip } from './contexts/TripContext';

const ManualLogScreen = () => {

    // state variables
    // const [date, setDate] = useState(new Date());
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [showStartPicker, setShowStartPicker] = useState(false);
    const [showEndPicker, setShowEndPicker] = useState(false);
    const [startAddress, setStartAddress] = useState('');
    const [endAddress, setEndAddress] = useState('');
    const [notes, setNotes] = useState('');
    const [vehicle, setVehicle] = useState<string | null>(null);
    const [type, setType] = useState<string | null>(null);
    const [rate, setRate] = useState<string | null>(null);
    const [parking, setParking] = useState<string>('');
    const [gas, setGas] = useState<string>('');
    const [tolls, setTolls] = useState('0.00');

    // sticky footer state variables
    const [tripValue, setTripValue] = useState('0.00');
    const [tripDistance, setTripDistance] = useState('0');
    
    const router = useRouter();

    //  fetch rates and categories from database
    const { rateItems, categoryItems, loading, error, updateSelectedRate, selectedRate } = useRateOptions();
    
    // use trip context for manual trip data
    const { tripData, setTripData, updateTripField, getCreateManualTripPayload, isManualTripDataComplete } = useTrip();


    // handle rate selection
    const handleRateChange = (selectedRateId: string | null) => {
        console.log('Rate changed to: ', selectedRateId);
        setRate(selectedRateId);
        setType(null);      // reset category when rate changes
        updateSelectedRate(selectedRateId);

        if (selectedRateId) {
            updateTripField('rateCustomizationId', selectedRateId);
        }
    };

    // handle category selection
    const handleCategoryChange = (categoryId: string | null) => {
        setType(categoryId);
        if (categoryId) {
            updateTripField('rateCategoryId', categoryId);
        }
    };

    // handle vehicle selection
    const handleVehicleChange = (vehicleValue: string | null) => {
        setVehicle(vehicleValue);
        if (vehicleValue) {
            updateTripField('vechicle', vehicleValue); // Use their spelling
        }
    };

    // handle notes/purpose change
    const handleNotesChange = (text: string) => {
        setNotes(text);
        updateTripField('purpose', text);
    };

    // handle parking cost change
    const handleParkingChange = (text: string) => {
        setParking(text);
        const cost = parseFloat(text) || 0;
        updateTripField('parkingCost', cost);
    };

    // handle gas cost change
    const handleGasChange = (text: string) => {
        setGas(text);
        const cost = parseFloat(text) || 0;
        updateTripField('gasCost', cost);
    };

    // handle tolls change
    const handleTollsChange = (text: string) => {
        setTolls(text);
    };

    // handle start address change
    const handleStartAddressChange = (text: string) => {
        setStartAddress(text);
        updateTripField('startAddress', text);
    };

    // handle end address change
    const handleEndAddressChange = (text: string) => {
        setEndAddress(text);
        updateTripField('endAddress', text);
    };

    // handle distance change
    const handleDistanceChange = (text: string) => {
        setTripDistance(text);
        const miles = parseFloat(text) || 0;
        updateTripField('miles', miles);
    };

    // date picker handlers
    const onStartDateChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
        setShowStartPicker(false);
        if (selectedDate) {
            setStartDate(selectedDate);
        }
    };

    const onEndDateChange = (event: DateTimePickerEvent, selectedDate?: Date) => {
        setShowEndPicker(false);
        if (selectedDate) {
            setEndDate(selectedDate);
        }
    };


    // Prepare manual trip data when fields are filled
    useEffect(() => {
        if (startAddress && endAddress && tripDistance && vehicle && type && rate) {
            setTripData({
                startAddress: startAddress,
                endAddress: endAddress,
                purpose: notes,
                vechicle: vehicle, // Use their spelling
                rateCustomizationId: rate,
                rateCategoryId: type,
                miles: parseFloat(tripDistance) || 0,
                parkingCost: parseFloat(parking) || 0,
                gasCost: parseFloat(gas) || 0,
            });
        }
    }, [startAddress, endAddress, tripDistance, vehicle, type, rate, notes, parking, gas]);
    

    // add trip to history event handler
    const handleAddTrip = async () => {
        if (!isManualTripDataComplete()) {
            alert('Please fill in all required trip details including start/end addresses and distance');
            return;
        }

        // Add type guards to ensure these aren't null
        if (!vehicle || !type || !rate) {
            alert('Please select vehicle, rate, and category');
            return;
        }

        try {
            console.log("Adding manual trip to history...");
            
            // Finalize trip data with dates - now TypeScript knows these aren't null
            setTripData({
                startAddress: startAddress,
                endAddress: endAddress,
                purpose: notes,
                vechicle: vehicle, // vehicle is not null due to check above
                rateCustomizationId: rate, // rate is not null due to check above
                rateCategoryId: type, // type is not null due to check above
                miles: parseFloat(tripDistance) || 0,
                parkingCost: parseFloat(parking) || 0,
                gasCost: parseFloat(gas) || 0,
            });

            // Data is ready for manual trip API call
            console.log('Manual trip data ready:', {
                rawData: tripData,
                apiPayload: getCreateManualTripPayload(),
                isComplete: isManualTripDataComplete()
            });

            // call createManualTrip here
            // const manualTrip = await createManualTrip(getCreateManualTripPayload());
            
            router.push('/(tabs)/history');
        } catch (error) {
            console.error('Error creating manual trip:', error);
            alert('Failed to save trip. Please try again.');
        }
    };



    // icons style object
    const iconProps = { size: 18 };


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
                        onPress={handleAddTrip}
                        style={{top: 10}}
                        disabled={!isManualTripDataComplete()}
                    />
                </>
            }
        >
            <Text className='text-3xl text-primaryPurple font-bold p-6'>Manually Log Trip</Text>


            <View style={{ paddingHorizontal: 25, gap: 16 }}>

                <Text className='text-sm text-gray-500 mb-1'>Start Time</Text>
                {/* button for picking a date and time */}
                <TouchableOpacity onPress={() => setShowStartPicker(true)}>
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

                {/* picker where you choose date and time. Hidden until showpicker is set true*/}
                {
                    showStartPicker && (
                        <DateTimePicker
                            value={startDate}
                            mode='datetime'
                            display='default'
                            onChange={onStartDateChange}
                        />
                    )
                }

                <Text className='text-sm text-gray-500 mb-1'>End Time</Text>
                {/* button for picking a date and time */}
                <TouchableOpacity onPress={() => setShowEndPicker(true)}>
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
                {
                    showEndPicker && (
                        <DateTimePicker
                            value={endDate}
                            mode='datetime'
                            display='default'
                            onChange={onEndDateChange}
                        />
                    )
                }
            </View>
                <TripDetailsForm 

                    // state variables
                    notes={notes} setNotes={handleNotesChange}
                    vehicle={vehicle} setVehicle={handleVehicleChange}
                    type={type} setType={handleCategoryChange}
                    rate={rate} setRate={handleRateChange}
                    parking={parking} setParking={handleParkingChange}
                    gas={gas} setGas={handleGasChange}
                    tolls={tolls} setTolls={handleTollsChange}
                    startAddress={startAddress} setStartAddress={handleStartAddressChange}
                    endAddress={endAddress} setEndAddress={handleEndAddressChange}

                    // mock data arrays
                    vehicleItems={vehicleItems}
                    typeItems={categoryItems}
                    rateItems={rateItems}
                    
                />


            


        </ScreenLayout>
    )
}

export default ManualLogScreen
