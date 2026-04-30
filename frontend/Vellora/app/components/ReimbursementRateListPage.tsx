import { View, Text, Pressable, SafeAreaView, FlatList, ScrollView } from "react-native";
import { rateStyles } from "../styles/ReimbursementStyles";
import type { CustomRate } from "../reimbursement";
import { router } from "expo-router";

type Props = {
	rates: CustomRate[];
	onCreateCustom: () => void;
	onOpenIRS: () => void;
	onOpenCustomRate: (id: string) => void;
	onDelete: (id: string) => void;
	deletingId: string | null;
};

export default function ReimbursementRateListPage({
	rates,
	onCreateCustom,
	onOpenIRS,
	onOpenCustomRate,
	onDelete,
	deletingId,
}: Props) {
	return (
		<SafeAreaView style={rateStyles.safe}>

			<ScrollView contentContainerStyle={rateStyles.screenContainer}>

				<View style={rateStyles.headerRow}>
					<Text style={rateStyles.headerTitle}>Vehicles</Text>
				</View>
				<Text style={rateStyles.paragraph}>
					Manage your personal and business vehicles for trip tracking.
				</Text>

				<View style={rateStyles.card}>
					<Pressable onPress={() => router.push("../vehicles")}>
						<View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
							<Text style={rateStyles.listItem}>Manage My Vehicles</Text>
							<Text style={{ fontSize: 18, color: "#3F46D6" }}>{">"}</Text>
						</View>
					</Pressable>
				</View>

				{/* space between sections */}
				<View style={{ height: 30 }} /> 


				<View style={rateStyles.headerRow}>
					<Text style={rateStyles.headerTitle}>Reimbursement rate</Text>
				</View>

				<Text style={rateStyles.paragraph}>
					Personalize your experience by selecting or adding a custom mileage
					reimbursement rate
				</Text>

				<View style={rateStyles.card}>
					<Pressable onPress={onOpenIRS}>
						<Text style={rateStyles.listItem}>IRS Standard Rates</Text>
					</Pressable>

					{rates.map((item) => (
						<View key={item.id} style={{ flexDirection: "row", alignItems: "center" }}>
							<Pressable
								style={{ flex: 1 }}
								onPress={() => onOpenCustomRate(item.id)}>
								<Text style={rateStyles.listItem}>{item.name}</Text>
							</Pressable>
							<Pressable
								onPress={() => onDelete(item.id)}
								disabled={deletingId === item.id}
								style={{
									paddingHorizontal: 12,
									paddingVertical: 12,
									opacity: deletingId === item.id ? 0.5 : 1,
								}}>
								<Text style={{ color: "#EF4444", fontSize: 14 }}>Delete</Text>
							</Pressable>
						</View>	
					))}

					<Pressable onPress={onCreateCustom}>
						<Text style={rateStyles.addCustom}>+ Create custom rate</Text>
					</Pressable>
				</View>
				
				<View style={{ height: 50 }} />

			</ScrollView>
		</SafeAreaView>
	);
}
