import { View, Text, Pressable, SafeAreaView } from "react-native";
import { Image } from "expo-image";
import { router } from "expo-router";
import { welcomeStyles } from "./styles/welcomeStyles";

export default function WelcomeScreen() {
	return (
		<SafeAreaView style={welcomeStyles.safeArea}>
			<View style={welcomeStyles.container}>
				<View style={welcomeStyles.logoContainer}>
					<Image
						source={require("./assets/Vellora_Logo_Light.png")}
						contentFit="contain"
						style={welcomeStyles.logo}
					/>
					<Text style={welcomeStyles.tagline}>The Value of the Journey</Text>
				</View>
				<View style={welcomeStyles.buttonsContainer}>
					<Pressable
						onPress={() => router.push("/login" as any)}
						style={welcomeStyles.loginButton}>
						<Text style={welcomeStyles.loginButtonText}>Login</Text>
					</Pressable>
					<Pressable
						onPress={() => router.push("/pages/Register" as any)}
						style={welcomeStyles.registerButton}>
						<Text style={welcomeStyles.registerButtonText}>Register</Text>
					</Pressable>
				</View>
			</View>
		</SafeAreaView>
	);
}
