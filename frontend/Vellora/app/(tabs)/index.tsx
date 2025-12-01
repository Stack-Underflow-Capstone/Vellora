import { Text, View, ScrollView, TouchableOpacity, Modal, TouchableWithoutFeedback } from "react-native";
import { Link, useRouter } from "expo-router";
import { SafeAreaView, useSafeAreaInsets } from "react-native-safe-area-context";
import { getProviderAuthorizeUrl, login } from "../services/auth";
import { FontAwesome } from "@expo/vector-icons";
import Button from "../components/Button";
import { useState } from "react";

import { useCommonPlaces } from "../hooks/useCommonPlaces";
import CommonPlaceCard from "../components/CommonPlaceCard";
// import Tracking from "../components/tracking";

export default function Index() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  
  // state for modal pop up with trip log seelction
  const [shotLogTripModal, setShowLogTripModal] = useState(false);

  const { places: commonPlaces, loading } = useCommonPlaces();

  // temporary common places data
  // const commonPlaces = [

  //   { id: '1', title: 'Home', address: '123 Main St, Springfield, IL', lat: 39.7817, lng: -89.6501},
  //   { id: '2', title: 'Work', address: '456 Corporate Blvd, Springfield, IL', lat: 39.7990, lng: -89.6436},
  //   { id: '3', title: 'Gym', address: '789 Fitness Ave, Springfield, IL', lat: 39.7886, lng: -89.6544},
  //   { id: '4', title: 'Grocery Store', address: '101 Market St, Springfield, IL', lat: 39.7833, lng: -89.6550},
  // ];



  // modal button handlers
  const handleManualLogPress = () => {
    setShowLogTripModal(false);     // close modal
    router.push('/manualLogScreen');  // navigate to manual log screen
  };

  const handleLiveTrackPress = () => {
    setShowLogTripModal(false);   // close modal
    router.push('/tracking');    // navigate to live tracking screen
  };

  return (

    <View style= {{ flex: 1 }}>
      <View className="bg-testWhite flex-1">

        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={{ paddingBottom: 100 }}
        >

          {/* purple header */}
          <View className="bg-primaryPurple w-full pb-10">

            <View style={{ paddingTop: insets.top + 20, paddingHorizontal: 25 }}>
              <Text className="text-5xl text-textWhite font-bold">Welcome back,</Text>

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
