import React, { useState, useCallback } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Agenda, Calendar, DateData } from 'react-native-calendars';
import { FontAwesome } from '@expo/vector-icons';
import { useRouter, useFocusEffect } from 'expo-router';
import Button from './Button';

// import services
import { getTrips, Trip, TripStatus } from '../services/Trips';
import { useTripData } from '../contexts/TripDataContext';
import { getRateCustomizations } from '../services/rateCustomizations';
// define the shape of a single trip item
interface AgendaItem {
  id: string;
  time: string;
  purpose: string;
  address: string;
  type: string;
  status: string;

  fullTripData: Trip; // context helper
}

// // define the shape of your schedule data object
// const MOCK_SCHEDULES: Record<string, AgendaItem[]> = {
//   '2026-02-13': [
//     { id: '1', time: '09:00 AM', purpose: 'Meeting with Client X', address: '123 Tech Blvd', type: 'Business', status: 'pending' },
//     { id: '2', time: '02:00 PM', purpose: 'Site Visit', address: '456 Construction Rd', type: 'Business', status: 'pending' }
//   ],
//   '2026-02-10': [
//     { id: '3', time: '11:30 AM', purpose: 'Lunch with Mentor', address: '789 Downtown Ave', type: 'Personal', status: 'pending' }
//   ],
//   '2026-02-15': [
//     { id: '3', time: '11:30 AM', purpose: 'Office trip', address: '123 Office Ave', type: 'Personal', status: 'pending' }
//   ]
// };

const CustomCalendar = () => {
  const router = useRouter();

  // access the context
  const { updateTripData, resetTripData } = useTripData();

  const today = new Date().toISOString().split('T')[0]; // get today's date in YYYY-MM-DD format
  const [selected, setSelected] = useState(today);
  const [schedules, setSchedules] = useState<Record<string, AgendaItem[]>>({});
  const [loading, setLoading] = useState(false);

  const fetchScheduledTrips = async () => {

    try {
      setLoading(true);
      const allTrips = await getTrips();  // call the api

      let categoryMap: Record<string, string> = {};

      try {
        const customizations = await getRateCustomizations();
        customizations.forEach(cust => {
          if (cust.categories) {
            cust.categories.forEach((cat: any) => {
              categoryMap[cat.id] = cat.name; // map category id to rate customization name
            });
          }
        });
      } catch (catError) {
        console.log("Could not fetch categories for mapping", catError);
      }
      
      const scheduledTrips = allTrips.filter(t => 
        t.scheduled_start_at && t.status !== TripStatus.cancelled
      );
      const grouper: Record<string, AgendaItem[]> = {};

      scheduledTrips.forEach((trip) => {

        // date parsning
        const dateObj = new Date(trip.scheduled_start_at as string);
        const dateKey = dateObj.toISOString().split('T')[0]; // YYYY-MM-DD
        const timeString = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (!grouper[dateKey]) grouper[dateKey] = [];

        grouper[dateKey].push({
          id: trip.id,
          time: timeString,
          purpose: trip.purpose || 'No purpose',
          address: trip.start_address || 'No address',
          type: categoryMap[trip.rate_category_id] || 'Unknown',
          status: trip.status,
          fullTripData: trip
        });
      });

      setSchedules(grouper);

    } catch (error) {
      console.error('Error fetching trips:', error);
    } finally {
      setLoading(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      fetchScheduledTrips();
    }, [])
  );

  // ACTION HANDLERS
  const handleEdit = (id: string) => {
    router.push({
      pathname: '/pages/editScheduledTrip',
      params: { id }
    } as any);
    
  };

  const handleStartTracking = (trip: AgendaItem) => {
    resetTripData(); // clear any existing data in context

    // extract vehicle id string
    let extractedVehicleID = trip.fullTripData.vehicle_id;
    if (!extractedVehicleID && trip.fullTripData.vehicle) {

      // if id is missing but vehicle obj exists, grab its id
      extractedVehicleID = typeof trip.fullTripData.vehicle === 'object'
        ? (trip.fullTripData.vehicle as any).id 
        : trip.fullTripData.vehicle;
    }
    updateTripData({
      startAddress: trip.fullTripData.start_address || '',
      endAddress: trip.fullTripData.end_address || '',
      notes: trip.purpose || '',
      vehicle: extractedVehicleID || null,
      rate: trip.fullTripData.rate_customization_id || null,
      type: trip.fullTripData.rate_category_id || null,

      linkedScheduledTripId: trip.fullTripData.id // link the active trip to this scheduled trip
    });

    router.push('/tracking'); // navigate to active trip screen
  };

  const handleMarkComplete = (item: AgendaItem) => {
    resetTripData(); // clear context data

    // extract vehicle id
    let extractedVehicleID = item.fullTripData.vehicle_id;
    if (!extractedVehicleID && item.fullTripData.vehicle) {
      extractedVehicleID = typeof item.fullTripData.vehicle === 'object'
      ? (item.fullTripData.vehicle as any).id
      : item.fullTripData.vehicle;
    }

    updateTripData({
      startAddress: item.fullTripData.start_address || '',
      endAddress: item.fullTripData.end_address || '',
      notes: item.purpose || '',
      vehicle: extractedVehicleID || null,
      rate: item.fullTripData.rate_customization_id || null,
      type: item.fullTripData.rate_category_id || null,

      startDate: item.fullTripData.scheduled_start_at || undefined,
      endDate: item.fullTripData.scheduled_end_at || undefined,
      
      linkedScheduledTripId: item.fullTripData.id // link the completed trip to this scheduled trip
    });

    router.push('/manualLogScreen'); // navigate to manual log screen with pre-filled data
  };

  const getMarkedDates = () => {
    const marks: any = {};
    const CIRCLE_SIZE = 40;

    // add dots for days with scheduled trips
    Object.keys(schedules).forEach(date => {
      marks[date] = { marked: true, dotColor: '#404CCF' };
    });

    // style "today"
    marks[today] = {
      ...(marks[today] || {}),
      customStyles: {
        container: {
          backgroundColor: '#404CCF',
          borderRadius: CIRCLE_SIZE / 2,
          justifyContent: 'center',
          alignItems: 'center',
          width: CIRCLE_SIZE,
          height: CIRCLE_SIZE,
        },
        text: {
          color: 'white',
          fontWeight: 'bold'
        }
      }   
    };

    // style the selected day
    if (selected) {
      marks[selected] = {
        ...(marks[selected] || {}),
        customStyles: {
          container: {
            backgroundColor: 'white',
            borderColor: '#404CCF',
            borderWidth: 2,
            borderRadius: CIRCLE_SIZE / 2,
            justifyContent: 'center',
            alignItems: 'center',
            width: CIRCLE_SIZE,
            height: CIRCLE_SIZE,
          },
          text: {
            color: '#404CCF',
            fontWeight: 'bold'
          }
        }
      };
    }

    return marks;
  };

  const renderAgendaItem = (item: AgendaItem ) => {

    const isScheduled = item.status === TripStatus.scheduled;

    // check if the trip is older than 5 hours
    let showStartButton = true;
    if (item.fullTripData.scheduled_start_at) {
      const startTime = new Date(item.fullTripData.scheduled_start_at).getTime();
      const now = new Date().getTime();
      
      // hours difference
      const hoursDifference = (now - startTime) / (1000 * 60 * 60);

      // if it's in the future, hoursdifference is negative
      // if it is in the past, it will only show if it's been 5 hours or less
      showStartButton = hoursDifference <= 5;
    }


    return (
      <View key={item.id} style={styles.card}>

        {/* trip info section */}
        <View style={styles.cardTopRow}>
          <View style={styles.cardTimeContainer}>
            <Text style={styles.cardTime}>{item.time}</Text>
            <View style={styles.verticalLine} />
          </View>
          <View style={styles.cardContent}>
            <Text style={styles.cardPurpose}>{item.purpose}</Text>
            <Text style={styles.cardAddress}>{item.address}</Text>

            <View style={{ flexDirection: 'row', gap: 8 }}>
              <View style={styles.badgeContainer}>
                <Text style={styles.badgeText}>{item.type}</Text>
              </View>


              {!isScheduled && (
                <View style={[
                  styles.badgeContainer, 
                  { backgroundColor: item.status === TripStatus.completed ? '#D1FAE5' : '#FEF3C7' }
                ]}>
                  <Text style={[
                    styles.badgeText, 
                    { color: item.status === TripStatus.completed ? '#059669' : '#D97706' }
                  ]}>
                    {item.status.toUpperCase()}
                  </Text>
                </View>
              )}
      
            </View>
          </View>
        </View>

        {/* action buttons. Show only if schedueld*/}

        {isScheduled ? (
          <View style={styles.actionRow}>

            {/* edit */}
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => handleEdit(item.id)}
            >
              <FontAwesome name="pencil" size={14} color="#666" />
              <Text style={styles.actionText}>Edit</Text>

            </TouchableOpacity>

            {/* start tracking */}
            {showStartButton && (
              <TouchableOpacity
              style={[styles.actionButton, styles.primaryAction]}
              onPress={() => handleStartTracking(item)}
            >
              <FontAwesome name="play" size={14} color="#666" />
              <Text style={[styles.actionText, styles.primaryActionText]}>Start</Text>
            </TouchableOpacity>
            )}

            {/* mark complete */}
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => handleMarkComplete(item)}
            >
              <FontAwesome name="check-circle" size={14} color="#666" />
              <Text style={styles.actionText}>Complete</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View style={[styles.actionRow, { justifyContent: 'center', paddingVertical: 8 }]}>
            <Text style={{ color: '#9CA3AF', fontStyle: 'italic', fontSize: 12}}>
              This trip has already been {item.status}.
            </Text>
          </View>
        )}
      </View>
    );
  };

  const dailyTrips = schedules[selected] || [];

  return (
    <View style={styles.container}>
      
      <Calendar
        markingType={'custom'}      // enable custom styling
        onDayPress={(day: DateData) => {
          setSelected(day.dateString);
        }}

        // dynamic marks
        markedDates={getMarkedDates()}

        theme={{
          todayTextColor: '#404CCF',
          arrowColor: '#404CCF',
        }}
      />

      <View style={styles.agendaContainer}>
        <Text style={styles.headerTitle}>
          {selected ? `Schedule for ${selected}` : 'Select a date to view trips'}
        </Text>

        {loading ? (
          <ActivityIndicator size="large" color="#404CCF" />
        ) : (
          <View>
            {dailyTrips.length > 0 ? (
              dailyTrips.map((item : AgendaItem) => renderAgendaItem(item))
            ) : (
              selected && <Text style={styles.emptyText}>No trips scheduled for this day.</Text>
            )}
            <Button
                title="Schedule a Trip"
                onPress={() => {router.push('./pages/scheduleTripScreen')}}
                className="w-full py-4 px-5" 
              />
          </View> 
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    // flex: 1,
    backgroundColor: '#F5F5F5',
  },
  agendaContainer: {
    // flex: 1,
    padding: 16,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  emptyText: {
    color: '#999',
    fontStyle: 'italic',
    marginTop: 10,
    marginBottom: 20
  },
  card: {
    // flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 12,
    marginBottom: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTopRow:{
    flexDirection: 'row',
    marginBottom: 12,
  },
  cardTimeContainer: {
    alignItems: 'center',
    marginRight: 16,
    width: 60,
  },
  cardTime: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  verticalLine: {
    flex: 1,
    width: 2,
    backgroundColor: '#F0F0F0',
    marginTop: 4,
  },
  cardContent: {
    flex: 1,
    justifyContent: 'center',
  },
  cardPurpose: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  cardAddress: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  badgeContainer: {
    backgroundColor: '#EEEFFF',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  badgeText: {
    color: '#404CCF',
    fontSize: 12,
    fontWeight: '600',
  },

  actionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
    paddingTop: 12,
  },

  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 8,
    backgroundColor: '#F9FAFB',
  },

  actionText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666',
    marginLeft: 6,
  },

  primaryAction: {
    backgroundColor: '#404CCF',
  },
  primaryActionText: {
    color: 'white',
    fontWeight: 'bold',
  }
});

export default CustomCalendar;