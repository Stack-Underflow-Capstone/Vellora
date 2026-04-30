import { Text, View, TouchableOpacity, Platform } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';
import DateTimePicker, { DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { DateTimePickerAndroid } from '@react-native-community/datetimepicker';

// component and data imports
import ScreenLayout from './components/ScreenLayout';
import TripDetailsForm from './components/TripDetailsForm';
import Button from './components/Button';
import EditableNumericDisplay from './components/EditableNumericDisplay';
import { useRateOptions } from './hooks/useRateOptions';
import { useTripData } from './contexts/TripDataContext';
import { useCommonPlaces } from './hooks/useCommonPlaces';
import { useVehicles } from './hooks/useVehicles';

//  import service
import { createExpensePayload, createManualTrip, createManualTripPayload, editTrip, TripStatus } from './services/Trips';
import { createTripExpense, Expense } from './services/Trips';

const ManualLogScreen = () => {

    // use trip data context
    const { tripData, updateTripData, resetTripData } = useTripData();

    // use rate options hook for dynamic rates
    const { rateItems, categoryItems, loading, error, updateSelectedRate, rates } = useRateOptions();

    // fetch vehicles
    const { vehicleItems: dynamicVehicleItems, vehicles } = useVehicles();

    // use common places hook to get all the common places
    const { places: commonPlaces } = useCommonPlaces();

    // state variables
    const [startDate, setStartDate] = useState(tripData.startDate ? new Date(tripData.startDate) : new Date());
    const [endDate, setEndDate] = useState(tripData.endDate ? new Date(tripData.endDate) : new Date());
    // const [showStartPicker, setShowStartPicker] = useState(false);
    // const [showEndPicker, setShowEndPicker] = useState(false);

    const [showStartIOS, setShowStartIOS] = useState(false);
    const [showEndIOS, setShowEndIOS] = useState(false);

    const [startAddress, setStartAddress] = useState(tripData.startAddress || '');
    const [endAddress, setEndAddress] = useState(tripData.endAddress || '');
    const [notes, setNotes] = useState(tripData.notes ||'');
    const [vehicle, setVehicle] = useState<string | null>(tripData.vehicle || null);
    const [type, setType] = useState<string | null>(tripData.type ||null);
    const [rate, setRate] = useState<string | null>(tripData.rate || null);
    const [parking, setParking] = useState<string>(tripData.parking || '');
    const [gas, setGas] = useState<string>(tripData.gas || '');
    const [tolls, setTolls] = useState(tripData.tolls || '0.00');

    // sticky footer state variables
    const [tripValue, setTripValue] = useState('0.00');
    const [tripDistance, setTripDistance] = useState('0');
    
    const router = useRouter();

    useEffect(() => {
        if (rate && rates.length > 0) {
          updateSelectedRate(rate);
        }
      }, [rate, rates]);
    
    
    // handle vehicle selection
    useEffect(() => {
        if (tripData.vehicle && vehicles.length > 0) {
          setVehicle(tripData.vehicle);
        }
    }, [tripData.vehicle, vehicles]);


    // handle rate selection to update categories
    const handleRateChange = (selectedRateId: string | null) => {

        // reset if it actually changes
        if (rate !== selectedRateId) {
            setRate(selectedRateId);
            setType(null); // reset category when rate changes
            updateSelectedRate(selectedRateId);
        }
    };

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

                }
            }
        }
    }, [rate, type, tripDistance, rateItems, categoryItems]);

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

    // add trip to history event handler. TO BE ADJUSTED
    const handleAddTrip = async () => {
        console.log("Adding trip to history...");

        try {
            // validate
            if (!rate || !type || !tripDistance || parseFloat(tripDistance) <= 0) {
                alert("please fill in all required fields including distance");
                return;
            }

            // create the expenses array for storage and filter by amounts that aren't empty (0)
            const expensesInput: Expense[] = [
                { type: 'parking', amount: parseFloat(parking) || 0 },
                { type: 'gas', amount: parseFloat(gas) || 0 },
                { type: 'tolls', amount: parseFloat(tolls) || 0 }
            ].filter(e => e.amount > 0)

            // update the context data BEFORE making an API call to ensure the context is up to date
            updateTripData({
                notes,
                vehicle,
                type,
                rate,
                parking: parking.toString(),
                gas: gas.toString(),
                tolls: tolls.toString(),
                startAddress,
                endAddress,
                distance: tripDistance,
                value: tripValue
            })
         
            // typed shape  createManualTrip expects
            const manualTripPayload: createManualTripPayload = {
                start_address: startAddress?.trim() || "Unknown start location",
                end_address: endAddress?.trim() || "Unknown end location",
                started_at: startDate.toISOString(),
                ended_at: endDate.toISOString(),
                miles: Number(parseFloat(tripDistance)),
                geometry: null,
                rate_customization_id: rate, // these should be UUID strings
                rate_category_id: type,
                expenses: expensesInput,               
                purpose: notes?.trim() || null,
                parking: parseFloat(parking) || 0,
                gas: parseFloat(gas) || 0,
                tolls: parseFloat(tolls) || 0,
                vehicle: vehicle || null,
            };

            console.log("Creating manual trip with frontend payload:", manualTripPayload);

            // call the service which will map the backend format
            const newTrip = await createManualTrip(manualTripPayload);
            console.log("Manual trip created successfully:", newTrip);

            // update trip status
            if (tripData.linkedScheduledTripId) {
                try {
                    console.log("Attempting to update scheduled trip status for ID: ", tripData.linkedScheduledTripId);
                    await editTrip(tripData.linkedScheduledTripId, { status: TripStatus.completed });
                    console.log("Successfully updated linked scheduled trip status to completed");
                } catch (e) {
                    console.error("Failed to update linked scheduled trip status: ", e);
                }
            } else {
                console.log("No linked scheduled trip to update");
            }
            // navigate away
            setTimeout(() => {
                router.push("/(tabs)/history");
            }, 300);

        } catch (error: any) {
            console.error("Error creating manual trip: ", error);
            alert("Failed to create manual trip: " + (error?.message ?? String(error)));
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
                        className='py-4 px-5'
                    />
                </>
            }
        >
            <Text className='text-3xl text-primaryPurple font-bold p-6'>Manually Log Trip</Text>


            <View style={{ paddingHorizontal: 25, gap: 16 }}>

                <Text className='text-sm text-gray-500 mb-1'>Start Time</Text>
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

                <Text className='text-sm text-gray-500 mb-1'>End Time</Text>
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
                    parking={parking} setParking={setParking}
                    gas={gas} setGas={setGas}
                    tolls={tolls} setTolls={setTolls}
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

export default ManualLogScreen
