import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { Image } from 'expo-image';
import { FontAwesome } from '@expo/vector-icons';
import { useState, useEffect, useCallback } from 'react';
import { getCurrentUser, getTripCounts, User, TripCounts } from '../services/user';
import { tokenStorage } from '../services/tokenStorage';

// Commented out original rates functionality - keeping for reference
// import { useState, useEffect } from "react";
// import { useLocalSearchParams, router } from "expo-router";
// import { View, Text, ActivityIndicator } from "react-native";
// import ReimbursementRateListPage from "../components/ReimbursementRateListPage";
// import {
// 	getRateCustomizations,
// 	RateCustomization,
// 	deleteRateCustomization,
// } from "../services/rateCustomizations";
// import { tokenStorage } from "../services/tokenStorage";

// export type CustomRate = {
// 	id: string;
// 	name: string;
// 	description: string;
// 	year: string;
// 	categories: {
// 		id: string;
// 		name: string;
// 		rate: string;
// 	}[];
// };

// function mapToCustomRate(customization: RateCustomization): CustomRate {
// 	return {
// 		id: customization.id,
// 		name: customization.name,
// 		description: customization.description || "",
// 		year: customization.year.toString(),
// 		categories: (customization.categories || []).map((cat) => ({
// 			id: cat.id,
// 			name: cat.name,
// 			rate: cat.cost_per_mile.toFixed(2),
// 		})),
// 	};
// }

// export default function Profile() {
// 	const params = useLocalSearchParams();
// 	const [customRates, setCustomRates] = useState<CustomRate[]>([]);
// 	const [loading, setLoading] = useState(true);
// 	const [error, setError] = useState<string | null>(null);
// 	const [redirecting, setRedirecting] = useState(false);
// 	const [deletingId, setDeletingId] = useState<string | null>(null);
// 	const [currentToken, setCurrentToken] = useState<string | null>(null);

// 	const fetchRates = async () => {
// 		const token = tokenStorage.getToken();
// 		if (!token) {
// 			if (!redirecting) {
// 				setRedirecting(true);
// 				router.replace({
// 					pathname: "/login",
// 					params: { redirect: "/(tabs)/profile" },
// 				} as any);
// 			}
// 			return;
// 		}

// 		setLoading(true);
// 		setError(null);
// 		setRedirecting(false);
// 		try {
// 			setCurrentToken(token);
// 			const rates = await getRateCustomizations(token || undefined);
// 			const mappedRates = rates
// 				.map(mapToCustomRate)
// 				.filter((rate) => rate.name !== "IRS Standard Rates");
// 			setCustomRates(mappedRates);
// 		} catch (err) {
// 			if (
// 				(err instanceof Error &&
// 					(err.message.includes("Authentication required") ||
// 						err.message.includes("Unauthorized"))) ||
// 				(err as any).status === 401
// 			) {
// 				if (!redirecting) {
// 					setRedirecting(true);
// 					tokenStorage.clearToken();
// 					router.replace({
// 						pathname: "/login",
// 						params: { redirect: "/(tabs)/profile" },
// 					} as any);
// 					return;
// 				}
// 			}
// 			setError(err instanceof Error ? err.message : "Failed to load rates");
// 		} finally {
// 			setLoading(false);
// 		}
// 	};

// 	useEffect(() => {
// 		const timer = setTimeout(() => {
// 			fetchRates();
// 		}, 500);
// 		return () => clearTimeout(timer);
// 	}, []);

// 	useEffect(() => {
// 		if (params.newRate && typeof params.newRate === "string") {
// 			try {
// 				const parsed = JSON.parse(params.newRate);
// 				setCustomRates((prev) => {
// 					if (prev.some((r) => r.id === parsed.id)) return prev;
// 					return [...prev, parsed];
// 				});
// 				fetchRates();
// 			} catch {}
// 		}
// 	}, [params.newRate]);

// 	const handleDelete = async (id: string) => {
// 		if (deletingId) return;
// 		setDeletingId(id);
// 		try {
// 			const token = currentToken || tokenStorage.getToken();
// 			if (!token) {
// 				setError("Please log in to delete rates");
// 				setDeletingId(null);
// 				return;
// 			}

// 			await deleteRateCustomization(id, token);
// 			setCustomRates((prev) => prev.filter((rate) => rate.id !== id));
// 			setError(null);
// 		} catch (err) {
// 			if (
// 				(err instanceof Error &&
// 					(err.message.includes("Authentication required") ||
// 						err.message.includes("Unauthorized"))) ||
// 				(err as any).status === 401
// 			) {
// 				setError("Your session has expired. Please log in again.");
// 				tokenStorage.clearToken();
// 				setTimeout(() => {
// 					if (!redirecting) {
// 						setRedirecting(true);
// 						router.replace({
// 							pathname: "/login",
// 							params: { redirect: "/(tabs)/profile" },
// 						} as any);
// 					}
// 				}, 2000);
// 			} else {
// 				setError(err instanceof Error ? err.message : "Failed to delete rate");
// 			}
// 		} finally {
// 			setDeletingId(null);
// 		}
// 	};

// 	if (loading) {
// 		return (
// 			<View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
// 				<ActivityIndicator size="large" color="#3F46D6" />
// 				<Text style={{ marginTop: 10 }}>Loading rates...</Text>
// 			</View>
// 		);
// 	}

// 	if (error) {
// 		return (
// 			<View
// 				style={{
// 					flex: 1,
// 					justifyContent: "center",
// 					alignItems: "center",
// 					padding: 20,
// 				}}>
// 				<Text style={{ color: "red", marginBottom: 10 }}>{error}</Text>
// 				<Text
// 					onPress={fetchRates}
// 					style={{ color: "#3F46D6", textDecorationLine: "underline" }}>
// 					Retry
// 				</Text>
// 			</View>
// 		);
// 	}

// 	return (
// 		<ReimbursementRateListPage
// 			rates={customRates}
// 			onCreateCustom={() => router.push("/reimbursement/add")}
// 			onOpenIRS={() => router.push("/reimbursement/irs")}
// 			onOpenCustomRate={(id) =>
// 				router.push({
// 					pathname: "/reimbursement/details",
// 					params: { id },
// 				})
// 			}
// 			onDelete={handleDelete}
// 			deletingId={deletingId}
// 		/>
// 	);
// }

export default function Profile() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tripCounts, setTripCounts] = useState<TripCounts | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfileData = async () => {
    const token = tokenStorage.getToken();
    if (!token) {
      router.replace('/login' as any);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      //get user data and trip counts
      const [userData, tripData] = await Promise.all([
        getCurrentUser(),
        getTripCounts()
      ]);
      
      setUser(userData);
      setTripCounts(tripData);
    } catch (err) {
      if (err instanceof Error && (err.message.includes("Authorization") || (err as any).status === 401)) {
        //if token expired or invalid redirect to login
        tokenStorage.clearToken();
        router.replace('/login' as any);
        return;
      }
      setError(err instanceof Error ? err.message : 'Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfileData();
  }, []);

  //refresh data when we return to profile page to update any user changes
  useFocusEffect(
    useCallback(() => {
      fetchProfileData();
    }, [])
  );

  const handleEditProfile = () => {
    router.push('/edit-profile' as any);
  };

  if (loading) {
    return (
      <View className="flex-1 bg-gray-60 justify-center items-center">
        <ActivityIndicator size="large" color="#404CCF" />
        <Text className="text-gray-600 mt-2">Loading profile...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View className="flex-1 bg-gray-60 justify-center items-center px-6">
        <Text className="text-red-500 text-center mb-4">{error}</Text>
        <TouchableOpacity 
          onPress={fetchProfileData}
          className="bg-blue-500 px-6 py-3 rounded-lg"
        >
          <Text className="text-white font-medium">Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-gray-60">
        
        <View className="bg-white px-10 py-20 mx-3 mt-3 rounded-3xl">
          <View className="flex-row items-center">
            <View 
              style={{width: 120, height: 120, borderWidth: 0}}
              className="items-center justify-center mr-10"
            >
              <Image 
                source={require('../assets/placeholderProfile.svg')}
                contentFit="cover"
                style={{width: 200, height: 125, borderRadius: 55}}
              />
            </View>
            
            <View className="flex-1">
              <Text 
                style={{
                  fontSize: 23,
                  fontFamily: 'Inter',
                  fontWeight: 'bold',
                  color: '#404CCF',
                  marginBottom: 8
                }}
              >
                {user?.full_name || user?.email || 'User'}
              </Text>
              <View className="flex-row mb-4">
                <Text className="text-black mr-6 font-bold">
                  {tripCounts?.total_trips || 0} trips
                </Text>
                <Text className="text-black font-bold">
                  {tripCounts?.total_scheduled || 0} scheduled
                </Text>
              </View>
              
              <TouchableOpacity 
                style={{
                  backgroundColor: '#898989',
                  borderRadius: 12,
                  paddingHorizontal: 45,
                  paddingVertical: 8,
                  alignSelf: 'flex-start'
                }}
                onPress={handleEditProfile}
              >
                <Text className="text-white font-medium">Edit profile</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        
        <Text 
          style={{
            fontSize: 14,
            fontFamily: 'Inter',
            fontWeight: 'bold',
            color: '#404CCF',
            marginTop: 20,
            marginLeft: 30
          }}>PERSONALIZATION</Text>

        <View className="bg-white mt-3 mx-3 rounded-3xl">
          <View className="mt-1">
            
            <TouchableOpacity 
              className="bg-white px-6 py-4 flex-row items-center justify-between border-b border-gray-100 rounded-3xl mb-1"
              onPress={() => router.push('/reimbursement')}
            >
              <View className="flex-row items-center">
                <FontAwesome name="dollar" size={22} color="black" className="mr-3 ml-2" />
                <Text className="text-black text-base ml-3">Reimbursement Rates</Text>
              </View>
              <FontAwesome name="chevron-right" size={16} color="black" />
            </TouchableOpacity>

            <TouchableOpacity 
              className="bg-white px-6 py-4 flex-row items-center justify-between rounded-3xl mb-1"
              onPress={() => router.push('/vehicles')}
            >
              <View className="flex-row items-center">
                <FontAwesome name="car" size={18} color="black" className="mr-3 ml-2" />
                <Text className="text-black text-base ml-3">Vehicles</Text>
              </View>
              <FontAwesome name="chevron-right" size={16} color="black" />
            </TouchableOpacity>

          </View>
        </View>

        <Text 
          style={{
            fontSize: 14,
            fontFamily: 'Inter',
            fontWeight: 'bold',
            color: '#404CCF',
            marginTop: 20,
            marginLeft: 30
          }}>ACCOUNT</Text>

        <View className="bg-white mt-3 mx-3 rounded-3xl">
          <View className="mt-1">
            
            <TouchableOpacity className="bg-white px-6 py-4 flex-row items-center justify-between border-b border-gray-100 rounded-3xl mb-1">
              <View className="flex-row items-center">
                <Text className="text-black text-base ml-3"></Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity className="bg-white px-6 py-4 flex-row items-center justify-between rounded-3xl mb-1">
              <View className="flex-row items-center">
                <Text className="text-black text-base ml-3"></Text>
              </View>
            </TouchableOpacity>

          </View>
        </View>

    </View>
  );
}
