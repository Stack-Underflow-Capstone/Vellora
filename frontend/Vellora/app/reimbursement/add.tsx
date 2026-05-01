import { useState } from "react";
import {
	View,
	Text,
	TextInput,
	Pressable,
	SafeAreaView,
	KeyboardAvoidingView,
	Platform,
	Modal,
	FlatList,
	ActivityIndicator,
} from "react-native";
import { rateStyles } from "../styles/ReimbursementStyles";
import { router } from "expo-router";
import CurrencyInput from "../components/CurrencyInput";
import {
	createRateCustomization,
	createRateCategory,
} from "../services/rateCustomizations";

type Category = {
	id: string;
	name: string;
	rate: string;
};

export default function AddCustomRatePage() {
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [year, setYear] = useState("");
	const [yearPickerVisible, setYearPickerVisible] = useState(false);
	const [categories, setCategories] = useState<Category[]>([]);
	const [isAddingCategory, setIsAddingCategory] = useState(false);
	const [newCategoryName, setNewCategoryName] = useState("");
	const [newCategoryRate, setNewCategoryRate] = useState("0.00");
	const [errors, setErrors] = useState("");
	const [saving, setSaving] = useState(false);

	const currentYear = new Date().getFullYear();
	const years = Array.from(
		{ length: currentYear - 1999 + 2 },
		(_, i) => `${2000 + i}`
	);

	const validateBeforeSave = () => {
		if (!name.trim()) return setErrors("Name is required.");
		if (!year.trim()) return setErrors("Year is required.");
		if (categories.length === 0)
			return setErrors("You must add at least one category.");
		for (const c of categories) {
			if (!c.name.trim()) return setErrors("Category names cannot be empty.");
			if (!c.rate.trim()) return setErrors("Category rates cannot be empty.");
		}
		setErrors("");
		return true;
	};

	const commitNewCategory = () => {
		const trimmed = newCategoryName.trim();
		if (!trimmed) return;
		const next: Category = {
			id: `${Date.now()}`,
			name: trimmed,
			rate: newCategoryRate || "0.00",
		};
		setCategories((prev) => [...prev, next]);
		setNewCategoryName("");
		setNewCategoryRate("0.00");
		setIsAddingCategory(false);
		setErrors("");
	};

	const deleteCategory = (id: string) => {
		setCategories((prev) => prev.filter((c) => c.id !== id));
	};

	const updateCategoryRate = (id: string, val: string) => {
		setCategories((prev) =>
			prev.map((c) => (c.id === id ? { ...c, rate: val } : c))
		);
	};

	const saveRate = async () => {
		if (!validateBeforeSave()) return;

		setSaving(true);
		setErrors("");

		try {
			const customization = await createRateCustomization({
				name: name.trim(),
				description: description.trim() || null,
				year: parseInt(year, 10),
			});

			if (categories.length > 0) {
				await Promise.all(
					categories.map((cat) => {
						const cleanedRate = cat.rate.replace(/[^0-9.-]/g, "");
						const costPerMile = parseFloat(cleanedRate);
						if (isNaN(costPerMile) || costPerMile < 0) {
							throw new Error(
								`Invalid rate for category "${cat.name}": must be a non-negative number`
							);
						}
						return createRateCategory(customization.id, {
							name: cat.name.trim(),
							cost_per_mile: costPerMile,
						});
					})
				);
			}

			router.replace("/(tabs)/stats");
		} catch (err) {
			setErrors(
				err instanceof Error
					? err.message
					: "Failed to save rate. Please try again."
			);
		} finally {
			setSaving(false);
		}
	};

	return (
		<SafeAreaView style={rateStyles.safe}>
			<KeyboardAvoidingView
				style={{ flex: 1 }}
				behavior={Platform.OS === "ios" ? "padding" : undefined}>
				<View style={rateStyles.fullScreenWhite}>
					<View style={rateStyles.formHeaderRow}>
						<Pressable
							onPress={() => router.back()}
							style={rateStyles.closeCircle}>
							<Text style={rateStyles.closeText}>×</Text>
						</Pressable>
						<Text style={rateStyles.formTitle}>Add custom rate</Text>
					</View>

					{errors ? (
						<Text style={{ color: "red", marginBottom: 10 }}>{errors}</Text>
					) : null}

					<View style={rateStyles.formFieldGroup}>
						<Text style={rateStyles.formLabel}>Name</Text>
						<TextInput
							style={rateStyles.formInput}
							value={name}
							onChangeText={setName}
							placeholder="Custom rate name"
						/>
					</View>

					<View style={rateStyles.formFieldGroup}>
						<Text style={rateStyles.formLabel}>Description</Text>
						<TextInput
							style={rateStyles.formInput}
							value={description}
							onChangeText={setDescription}
							placeholder="Description"
						/>
					</View>

					<View style={rateStyles.formFieldGroup}>
						<Text style={rateStyles.formLabel}>Year</Text>
						<Pressable
							style={[
								rateStyles.formInput,
								{ justifyContent: "center", width: 120 },
							]}
							onPress={() => setYearPickerVisible(true)}>
							<Text>{year || "Select year"}</Text>
						</Pressable>
					</View>

					<Modal visible={yearPickerVisible} transparent animationType="fade">
						<View style={rateStyles.modalOverlay}>
							<View style={rateStyles.modalCard}>
								<Text style={rateStyles.modalTitle}>Select Year</Text>
								<FlatList
									data={years}
									style={{ maxHeight: 250 }}
									keyExtractor={(item) => item}
									renderItem={({ item }) => (
										<Pressable
											onPress={() => {
												setYear(item);
												setYearPickerVisible(false);
											}}
											style={rateStyles.modalItem}>
											<Text style={{ fontSize: 16 }}>{item}</Text>
										</Pressable>
									)}
								/>
								<Pressable onPress={() => setYearPickerVisible(false)}>
									<Text style={{ padding: 10, textAlign: "center" }}>
										Close
									</Text>
								</Pressable>
							</View>
						</View>
					</Modal>

					<View style={rateStyles.formHeadingRow}>
						<Text style={rateStyles.sectionLabel}>Categories and costs</Text>
					</View>

					{!isAddingCategory && (
						<Pressable
							onPress={() => {
								setIsAddingCategory(true);
								setErrors("");
							}}
							style={rateStyles.addRow}>
							<View style={rateStyles.addIconCircle}>
								<Text style={rateStyles.addIconText}>+</Text>
							</View>
							<Text style={rateStyles.addText}>Add a category</Text>
						</Pressable>
					)}

					{isAddingCategory && (
						<View style={{ marginBottom: 10 }}>
							<View style={rateStyles.rateRow}>
								<TextInput
									style={rateStyles.categoryInput}
									placeholder="Category name"
									value={newCategoryName}
									onChangeText={setNewCategoryName}
								/>
								<View style={{width:90}}>
									<CurrencyInput
										label=""
										value={newCategoryRate}
										onChangeText={setNewCategoryRate}
										// style={{ width: 90 }}
									/>
								</View>
								<Pressable
									onPress={commitNewCategory}
									style={{
										backgroundColor: "#4F46E5",
										paddingVertical: 6,
										paddingHorizontal: 12,
										borderRadius: 6,
										marginLeft: 10,
									}}>
									<Text style={{ color: "white" }}>Save</Text>
								</Pressable>
							</View>
						</View>
					)}

					{categories.map((c) => (
						<View key={c.id} style={rateStyles.rateRow}>
							<Pressable onPress={() => deleteCategory(c.id)}>
								<View style={rateStyles.minusIcon} />
							</Pressable>
							<Text style={rateStyles.rateRowText}>{c.name}</Text>

							<View style={{ width: 90 }}>
								<CurrencyInput
									label=""
									value={c.rate}
									onChangeText={(v) => updateCategoryRate(c.id, v)}
									style={{ width: 90 }}
								/>
							</View>
						</View>
					))}

					<Pressable
						style={[rateStyles.formSaveButton, saving && { opacity: 0.6 }]}
						onPress={saveRate}
						disabled={saving}>
						{saving ? (
							<ActivityIndicator color="#fff" />
						) : (
							<Text style={rateStyles.formSaveText}>Save</Text>
						)}
					</Pressable>
				</View>
			</KeyboardAvoidingView>
		</SafeAreaView>
	);
}
