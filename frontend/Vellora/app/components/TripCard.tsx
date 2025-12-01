import { View, Text, StyleSheet, Pressable } from "react-native";
import React from 'react';
import GeometryMap from "./GeometryMap";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";

// start address
// end address

// value - amount of miles

interface TripCardProps {
    geometry?: object | null;
    start_address: string;
    end_address: string;
    mileage_reimbursement_total: number;
    distance_meters: number;
}

const router = useRouter();


const handleEditTrip = () => {
    router.push('/pages/editTripPage')
}

const TripCard: React.FC<TripCardProps> = ({ geometry, start_address, end_address, mileage_reimbursement_total, distance_meters }) => {

    return (
        <View style={styles.cardContainer}>
            <View style={styles.mapContainer}>
                <GeometryMap geometry={geometry}/>
            </View>
            <View style={styles.textContainer}>
                <View style={styles.addressTextContainer}> 
                    <Text style={{flexWrap: 'wrap', flex: 1, fontSize: 12}}>{'\u2022'} {start_address}</Text>
                    <Text style={{flexWrap: 'wrap', flex: 1, fontSize: 12}}>{'\u2022'} {end_address}</Text>
                </View>
                <View style={{marginBottom: 40, marginLeft: 40}}>
                    <Text style={{color: '#4DBF69'}}>${mileage_reimbursement_total} - {distance_meters} mi</Text>
                </View>
            </View>
            <Pressable style={styles.editContainer} onPress={handleEditTrip}>
                <FontAwesome name='pencil' size={18} color="#6B7280"></FontAwesome>
            </Pressable>
        </View>
    )
}

const styles = StyleSheet.create({
    cardContainer: {
        justifyContent: 'flex-start',
        alignItems: 'center',
        alignContent: 'center',
        width: '100%',
        height: '10%',
        flexDirection: 'row',
        borderTopWidth: 1.5,
        borderColor: '#b5b5b5',
        paddingTop: 40,
        paddingBottom: 40,
        backgroundColor: 'white'
    },
    mapContainer: {
        height: 115, 
        width: 115, 
        overflow: 'hidden', 
        borderRadius: 10, 
        flexShrink: 0 ,
        marginLeft: 15
    },
    textContainer: {
        flex: 1, 
        marginLeft: 10,
        marginTop: 2
    },
    addressTextContainer: {
        marginBottom: 30, 
        marginTop: 20,
        maxWidth: '80%'
    },
    editContainer: {
        marginRight: 15
    }

});


export default TripCard