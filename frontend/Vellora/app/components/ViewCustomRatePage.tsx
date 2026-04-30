import { View, Text, Pressable, SafeAreaView } from "react-native";
import { rateStyles } from "../styles/ReimbursementStyles";

type CustomRatePageProps = {
	onBack?: () => void;
};

const sampleCustomRate = {
	name: "Custom rate 1",
	description: "This is just a test custom rate",
	categories: [
		{ name: "Business", rate: "0.50" },
		{ name: "Charity", rate: "0.20" },
		{ name: "Personal", rate: "0.05" },
	],
};

export default function ViewCustomRatePage({ onBack }: CustomRatePageProps) {
	return (
		<SafeAreaView style={rateStyles.safe}>
			<View style={rateStyles.screenContainer}>
				<View style={rateStyles.headerRow}>
					<Pressable onPress={onBack}>
						<Text style={rateStyles.backArrow}>{"<"}</Text>
					</Pressable>
					<Text style={rateStyles.headerTitle}>{sampleCustomRate.name}</Text>
				</View>

				{sampleCustomRate.description ? (
					<Text style={[rateStyles.paragraph, { marginTop: 12 }]}>
						{sampleCustomRate.description}
					</Text>
				) : null}

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
					{sampleCustomRate.categories.map((c, i) => (
						<View
							key={c.name}
							style={{
								flexDirection: "row",
								justifyContent: "space-between",
								paddingVertical: 14,
								paddingHorizontal: 18,
								borderBottomWidth:
									i < sampleCustomRate.categories.length - 1 ? 1 : 0,
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
