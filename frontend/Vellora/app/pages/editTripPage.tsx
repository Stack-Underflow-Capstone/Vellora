import { View, Text } from "react-native";
import { useRouter, useLocalSearchParams } from 'expo-router';
import { getTrip, Trip } from "../services/Trips";
import TripDetailsForm from "../components/TripDetailsForm";
import { useState, useEffect } from "react";

const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;


const EditTripPage = () => {
    const router = useRouter();
    const params = useLocalSearchParams();

    const [trip, setTrip] = useState<Trip | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    


    const handleGetTrip = async () => {
        const tripId = params.id as string;
        if (!tripId) return;

        setLoading(true);
        const response = await getTrip(tripId);
        
        if (!response) {
            alert("Trip not found, please try again.");
            setLoading(false);
            return;
        }

        setTrip(response);
        setLoading(false);
    }
    

    useEffect(() => {
        if (params?.id) {
            handleGetTrip();
        }
    }, [params?.id]);

    return (
        <View>
            <Text>Edit trip page</Text>
        </View>
    );
}

export default EditTripPage;