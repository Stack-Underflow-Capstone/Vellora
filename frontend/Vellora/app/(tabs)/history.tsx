import { View, Text, ScrollView, Button, SectionList } from 'react-native'
import React, { useState, useEffect, useCallback } from 'react'
import TripCard from '../components/TripCard'
import { getTrips, Trip, getTripsByMonthYear } from '../services/Trips'
import ScreenLayout from '../components/ScreenLayout'
import { SafeAreaView } from 'react-native-safe-area-context'
import  MonthYearDropdown from '../components/MonthYearDropdown'
import FilterButton from '../components/filterButton'
import { useRateOptions } from '../hooks/useRateOptions'


const History = () => {
  const [loading, setIsLoading] = useState(true);
  const [trips, setTrips] = useState<Trip[]>([]);
  const [error, setError] = useState<unknown | null>(null);
  const [date, setDate] = useState<Date>(new Date());
  const [value, setValue] = useState<number>(0.00);
  const { rateItems, categoryItems, updateSelectedRate, rates } = useRateOptions();
  // console.log(rateItems[0].originalRate.categories[0].name);


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

const handleGetTripsByMonth = async (currentDate: Date) => {
  try {
    setIsLoading(true);

    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();
    
    const response = await getTripsByMonthYear(month, year);


    if (!response) {
      alert("Failed to get trip history by Month/Year, please try again"); 
      return;
    } 

    setTrips(response.trips);
    setValue(response.total_mileage_reimbursement)
    setIsLoading(false);

  } catch (error) {
    console.error('Failed to get trip by month: ', error);
    alert("Failed to filter trip by month, please try again.");
    setError(error);
    return;
  }
}

const groupTripsByDate = (trips: Trip[]) => {

  if (!trips) {
    return [];
  }

  const grouped = trips.reduce((acc, trip) => {
    const date = new Date(trip.started_at);
    const dateKey = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'short'
    });

    if (!acc[dateKey]) {
      acc[dateKey] = [];
    }
    acc[dateKey].push(trip);
    return acc;
  }, {} as Record<string, Trip[]>);
  
  return Object.keys(grouped).map(date => ({
    title: date,
    data: grouped[date]
  }));
}

const getLabelsforFilter = (rateItems: any) => {
  
}

  useEffect(() => {
    // handleGetAllTrips();
    handleGetTripsByMonth(date); //needs to be modified to return all trip data
  }, [date]); 

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
  <SafeAreaView style={{flex: 1}}>
    <SectionList
      sections={trips ? groupTripsByDate(trips) : []}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <TripCard
          id={item.id}
          geometry={item.geometry ?? null}
          start_address={item.start_address ?? ''}
          end_address={item.end_address ?? ''}
          mileage_reimbursement_total={item.mileage_reimbursement_total ?? 0}
          distance_meters={item.miles ?? 0}
        />
      )}
      renderSectionHeader={({ section: { title } }) => (
        <View style={{backgroundColor: '#ffffffff', padding: 12, marginTop: 20}}>
          <Text style={{fontSize: 14}}>{title}</Text>
        </View>
      )}
      ListHeaderComponent={
        <View style={{justifyContent: 'center', alignItems: 'center', backgroundColor: 'white', marginBottom: 10, height: 200}}>
            <MonthYearDropdown 
            currentDate={date}
            onDateChange={setDate} 
            />
            <Text style={{textAlign: 'center', color: '#A2A2A2', fontWeight: 'bold', fontSize: 11}}>Classified value: ${value}</Text>
           
        </View>
      }
      ListEmptyComponent={
        <View style={{alignItems: 'center', justifyContent: 'center', marginTop: 20}}>
        <Text style={{textAlign: 'center', fontWeight: 'bold'}}>No Trips Found for {date.toLocaleDateString('en-US', {month: 'long', year: 'numeric'})}.</Text>
        </View>
      }
    />
  </SafeAreaView>
  )
}

export default History