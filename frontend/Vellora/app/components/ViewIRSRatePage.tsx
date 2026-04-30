import { View, Text, Pressable, SafeAreaView } from "react-native";
import { rateStyles } from "../styles/ReimbursementStyles";

type IRSPageProps = {
	onBack?: () => void;
};

const irsRates = [
	{ name: "Business", rate: "0.70" },
	{ name: "Charity", rate: "0.14" },
	{ name: "Medical moving", rate: "0.21" },
	{ name: "Military moving", rate: "0.21" },
	{ name: "Personal", rate: "0.00" },
];

export default function ViewIRSRatePage({ onBack }: IRSPageProps) {
	return (
		<SafeAreaView style={rateStyles.safe}>
			<View style={rateStyles.screenContainer}>
				<View style={rateStyles.headerRow}>
					<Pressable onPress={onBack}>
						<Text style={rateStyles.backArrow}>{"<"}</Text>
					</Pressable>
					<Text style={rateStyles.headerTitle}>IRS Standard Mileage Rate</Text>
				</View>

				<Text style={[rateStyles.paragraph, { marginTop: 12 }]}>
					Below is the IRS set standard mileage rate for US
				</Text>

				<Text
					style={{
						marginTop: 30,
						marginBottom: 8,
						fontSize: 14,
						fontWeight: "700",
						color: "#4F46E5",
					}}>
					RATES
				</Text>

				<View
					style={{
						backgroundColor: "white",
						borderRadius: 12,
						overflow: "hidden",
					}}>
					{irsRates.map((c, i) => (
						<View
							key={c.name}
							style={{
								flexDirection: "row",
								justifyContent: "space-between",
								paddingVertical: 14,
								paddingHorizontal: 18,
								borderBottomWidth: i < irsRates.length - 1 ? 1 : 0,
								borderColor: "#E5E7EB",
							}}>
							<Text style={{ fontSize: 16 }}>{c.name}</Text>
							<Text style={{ fontSize: 16 }}>${c.rate}</Text>
						</View>
					))}
				</View>
			</View>
		</SafeAreaView>
	);
}
