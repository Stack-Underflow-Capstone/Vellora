import { View, Text, StyleSheet, Pressable } from "react-native";
import React from 'react';
import GeometryMap from "./GeometryMap";
import { FontAwesome } from "@expo/vector-icons";
import { useRouter } from "expo-router";

// start address
// end address

// value - amount of miles

interface TripCardProps {
    id?: string;
    geometry?: object | null;
    start_address: string;
    end_address: string;
    mileage_reimbursement_total: number;
    distance_meters: number;
}


const TripCard: React.FC<TripCardProps> = ({ id, geometry, start_address, end_address, mileage_reimbursement_total, distance_meters }) => {


const router = useRouter();


    const handleEditTrip = () => {
        router.push({
            pathname: '/pages/editTripPage',
            params: {
                    id: id
        }})
    } 

    return (
        <View style={styles.cardContainer}>
            <View style={styles.mapContainer}>
                <GeometryMap geometry={geometry}/>
            </View>
            <View style={styles.textContainer}>
                <View style={styles.addressTextContainer}> 
                    <Text numberOfLines={3} style={{flexWrap: 'wrap', flex: 1, fontSize: 12 }}>{'\u2022'} {start_address}</Text>
                    <Text numberOfLines={3} style={{flexWrap: 'wrap', flex: 1, fontSize: 12 }}>{'\u2022'} {end_address}</Text>
                </View>
                <View style={{marginLeft: 30}}>
                    <Text style={{color: '#4DBF69'}}>${mileage_reimbursement_total.toFixed(2)} - {distance_meters.toFixed(2)} mi</Text>
                </View>
            </View>
           <Pressable onPress={handleEditTrip} style={styles.editContainer}>
                <FontAwesome name='pencil' size={18} color="#6B7280"></FontAwesome>
            </Pressable>
        </View>
    )
}

const styles = StyleSheet.create({
    cardContainer: {
        justifyContent: 'flex-start',
        alignItems: 'center',
        width: '100%',
        minHeight: 155,
        flexDirection: 'row',
        borderTopWidth: 1.5,
        borderColor: '#b5b5b5',
        paddingTop: 12,
        paddingBottom: 12,
        backgroundColor: 'white'
    },
    mapContainer: {
        height: 100, 
        width: 100, 
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
        marginBottom: 15, 
        marginTop: 6,
    },
    editContainer: {
        marginRight: 6
    }
});


export default TripCard