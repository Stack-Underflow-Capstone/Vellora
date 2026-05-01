import { StyleSheet } from "react-native";

const BLUE = "#3F46D6";

export const styles = StyleSheet.create({
	safe: {
		flex: 1,
		backgroundColor: "#fff",
	},
	container: {
		flex: 1,
		paddingHorizontal: 24,
		paddingTop: 80,
	},
	logoRow: {
		alignItems: "center",
		justifyContent: "center",
		marginBottom: 40,
	},
	logo: {
		width: 200,
		height: 64,
	},
	fieldGroup: {
		marginTop: 20,
	},
	label: {
		color: BLUE,
		fontSize: 14,
		marginBottom: 8,
	},
	input: {
		height: 44,
		borderBottomWidth: 1,
		borderBottomColor: "#111",
		fontSize: 16,
	},
	ctaButton: {
		marginTop: 36,
		height: 52,
		borderRadius: 12,
		borderWidth: 1,
		borderColor: BLUE,
		alignItems: "center",
		justifyContent: "center",
	},
	ctaButtonText: {
		color: BLUE,
		fontSize: 18,
		fontWeight: "700",
	},
	footerText: {
		marginTop: 16,
		textAlign: "center",
		color: "#111",
	},
	link: {
		color: BLUE,
		fontWeight: "700",
	},
	message: {
		marginTop: 16,
		fontSize: 14,
	},
	messageError: {
		color: "#dc2626",
	},
	messageSuccess: {
		color: "#16a34a",
	},
});
