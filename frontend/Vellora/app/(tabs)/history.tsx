import { View, Text, ScrollView, Pressable } from 'react-native'
import React, { useState, useEffect } from 'react'
import TripCard from '../components/TripCard'
import { getTrips, Trip } from '../services/Trips'
import ScreenLayout from '../components/ScreenLayout'
import { SafeAreaView } from 'react-native-safe-area-context'


const history = () => {
  const [loading, setIsLoading] = useState(true);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [error, setError] = useState<unknown | null>(null);

  const handleGetAllTrips = async () => { 
  try {
    setIsLoading(true);
    const response = await getTrips();

    if (!response) {
      alert("Failed to get trip history. Please try again.");
      return;
    }

    setTrips(response);
    setIsLoading(false);

  } catch (error) {
    console.error('failed to get trips: ', error);
    alert("Failed to get trip history. Please try again.");
    setError(error);
    return;
  }
}

  useEffect(() => {
    handleGetAllTrips();
  }, []);

  if (loading) {
    return (
      <Text>Loading...</Text>
    )
  }

  if (error) {
    return (
      <Text>Error</Text>
    )
  }

  return (
  <View>
    <ScrollView>
      <View style={{alignItems: 'center', justifyContent: 'center', height: 200, backgroundColor: 'white', marginBottom: 10}}>
        <Text className='text-3xl text-primaryPurple font-bold p-6'>History</Text>
      </View>
      {trips.length === 0 ? (
        <Text>No Trips Found.</Text>
      ) : (
        <View style={{flex: 1, width:'100%', height: '100%' }}>
          {trips.map((trip, idx) => (
            <TripCard
              key={trip.id ?? idx}
              geometry={trip.geometry ?? null}
              start_address={trip.start_address ?? ''}
              end_address={trip.end_address ?? ''}
              mileage_reimbursement_total={trip.mileage_reimbursement_total ?? 0}
              distance_meters={trip.miles ?? 0}
            />
          ))}
        </View>
      )}
    </ScrollView>
  </View>
  )
}

export default history