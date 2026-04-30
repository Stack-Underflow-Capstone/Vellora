import { useState, useEffect } from "react";
import { View, Text, Pressable, SafeAreaView, TextInput, Alert, Platform, ActivityIndicator, KeyboardAvoidingView } from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { getVehicle, updateVehicle, deleteVehicle } from "../services/vehicles";
import { rateStyles } from "../styles/ReimbursementStyles";

export default function EditVehiclePage() {
    const { id } = useLocalSearchParams();
    const vehicleId = Array.isArray(id) ? id[0] : id; // handle case where id might be an array

    const [name, setName] = useState("");
    const [licensePlate, setLicensePlate] = useState("");
    const [model, setModel] = useState("");
    const [year, setYear] = useState("");
    const [color, setColor] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [errors, setErrors] = useState("");

    useEffect(() => {
        if (!vehicleId) {
            setErrors("No vehicle ID provided.");
            setLoading(false);
            return;
        }

        getVehicle(vehicleId).then((v) => {
            setName(v.name || "");
            setLicensePlate(v.license_plate || "");
            setModel(v.model || "");
            setYear(v.year ? v.year.toString() : "");
            setColor(v.color || "");
        }).catch(() => setErrors("Failed to load vehicle details. Please try again."))
        .finally(() => setLoading(false));
    }, [vehicleId]);

    const handleUpdate = async () => {
        if (!vehicleId) return;

        setSaving(true);
        try {
            await updateVehicle(vehicleId, {
                name: name.trim(),
                license_plate: licensePlate.trim(),
                model: model.trim(),
                year: year ? parseInt(year) : undefined,
                color: color.trim() || undefined,
            });
            router.back();
        } catch (err) {
            setErrors("Failed to update vehicle. Please try again.");
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = () => {
        Alert.alert("Confirm Delete", "Are you sure you want to delete this vehicle?", [
            { text: "Cancel", style: "cancel" },
            {
                text: "Delete",
                style: "destructive",
                onPress: async () => {
                    if (!vehicleId) return;
                    try {
                        await deleteVehicle(vehicleId);
                        router.back();
                    } catch (e) {
                        setErrors("Failed to delete vehicle. Please try again.");
                    }
                },
            },
        ]);
    };

    if (loading) {
        return (
            <SafeAreaView style={rateStyles.safe}>
                <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                    <ActivityIndicator style={{ flex: 1 }} size="large" color="#3F46D6" />
                    <Text style={{ marginTop: 10 }}>Loading vehicle...</Text>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={rateStyles.safe}>
            <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{ flex: 1 }}>
                <View style={rateStyles.fullScreenWhite}>
                    <View style={rateStyles.formHeaderRow}>
                        <Pressable onPress={() => router.back()} style={rateStyles.closeCircle}>
                            <Text style={rateStyles.closeText}>{"<"}</Text>
                        </Pressable>
                        <Text style={rateStyles.formTitle}>Edit Vehicle</Text>
                        <Pressable onPress={handleDelete}>
                            <Text style={{ color: "red", fontWeight: "bold" }}>Delete</Text>
                        </Pressable>
                    </View>

                    {errors ? <Text style={{ color: "red", marginBottom: 10 }}>{errors}</Text> : null}

                    {/* form same layout as add page */}
                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>Vehicle Nickname</Text>
                        <TextInput 
                            style={rateStyles.formInput}
                            value={name}
                            onChangeText={setName}
                        />
                    </View>

                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>License Plate</Text>
                        <TextInput 
                            style={rateStyles.formInput}
                            value={licensePlate}
                            onChangeText={setLicensePlate}
                        />
                    </View>

                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>Model</Text>
                        <TextInput 
                            style={rateStyles.formInput}
                            value={model}
                            onChangeText={setModel}
                        />
                    </View>

                    <View style={{ flexDirection: 'row', gap: 10}}>
                        <View style={[rateStyles.formFieldGroup, { flex: 1 }]}>
                            <Text style={rateStyles.formLabel}>Year (optional)</Text>
                            <TextInput
                                style={rateStyles.formInput}
                                placeholder="e.g. 2026"
                                value={year}
                                onChangeText={setYear}
                                keyboardType="numeric"
                            />
                        </View>
                        <View style={[rateStyles.formFieldGroup, { flex: 1 }]}>
                            <Text style={rateStyles.formLabel}>Color (optional)</Text>
                            <TextInput
                                style={rateStyles.formInput}
                                placeholder="e.g. Red"
                                value={color}
                                onChangeText={setColor}
                            />
                        </View>
                    </View>

                    <Pressable onPress={handleUpdate} disabled={saving} style={[rateStyles.formSaveButton, saving && { opacity: 0.6 }]}>
                        {saving ? (
                            <ActivityIndicator color="#fff" />
                        ) : (
                            <Text style={rateStyles.formSaveText}>Save Changes</Text>
                        )}
                    </Pressable>
                </View>
                
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}