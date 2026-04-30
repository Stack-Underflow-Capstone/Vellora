import { useState } from "react";
import { View, Text, Pressable, SafeAreaView, TextInput, KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { router } from "expo-router";
import { createVehicle } from "../services/vehicles";

// use the same styles as in reimbursement
import { rateStyles } from "../styles/ReimbursementStyles";

export default function AddVehiclePage() {
    const [name, setName] = useState("");
    const [licensePlate, setLicensePlate] = useState("");
    const [model, setModel] = useState("");
    const [year, setYear] = useState("");
    const [color, setColor] = useState("");

    const [saving, setSaving] = useState(false);
    const [errors, setErrors] = useState("");

    const validate = () => {
        if (!name.trim()) return "Name is required (e.g., 'My Honda')";
        if (!licensePlate.trim()) return "License plate is required";
        if (!model.trim()) return "Model is required";
        return "";
    };

    const handleSave = async () => {
        const errorMsg = validate();
        if (errorMsg) {
            setErrors(errorMsg);
            return;
        }

        setSaving(true);
        setErrors("");

        try {
            await createVehicle({
                name: name.trim(),
                license_plate: licensePlate.trim(),
                model: model.trim(),
                year: year ? parseInt(year) : undefined,
                color: color.trim() || undefined,
            });
            router.back();
        } catch (error) {
            setErrors("Failed to save vehicle. Please try again.");
        } finally {
            setSaving(false);
        }
    };

    return (
        <SafeAreaView style={rateStyles.safe}>
            <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{ flex: 1 }}>
                <View style={rateStyles.fullScreenWhite}>
                    <View style={rateStyles.formHeaderRow}>
                        <Pressable onPress={() => router.back()} style={rateStyles.closeCircle}>
                            <Text style={rateStyles.closeText}>X</Text>
                        </Pressable>
                        <Text style={rateStyles.formTitle}>Add Vehicle</Text>
                    </View>

                    {errors ? <Text style={{ color: "red", marginBottom: 10 }}>{errors}</Text> : null}
                    
                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>Vehicle Nickname</Text>
                        <TextInput
                            style={rateStyles.formInput}
                            placeholder="e.g., 'My Honda'"
                            value={name}
                            onChangeText={setName}
                        />
                    </View>
                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>License Plate</Text>
                        <TextInput
                            style={rateStyles.formInput}
                            placeholder="e.g. ABC-1234"
                            value={licensePlate}
                            onChangeText={setLicensePlate}
                        />
                    </View>
                    <View style={rateStyles.formFieldGroup}>
                        <Text style={rateStyles.formLabel}>Model</Text>
                        <TextInput
                            style={rateStyles.formInput}
                            placeholder="e.g. Ford A-123"
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

                    <Pressable onPress={handleSave} disabled={saving} style={[rateStyles.formSaveButton, saving && { opacity: 0.6 }]}>
                        {saving ? (
                            <ActivityIndicator color="#fff" size="small" />
                        ) : (
                            <Text style={rateStyles.formSaveText}>Save Vehicle</Text>
                        )}
                    </Pressable>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}