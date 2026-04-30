import { View, Text, Pressable, SafeAreaView } from "react-native";
import { router } from "expo-router";
import { rateStyles } from "../styles/ReimbursementStyles";

const irsRates = [
	{ name: "Business use", rate: "0.70" },
	{ name: "Medical or military moving", rate: "0.21" },
	{ name: "Charity use", rate: "0.14" },
];

export default function Page() {
	return (
		<SafeAreaView style={rateStyles.safe}>
			<View style={rateStyles.screenContainer}>
				<View style={rateStyles.headerRow}>
					<Pressable onPress={() => router.back()}>
						<Text style={rateStyles.backArrow}>{"<"}</Text>
					</Pressable>
					<Text style={rateStyles.headerTitle}>IRS Standard Mileage Rate</Text>
				</View>

				<Text style={rateStyles.paragraph}>
					Below is the IRS set standard mileage rate for US
				</Text>

				<View style={rateStyles.card}>
					<View style={rateStyles.cardSectionHeader}>
						<Text style={rateStyles.sectionLabel}>RATES</Text>
					</View>
					<View style={rateStyles.divider} />

					{irsRates.map((c, idx) => (
						<View key={c.name}>
							<View style={rateStyles.rateRow}>
								<Text style={rateStyles.rateRowText}>{c.name}</Text>
								<Text style={rateStyles.rateRowPrice}>${c.rate}</Text>
							</View>
							{idx < irsRates.length - 1 && <View style={rateStyles.divider} />}
						</View>
					))}
				</View>
			</View>
		</SafeAreaView>
	);
}
