import { useState, useEffect } from "react";
import {
	View,
	Text,
	Pressable,
	SafeAreaView,
	ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { rateStyles } from "../styles/ReimbursementStyles";
import { getRateCustomization } from "../services/rateCustomizations";

export default function CustomRateDetailsPage() {
	const params = useLocalSearchParams();
	const id = params?.id ? String(params.id) : null;
	const [rate, setRate] = useState<any>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		if (!id) {
			setError("No rate ID provided");
			setLoading(false);
			return;
		}

		const fetchRate = async () => {
			try {
				const customization = await getRateCustomization(id);
				setRate({
					id: customization.id,
					name: customization.name,
					description: customization.description || "",
					year: customization.year.toString(),
					categories: (customization.categories || []).map((cat) => ({
						id: cat.id,
						name: cat.name,
						rate: cat.cost_per_mile.toFixed(2),
					})),
				});
			} catch (err) {
				setError(err instanceof Error ? err.message : "Failed to load rate");
			} finally {
				setLoading(false);
			}
		};

		fetchRate();
	}, [id]);

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

	if (error || !rate) {
		return (
			<SafeAreaView style={rateStyles.safe}>
				<View
					style={{
						flex: 1,
						justifyContent: "center",
						alignItems: "center",
						padding: 20,
					}}>
					<Text style={{ color: "red", textAlign: "center" }}>
						{error || "No rate found."}
					</Text>
					<Pressable
						onPress={() => router.back()}
						style={{ marginTop: 20, padding: 10 }}>
						<Text style={{ color: "#3F46D6" }}>Go Back</Text>
					</Pressable>
				</View>
			</SafeAreaView>
		);
	}

	return (
		<SafeAreaView style={rateStyles.safe}>
			<View style={rateStyles.screenContainer}>
				<View style={rateStyles.headerRow}>
					<Pressable onPress={() => router.back()}>
						<Text style={rateStyles.backArrow}>{"<"}</Text>
					</Pressable>
					<Text style={rateStyles.headerTitle}>{rate.name}</Text>
					<Pressable
						onPress={() =>
							router.push({
								pathname: "/reimbursement/edit",
								params: { id: rate.id },
							} as any)
						}
						style={{ padding: 8 }}>
						<Text style={{ color: "#3F46D6", fontSize: 14 }}>Edit</Text>
					</Pressable>
				</View>

				{rate.description ? (
					<Text style={rateStyles.paragraph}>{rate.description}</Text>
				) : null}

				<View style={rateStyles.card}>
					<View style={rateStyles.cardSectionHeader}>
						<Text style={rateStyles.sectionLabel}>RATES</Text>
					</View>
					<View style={rateStyles.divider} />

					{rate.categories && rate.categories.length > 0 ? (
						rate.categories.map((c: any, idx: number) => (
							<View key={c.id}>
								<View style={rateStyles.rateRow}>
									<Text style={rateStyles.rateRowText}>{c.name}</Text>
									<Text style={rateStyles.rateRowPrice}>${c.rate}</Text>
								</View>
								{idx < rate.categories.length - 1 && (
									<View style={rateStyles.divider} />
								)}
							</View>
						))
					) : (
						<View style={rateStyles.rateRow}>
							<Text style={rateStyles.rateRowText}>No categories found</Text>
						</View>
					)}
				</View>
			</View>
		</SafeAreaView>
	);
}
