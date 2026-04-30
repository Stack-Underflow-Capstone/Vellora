import { Text, View, ScrollView, TouchableOpacity, Modal, TouchableWithoutFeedback } from "react-native";
import { Link, useRouter, useFocusEffect } from "expo-router";
import { SafeAreaView, useSafeAreaInsets } from "react-native-safe-area-context";
import { getProviderAuthorizeUrl, login } from "../services/auth";
import { getCurrentUser, User } from "../services/user";
import { tokenStorage } from "../services/tokenStorage";
import { FontAwesome } from "@expo/vector-icons";
import Button from "../components/Button";
import React, { useEffect, useState, useCallback } from "react";
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { registerDevice } from "../services/Notifications";
import { useTripData } from "../contexts/TripDataContext";
// Common Places
import { useCommonPlaces } from "../hooks/useCommonPlaces";
import CommonPlaceCard from "../components/CommonPlaceCard";
import CustomCalendar from "../components/CustomCalendar";
import MonthYearDropdown from "../components/MonthYearDropdown";
import { getMonthlyStats, MonthlyStats } from "../services/Trips";

// import Tracking from "../components/tracking";

export default function Index() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  
  // state for modal pop up with trip log seelction
  const [shotLogTripModal, setShowLogTripModal] = useState(false);

  const { places: commonPlaces, loading } = useCommonPlaces();
  const { tripData, updateTripData, resetTripData } = useTripData();

  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [monthlyStats, setMonthlyStats] = useState<MonthlyStats>({
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    total_drives: 0,
    total_miles: 0,
    total_reimbursement: 0
  });

  //get user data for welcome message
  const fetchUser = async () => {
    const token = tokenStorage.getToken();
    if (token) {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (err) {
        setUser(null);
      }
    }
  };

  const fetchStats = async () => {
    try {
      const month = currentDate.getMonth() + 1;
      const year = currentDate.getFullYear();

      const response: any = await getMonthlyStats(month, year);

      // show what the backend sent
      console.log('RAW STATS FROM BACKEND: ', JSON.stringify(response, null, 2));

      const rawData = response?.data || response || {};

      setMonthlyStats({
        month: rawData.month ?? month,
        year: rawData.year ?? year,
        total_drives: rawData.total_drives ?? 0,
        total_miles: rawData.total_miles ?? 0,
        total_reimbursement: rawData.total_reimbursement ?? 0
      });
      
    } catch (error) {
      console.error('Error fetching monthly stats:', error);
      alert('Failed to fetch monthly stats. Please try again later.');
    }
  }
  useEffect(() => {
    fetchUser();
  }, []);

  //refresh user data so change in user profile reflects immediately
  useFocusEffect(
    useCallback(() => {
      fetchUser();
      fetchStats();
    }, [currentDate])
  );

  // modal button handlers
  const handleManualLogPress = () => {
    setShowLogTripModal(false);     // close modal
    resetTripData();                // reset trip data context to clear any previous trip data
    router.push('/manualLogScreen');  // navigate to manual log screen
  };

  const handleLiveTrackPress = () => {
    setShowLogTripModal(false);   // close modal
    resetTripData();              // reset trip data context to clear any previous trip data
    router.push('/tracking');    // navigate to live tracking screen
  };

  const requestPushToken = async () => {
    if (Device.isDevice) { // Checking if a physical device
      try {
        // Get the notification permissions
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        // If no perms, request
        if (existingStatus !== 'granted') {
          const { status } = await Notifications.requestPermissionsAsync();
          finalStatus = status;
        }
        
        if (finalStatus !== 'granted') { // If no access no permissions
          alert('Permissions not granted to get push notifications!');
          throw new Error('Permissions not granted to get push notifications!');
        }

        // Get the project ID to be able to send notifications
        const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;

        if (!projectId) {
          throw new Error('Project ID not found!');
        }

        const token = await Notifications.getExpoPushTokenAsync();
        await registerDevice(token);

      } catch (error) {
        console.error('Failed to get push token', error);
      }
    } else {
      alert('Physical Device required for push notifications');
    }
  };

// Use effect for requesting notification push tokens for notifications
useEffect(() => {
  requestPushToken();
}, []);

  return (

    <View style= {{ flex: 1 }}>
      <View className="bg-testWhite flex-1">

        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 100 }}
        >

          {/* purple header */}
          <View className="bg-primaryPurple w-full pb-24">

            <View style={{ paddingTop: insets.top + 20, paddingHorizontal: 25 }}>
              <Text className="text-5xl text-textWhite font-bold">
                Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ','}!
              </Text>
            </View>
          </View>
          <View className="bg-primaryPurple">
            <View className="bg-white rounded-2xl shadow-sm mx-6 p-6 -mt-12 mb-6 z-10" style={{ elevation: 3 }}>
                <View className="items-start mb-6 items-center">
                  <MonthYearDropdown 
                  currentDate={currentDate}
                  onDateChange={setCurrentDate}
                  />
                </View>

                {/* stats */}
                <View className="flex-row justify-between items-center">

                  <View className="items-center">
                    <Text className="text-3xl font-extrabold text-black">{Number(monthlyStats?.total_drives) || 0}</Text>
                    <Text className="text-[10px] mt-1 font-semibold text-gray-800 tracking-widest uppercase">Drives</Text>
                  </View>

                  <View className="items-center">
                    <Text className="text-3xl font-extrabold text-black">{Math.round(Number(monthlyStats?.total_miles)) || 0}</Text>
                    <Text className="text-[10px] mt-1 font-semibold text-gray-800 tracking-widest uppercase">Miles</Text>
                  </View>

                  <View className="items-center">
                    <Text className="text-3xl font-extrabold text-[#4ade80]">${(Number(monthlyStats?.total_reimbursement) || 0).toFixed(0)}</Text>
                    <Text className="text-[10px] mt-1 font-semibold text-[#4ade80]tracking-widest uppercase">Logged</Text>
                  </View>
                </View>
            </View>
          </View>


          {/* page body */}
          <View className="px-6 my-8">


            {/* trip quickstart */}
            <Text className="text-2xl text-textBlack font-bold mb-4">Quick Start</Text>
            <Button
              title="Log a Trip"
              onPress={() => setShowLogTripModal(true)}
              className="w-full py-4 px-5" 
            />

            {/* common places */}
            <View className="mt-8 mb-4 flex-row justify-between items-center">
              <Text className="text-2xl text-textBlack font-bold mb-4">Common Places</Text>
              <Button 
                title="+ Add Place"
                onPress={() => {router.push('/AddCommonPlaceScreen')}}
                className="px-3 py-1.5 rounded-full flex-row items-center"
              />

            </View>

            {/* common places GRID CARDS*/}
            <View className="flex-row flex-wrap gap-4">

              {/* show loading state */}
              {loading && <Text>Loading common places...</Text>}

              {/* rednder places */}
              {commonPlaces.map((place) => (
                <CommonPlaceCard
                  key={place.id}
                  title={place.name}
                  address={place.address}
                  onPress={() => router.push({
                    pathname: '/AddCommonPlaceScreen',
                    params: {
                      id: place.id,
                      title: place.name,
                      address: place.address
                      // lat: place.lat,
                      // lng: place.lng
                    } 
                  })}
                />
              ))}  
            </View>

            {/* calendar */}
            <View className="mt-8 mb-4 flex-row justify-between items-center">
              <Text className="text-2xl text-textBlack font-bold mb-4">Trip Schedule</Text>
            </View>

            <View>
              <CustomCalendar />
            </View>
              
          </View>
        </ScrollView>

        <Modal
          animationType="fade"
          transparent={true}
          visible={shotLogTripModal}
          onRequestClose={() => setShowLogTripModal(false)}
        >
          <TouchableOpacity
            style={{ flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center' }}
            activeOpacity={1}
            onPress={() => setShowLogTripModal(false)}  // click out
          >
            {/* modal white card */}
            <TouchableWithoutFeedback>
              <View className="bg-white w-[85%] rounded-3xl p-6 shadow-lg">
                <View className="flex-row justify-between items-center mb-2">

                  <TouchableOpacity
                    onPress={() => setShowLogTripModal(false)}
                    className="p-2 bg-gray-100 rounded-full"
                  >
                    <FontAwesome name="close" size={16} color="#6B7280" />
                  </TouchableOpacity>
                </View>
                <Text className="text-2xl font-bold text-center mb-6 text-black">Would you like to...</Text>

                {/* options buttons */}
                <Button 
                  title="Manually Log a Trip"
                  onPress={handleManualLogPress}
                  className="mb-4 w-full py-4 px-5"
                />
                <Button 
                  title="Live Track a Trip"
                  onPress={handleLiveTrackPress}
                  className="mb-4 w-full py-4 px-5"
                />
              </View>
            </TouchableWithoutFeedback>

          </TouchableOpacity>
        </Modal>
      </View>
    </View>
    // <SafeAreaView className="flex-1 justify-start p-[25px]"
    // >
    //   <View className="bg-primaryPurple">
    //     <Text className="text-5xl text-primaryPurple font-bold">Welcome back,</Text>
    //   </View>
    //   <Link href="../tracking">Live track a trip</Link>
    //   <Link href="../manualLogScreen">Manually log a trip</Link>
    //   <Link href="../trackingTest"></Link>
    //   {/* <Tracking></Tracking> */}
    // </SafeAreaView>
  );
}
