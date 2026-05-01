import { useState, useEffect } from "react";
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
import { router, useLocalSearchParams } from "expo-router";
import CurrencyInput from "../components/CurrencyInput";
import {
	getRateCustomization,
	updateRateCustomization,
	createRateCategory,
	updateRateCategory,
	deleteRateCategory,
} from "../services/rateCustomizations";

type Category = {
	id: string;
	name: string;
	rate: string;
	isNew?: boolean;
};

export default function EditCustomRatePage() {
	const params = useLocalSearchParams();
	const id = params?.id ? String(params.id) : null;
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
	const [loading, setLoading] = useState(true);
	const [deletedCategoryIds, setDeletedCategoryIds] = useState<string[]>([]);

	const currentYear = new Date().getFullYear();
	const years = Array.from(
		{ length: currentYear - 1999 + 2 },
		(_, i) => `${2000 + i}`
	);

	useEffect(() => {
		if (!id) {
			setErrors("No rate ID provided");
			setLoading(false);
			return;
		}

		const fetchRate = async () => {
			try {
				const customization = await getRateCustomization(id);
				setName(customization.name);
				setDescription(customization.description || "");
				setYear(customization.year.toString());
				setCategories(
					(customization.categories || []).map((cat) => ({
						id: cat.id,
						name: cat.name,
						rate: cat.cost_per_mile.toFixed(2),
						isNew: false,
					}))
				);
			} catch (err) {
				setErrors(err instanceof Error ? err.message : "Failed to load rate");
			} finally {
				setLoading(false);
			}
		};

		fetchRate();
	}, [id]);

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
			id: `new_${Date.now()}`,
			name: trimmed,
			rate: newCategoryRate || "0.00",
			isNew: true,
		};
		setCategories((prev) => [...prev, next]);
		setNewCategoryName("");
		setNewCategoryRate("0.00");
		setIsAddingCategory(false);
		setErrors("");
	};

	const deleteCategory = (categoryId: string) => {
		setCategories((prev) => prev.filter((c) => c.id !== categoryId));
	};

	const handleDeleteCategory = (categoryId: string) => {
		const category = categories.find((c) => c.id === categoryId);
		if (category && !category.isNew) {
			setDeletedCategoryIds((prev) => [...prev, categoryId]);
		}
		deleteCategory(categoryId);
	};

	const updateCategoryRate = (categoryId: string, val: string) => {
		setCategories((prev) =>
			prev.map((c) => (c.id === categoryId ? { ...c, rate: val } : c))
		);
	};

	const updateCategoryName = (categoryId: string, val: string) => {
		setCategories((prev) =>
			prev.map((c) => (c.id === categoryId ? { ...c, name: val } : c))
		);
	};

	const saveRate = async () => {
		if (!validateBeforeSave() || !id) return;

		setSaving(true);
		setErrors("");

		try {
			await updateRateCustomization(id, {
				name: name.trim(),
				description: description.trim() || null,
				year: parseInt(year, 10),
			});

			for (const deletedId of deletedCategoryIds) {
				await deleteRateCategory(id, deletedId);
			}

			const existingCategories = categories.filter((c) => !c.isNew);
			const newCategories = categories.filter((c) => c.isNew);

			for (const cat of existingCategories) {
				const cleanedRate = cat.rate.replace(/[^0-9.-]/g, "");
				const costPerMile = parseFloat(cleanedRate);
				if (isNaN(costPerMile) || costPerMile < 0) {
					throw new Error(
						`Invalid rate for category "${cat.name}": must be a non-negative number`
					);
				}
				await updateRateCategory(id, cat.id, {
					name: cat.name.trim(),
					cost_per_mile: costPerMile,
				});
			}

			for (const cat of newCategories) {
				const cleanedRate = cat.rate.replace(/[^0-9.-]/g, "");
				const costPerMile = parseFloat(cleanedRate);
				if (isNaN(costPerMile) || costPerMile < 0) {
					throw new Error(
						`Invalid rate for category "${cat.name}": must be a non-negative number`
					);
				}
				await createRateCategory(id, {
					name: cat.name.trim(),
					cost_per_mile: costPerMile,
				});
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

	if (loading) {
		return (
			<SafeAreaView style={rateStyles.safe}>
				<View
					style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
					<ActivityIndicator size="large" color="#3F46D6" />
					<Text style={{ marginTop: 10 }}>Loading rate...</Text>
				</View>
			</SafeAreaView>
		);
	}

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
						<Text style={rateStyles.formTitle}>Edit custom rate</Text>
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
								<CurrencyInput
									label=""
									value={newCategoryRate}
									onChangeText={setNewCategoryRate}
									style={{ width: 90 }}
								/>
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
							<Pressable onPress={() => handleDeleteCategory(c.id)}>
								<View style={rateStyles.minusIcon} />
							</Pressable>
							<TextInput
								style={[rateStyles.rateRowText, { flex: 1 }]}
								value={c.name}
								onChangeText={(v) => updateCategoryName(c.id, v)}
							/>
							<CurrencyInput
								label=""
								value={c.rate}
								onChangeText={(v) => updateCategoryRate(c.id, v)}
								style={{ width: 90 }}
							/>
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
