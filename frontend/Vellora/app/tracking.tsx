import { View, Text } from 'react-native'
import React, { useState, useEffect } from 'react'
import { useRouter } from 'expo-router';
import Mapbox from '@rnmapbox/maps';

// Import reusable components
import ScreenLayout from './components/ScreenLayout';
import TripDetailsForm from './components/TripDetailsForm';
import Button from './components/Button';
import { vehicleItems } from '../app/constants/dropdownOptions';
import UserLocationMap from './components/UserLocationMap';
import { useLocationTracking } from './hooks/useLocationTracking';
import { useRateOptions } from './hooks/useRateOptions';
import { useTrip } from './contexts/TripContext';

const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;
Mapbox.setAccessToken(`${MAPBOX_KEY}`);

const Tracking = () => {

  // state variables
  const [notes, setNotes] = useState('');
  const [vehicle, setVehicle] = useState<string | null>(null);
  const [type, setType] = useState<string | null>(null);
  const [rate, setRate] = useState<string | null>(null);
  const [parking, setParking] = useState<string>('');
  const [gas, setGas] = useState<string>('');
  const [isStarting, setIsStarting] = useState(false);

  // initialize router hook for navigation
  const router = useRouter();

  // receive values from tracking logic
  const { startTracking, errorMessage, isTracking } = useLocationTracking();

  // fetch rates
  const { rateItems, categoryItems, loading, error, updateSelectedRate, selectedRate } = useRateOptions();

  // use the trip context
  const { tripData, setTripData, updateTripField, getCreateTripPayload, isTripDataComplete } = useTrip();

  // handle rate selection
  const handleRateChange = (selectedRateId: string | null) => {
    console.log('Rate changed to: ', selectedRate);
    setRate(selectedRateId);
    setType(null);      // reset category when rate changes
    updateSelectedRate(selectedRateId);

    // update trip data in the context
    if (selectedRateId) {
      updateTripField('rateCustomizationId', selectedRateId);
    }
  };

  // handle category selection
  const handleCategoryChange = (categoryId: string | null) => {
    setType(categoryId);
    
    // update trip data
    if (categoryId) {
      updateTripField('rateCategoryId', categoryId);
    }
  };

  // handle vehicle selection
  const handleVehicleChange = (vehicleValue: string | null) => {
    setVehicle(vehicleValue);
    
    // update trip data
    if (vehicleValue) {
      updateTripField('vechicle', vehicleValue);
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


  useEffect(() => {
    if (isTracking && isStarting) {
      router.push('/trackingInAction');
      setIsStarting(false);
    }
  }, [isTracking, isStarting]);


  // prepare trip data when all required fields are filled
  useEffect(() => {
    if (vehicle && type && rate) {
      // const currentAddress = await getCurrentLocationAddress();
      // setStartAddress(currentAddress);
        
      setTripData({
        startAddress: '',
        purpose: notes,
        vechicle: vehicle,
        rateCustomizationId: rate,
        rateCategoryId: type,
        parkingCost: parseFloat(parking) || 0,
        gasCost: parseFloat(gas) || 0,
      });
    }

  }, [vehicle, type, rate, notes, parking, gas]);

  // start trip event handler
  const handleStartTrip = async () => {

    // require input
    if (!vehicle || !type || !rate) {
      alert('Please fill in all required trip details');
      return;
    }

    console.log('STARTING...');
    setIsStarting(true);

    // finalize trip data with current location
    // const currentAddress = await getCurrentLocationAddress();

    const currentLocation = "Current Location"; // CHANGE THIS

    setTripData({
      startAddress: currentLocation,
      purpose: notes,
      vechicle: vehicle,
      rateCustomizationId: rate,
      rateCategoryId: type,
      parkingCost: parseFloat(parking) || 0,
      gasCost: parseFloat(gas) || 0,
    });


    console.log('Trip data ready for API:', {
      rawData: tripData,
      apiPayload: getCreateTripPayload(),
      isComplete: isTripDataComplete(),
    })

    const success = await startTracking();

    // check if tracking start unsuccessfu;
    if(!success) {
      setIsStarting(false);
      alert(errorMessage || 'Failed to start tracking:(');
    }

  };

  return (
    <ScreenLayout               // screen layout as the main wrapper
      footer={
        <Button 
          title='Start Trip'
          onPress={handleStartTrip}     // start the trip when footer button is pressed
          className=''                  // for additional styling
          disabled={!isTripDataComplete()}
        />
      }

    >
      <Text className="text-3xl text-primaryPurple font-bold p-6">Live Track Current Trip</Text>

      <View style={{ height: 300, width: '100%', borderRadius: 16, overflow: 'hidden' }}>
        <UserLocationMap />
      </View>

      {/* Container for displaying trip value and distance */}
      <View className='flex-row justify-between px-6 pt-6'>
        <Text className='text-xl'>
          Value: {' '}

          {/* Cost value. Starts at 0 */}
          <Text className='font-bold'>$0</Text>
        </Text>

        <Text className='text-xl'>
          Distance: {' '}

          {/* Distance value. Starts at 0 */}
          <Text className='font-bold'>0 mi</Text>
        </Text>
      </View>

      {/* display the form for trip details */}
      <TripDetailsForm 

        // state vairables
        notes={notes} setNotes={handleNotesChange}
        vehicle={vehicle} setVehicle={handleVehicleChange}
        type={type} setType={handleCategoryChange}
        rate={rate} setRate={handleRateChange}
        parking={parking} setParking={handleParkingChange}
        gas={gas} setGas={handleGasChange}

        // mock data arrays
        vehicleItems={vehicleItems}
        typeItems={categoryItems}
        rateItems={rateItems}
      
      />
    </ScreenLayout>

  )
}

export default Tracking
