import { View, Text, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Image } from "expo-image";
import { router } from "expo-router";

export default function OnboardingScreen2() {
	return (
		<SafeAreaView
			edges={["top"]}
			style={{
				flex: 1,
				backgroundColor: "#fff",
			}}>
			<View
				style={{
					flex: 1,
					backgroundColor: "#3F46D6",
				}}>
				<View
					style={{
						flex: 1,
					}}>
					<View
						style={{
							flex: 0.35,
							backgroundColor: "#fff",
							justifyContent: "center",
							alignItems: "center",
						}}>
						<Image
							source={require("./assets/Rectanges.png")}
							contentFit="contain"
							style={{
								width: 160,
								height: 160,
							}}
						/>
					</View>
					<View
						style={{
							flex: 0.65,
							backgroundColor: "#3F46D6",
							borderTopLeftRadius: 40,
							borderTopRightRadius: 40,
							paddingHorizontal: 24,
							justifyContent: "space-between",
							paddingBottom: 40,
						}}>
						<View
							style={{
								flex: 1,
								justifyContent: "center",
								alignItems: "center",
							}}>
							<Text
								style={{
									color: "#fff",
									fontSize: 22,
									fontWeight: "700",
									textAlign: "center",
									marginBottom: 12,
								}}>
								Easily count every mile{"\n"}you drive 🚗
							</Text>
							<Text
								style={{
									color: "#fff",
									fontSize: 16,
									fontWeight: "400",
									textAlign: "center",
									opacity: 0.9,
								}}>
								Don&apos;t miss a single mile with Velora&apos;s auto-tracking!
							</Text>
						</View>

						<View
							style={{
								alignItems: "center",
							}}>
							<View
								style={{
									flexDirection: "row",
									gap: 6,
									marginBottom: 30,
								}}>
								<View
									style={{
										width: 8,
										height: 8,
										borderRadius: 4,
										backgroundColor: "#fff",
										opacity: 0.3,
									}}
								/>
								<View
									style={{
										width: 8,
										height: 8,
										borderRadius: 4,
										backgroundColor: "#fff",
									}}
								/>
								<View
									style={{
										width: 8,
										height: 8,
										borderRadius: 4,
										backgroundColor: "#fff",
										opacity: 0.3,
									}}
								/>
							</View>

							<Pressable
								onPress={() => router.replace("/welcome" as any)}
								style={{
									width: "100%",
									paddingVertical: 14,
									backgroundColor: "#fff",
									borderRadius: 12,
								}}>
								<Text
									style={{
										color: "#3F46D6",
										textAlign: "center",
										fontSize: 16,
										fontWeight: "600",
									}}>
									Continue
								</Text>
							</Pressable>
						</View>
					</View>
				</View>
			</View>
		</SafeAreaView>
	);
}
