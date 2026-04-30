import { useState, useEffect, useCallback } from "react";
import { View, Text, Pressable, SafeAreaView, FlatList, ActivityIndicator, StyleSheet } from "react-native";
import { router, useFocusEffect } from "expo-router";
import { getVehicles, Vehicle } from "../services/vehicles";
import { rateStyles } from "../styles/ReimbursementStyles";

export default function VehiclesListPage() {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            const data = await getVehicles();
            setVehicles(data);
            setError(null);
        } catch (err) {
            setError("Failed to load vehicles. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // reload data every time we navigate back to this screen
    useFocusEffect(
        useCallback(() => {
            fetchVehicles();
        }, [])
    );

    const renderItem = ({ item }: { item: Vehicle }) => (
        <Pressable
            style={[rateStyles.card, { padding: 16, marginBottom: 10 }]}
            onPress={() => router.push({ pathname: `/vehicles/edit`, params: { id: item.id } } as any)}
        >
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                <View>
                    <Text style={[rateStyles.rateRowText, { marginBottom: 4 }]}>{item.name}</Text>
                    <Text style={{ color: "gray", fontSize: 14 }}>{item.model} - {item.license_plate} </Text>
                </View>
                <Text style={{ fontSize: 18, color: "#3F46D6", fontWeight: "bold" }}>{">"}</Text>
            </View>
        </Pressable>
    );

    if (loading) {
        return <ActivityIndicator style={{ flex: 1 }} size="large" color="#3F46D6" />;
    }

    return (
        <SafeAreaView style={rateStyles.safe}>
            <View style={rateStyles.screenContainer}>
                <View style={rateStyles.headerRow}>
                    <Text style={rateStyles.headerTitle}>My Vehicles</Text>
                    <Pressable onPress={() => router.push("/vehicles/add")}>
                        <Text style={{ color: "#3F46D6", fontSize: 16, fontWeight: "bold" }}>+ Add</Text>
                    </Pressable>
                </View>

                {error ? <Text style={{ color: "red", marginBottom: 10 }}>{error}</Text> : null}

                <FlatList
                    data={vehicles}
                    keyExtractor={(item) => item.id}
                    renderItem={renderItem}
                    contentContainerStyle={{ paddingBottom: 20, paddingTop: 10 }}
                    ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20 }}>No vehicles found</Text>}
                />
            </View>
        </SafeAreaView>
    );
}