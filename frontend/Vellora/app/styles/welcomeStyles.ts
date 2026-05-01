import { StyleSheet } from "react-native";

export const welcomeStyles = StyleSheet.create({
	safeArea: {
		flex: 1,
		backgroundColor: "#3F46D6",
		padding: 20,
	},
	container: {
		flex: 1,
		alignItems: "center",
		paddingTop: 200,
	},
	logoContainer: {
		alignItems: "center",
	},
	logo: {
		width: 220,
		height: 70,
		marginBottom: 4,
	},
	tagline: {
		color: "#fff",
		fontSize: 14,
		fontWeight: "400",
	},
	buttonsContainer: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
		width: "100%",
	},
	loginButton: {
		width: "90%",
		paddingVertical: 12,
		backgroundColor: "#3F46D6",
		borderRadius: 12,
		borderWidth: 2,
		borderColor: "#fff",
	},
	loginButtonText: {
		color: "#fff",
		textAlign: "center",
		fontSize: 16,
		fontWeight: "600",
	},
	registerButton: {
		width: "90%",
		paddingVertical: 12,
		backgroundColor: "#fff",
		borderRadius: 12,
		borderWidth: 2,
		borderColor: "#fff",
		marginTop: 16,
	},
	registerButtonText: {
		color: "#3F46D6",
		textAlign: "center",
		fontSize: 16,
		fontWeight: "600",
	},
});
