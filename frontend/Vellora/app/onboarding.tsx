import {
	View,
	Text,
	Pressable,
	FlatList,
	useWindowDimensions,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Image } from "expo-image";
import { router } from "expo-router";
import { useState, useRef } from "react";
import {
	onboardingStyles,
	getPageContainerStyle,
	getCurveOverlayStyle,
	getDotStyle,
} from "./styles/onboardingStyles";

interface OnboardingPage {
	id: number;
	image: any;
	title: string;
	subtitle: string;
}

const onboardingPages: OnboardingPage[] = [
	{
		id: 1,
		image: require("./assets/Notebook.png"),
		title: "Say goodbye to manual paper tracking 👋",
		subtitle: "No more noting down business miles by hand!",
	},
	{
		id: 2,
		image: require("./assets/Rectanges.png"),
		title: "Easily count every mile\nyou drive 🚗",
		subtitle: "Don't miss a single mile with Velora's auto-tracking!",
	},
];

function OnboardingPageItem({
	item,
	width,
}: {
	item: OnboardingPage;
	width: number;
}) {
	return (
		<View style={getPageContainerStyle(width)}>
			<View style={onboardingStyles.whiteSection}>
				<Image
					source={item.image}
					contentFit="contain"
					style={onboardingStyles.image}
				/>
			</View>
			<View style={onboardingStyles.blueSection}>
				<View style={getCurveOverlayStyle(width)} />
				<View style={onboardingStyles.textContainer}>
					<Text style={onboardingStyles.title}>{item.title}</Text>
					<Text style={onboardingStyles.subtitle}>{item.subtitle}</Text>
				</View>
			</View>
		</View>
	);
}

export default function OnboardingScreen() {
	const [currentIndex, setCurrentIndex] = useState(0);
	const flatListRef = useRef<FlatList>(null);
	const { width } = useWindowDimensions();

	const onViewableItemsChanged = useRef(({ viewableItems }: any) => {
		if (viewableItems.length > 0) {
			setCurrentIndex(viewableItems[0].index || 0);
		}
	}).current;

	const viewabilityConfig = useRef({
		itemVisiblePercentThreshold: 50,
	}).current;

	return (
		<SafeAreaView edges={["top"]} style={onboardingStyles.safeArea}>
			<View style={onboardingStyles.container}>
				<FlatList
					ref={flatListRef}
					data={onboardingPages}
					renderItem={({ item }) => (
						<OnboardingPageItem item={item} width={width} />
					)}
					keyExtractor={(item) => item.id.toString()}
					horizontal
					pagingEnabled
					showsHorizontalScrollIndicator={false}
					onViewableItemsChanged={onViewableItemsChanged}
					viewabilityConfig={viewabilityConfig}
					getItemLayout={(_, index) => ({
						length: width,
						offset: width * index,
						index,
					})}
				/>
				<View style={onboardingStyles.bottomContainer}>
					<View style={onboardingStyles.dotsContainer}>
						{onboardingPages.map((_, dotIndex) => (
							<View
								key={dotIndex}
								style={getDotStyle(currentIndex === dotIndex)}
							/>
						))}
					</View>

					<Pressable
						onPress={() => router.replace("/welcome" as any)}
						style={onboardingStyles.continueButton}>
						<Text style={onboardingStyles.continueButtonText}>Continue</Text>
					</Pressable>
				</View>
			</View>
		</SafeAreaView>
	);
}
