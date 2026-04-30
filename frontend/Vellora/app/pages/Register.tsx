import { useState } from "react";
import {
	View,
	Text,
	TextInput,
	Pressable,
	KeyboardAvoidingView,
	Platform,
	Image,
	ActivityIndicator,
} from "react-native";
import { styles } from "../styles/RegisterStyles";
import { router } from "expo-router";
import { register } from "../services/auth";
import { tokenStorage } from "../services/tokenStorage";

export default function RegisterPage() {
	const [first, setFirst] = useState("");
	const [last, setLast] = useState("");
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");

	const [emailError, setEmailError] = useState("");
	const [passwordError, setPasswordError] = useState("");
	const [loading, setLoading] = useState(false);
	const [message, setMessage] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const validateEmail = (text: string) => {
		setEmail(text);
		const emailRegex = /\S+@\S+\.\S+/;
		if (!emailRegex.test(text))
			setEmailError("Please enter a valid email address.");
		else setEmailError("");
	};

	const validatePassword = (text: string) => {
		setPassword(text);
		if (text.length < 8)
			setPasswordError("Password must be at least 8 characters.");
		else setPasswordError("");
	};

	const isFormValid =
		first.trim() &&
		last.trim() &&
		email.length > 0 &&
		password.length > 0 &&
		emailError === "" &&
		passwordError === "";

	const handleRegister = async () => {
		if (!isFormValid) {
			setError("Please fill in all fields correctly.");
			return;
		}

		setLoading(true);
		setError(null);
		setMessage(null);

		try {
			const fullName = `${first.trim()} ${last.trim()}`.trim();
			const response = await register({
				email: email.trim(),
				password: password,
				full_name: fullName || undefined,
			});

			tokenStorage.setToken(response.tokens.access_token);

			setMessage(
				`Account created successfully! Welcome ${
					response.user.full_name ?? response.user.email
				}!`
			);

			setTimeout(() => {
				router.push("/login" as any);
			}, 1500);
		} catch (err) {
			setError(
				err instanceof Error
					? err.message
					: "Registration failed. Please try again."
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<KeyboardAvoidingView
			style={styles.safe}
			behavior={Platform.OS === "ios" ? "padding" : undefined}>
			<View style={styles.container}>
				<View style={styles.logoRow}>
					<Image
						source={require("../assets/Vellora_Dark_Logo.png")}
						style={styles.logo}
						resizeMode="contain"
					/>
				</View>

				<View style={styles.fieldGroup}>
					<Text style={styles.label}>First Name</Text>
					<TextInput
						style={styles.input}
						placeholder="Enter First Name"
						placeholderTextColor="#9CA3AF"
						value={first}
						onChangeText={setFirst}
					/>
				</View>

				<View style={styles.fieldGroup}>
					<Text style={styles.label}>Last Name</Text>
					<TextInput
						style={styles.input}
						placeholder="Enter Last Name"
						placeholderTextColor="#9CA3AF"
						value={last}
						onChangeText={setLast}
					/>
				</View>

				<View style={styles.fieldGroup}>
					<Text style={styles.label}>Email Address</Text>
					<TextInput
						style={styles.input}
						placeholder="Enter Email"
						placeholderTextColor="#9CA3AF"
						autoCapitalize="none"
						keyboardType="email-address"
						value={email}
						onChangeText={validateEmail}
					/>
					{emailError ? (
						<Text style={{ color: "red", marginTop: 4 }}>{emailError}</Text>
					) : null}
				</View>

				<View style={styles.fieldGroup}>
					<Text style={styles.label}>Password</Text>
					<TextInput
						style={styles.input}
						placeholder="Enter Password"
						placeholderTextColor="#9CA3AF"
						secureTextEntry
						value={password}
						onChangeText={validatePassword}
					/>
					{passwordError ? (
						<Text style={{ color: "red", marginTop: 4 }}>{passwordError}</Text>
					) : null}
				</View>

				{error && (
					<Text
						style={[styles.message, styles.messageError, { marginTop: 16 }]}>
						{error}
					</Text>
				)}
				{message && (
					<Text
						style={[styles.message, styles.messageSuccess, { marginTop: 16 }]}>
						{message}
					</Text>
				)}

				<Pressable
					style={[
						styles.ctaButton,
						{ opacity: isFormValid && !loading ? 1 : 0.4 },
					]}
					disabled={!isFormValid || loading}
					onPress={handleRegister}>
					{loading ? (
						<ActivityIndicator color="#3F46D6" />
					) : (
						<Text style={styles.ctaButtonText}>Continue</Text>
					)}
				</Pressable>

				<Text style={styles.footerText}>
					Already have an account?{" "}
					<Text
						style={styles.link}
						onPress={() => router.push("/login" as any)}>
						Log in
					</Text>
				</Text>
			</View>
		</KeyboardAvoidingView>
	);
}
