import { StyleSheet } from "react-native";

export const reportStyles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#F6F6F6",
	},
	content: {
		padding: 20,
	},
	title: {
		fontSize: 28,
		fontWeight: "700",
		color: "#4F46E5",
		marginBottom: 20,
	},
	sectionLabel: {
		color: "#4F46E5",
		fontSize: 14,
		fontWeight: "600",
		marginBottom: 12,
	},
	card: {
		backgroundColor: "white",
		padding: 20,
		borderRadius: 16,
		shadowColor: "#000",
		shadowOpacity: 0.08,
		shadowRadius: 6,
		shadowOffset: { width: 0, height: 2 },
		elevation: 2,
	},
	inputLabel: {
		fontSize: 14,
		fontWeight: "500",
		color: "#333",
		marginBottom: 8,
	},
	inputBox: {
		flexDirection: "row",
		alignItems: "center",
		borderColor: "#E5E7EB",
		borderWidth: 1,
		borderRadius: 10,
		padding: 12,
		backgroundColor: "white",
	},
	inputText: {
		fontSize: 15,
		color: "#333",
	},
	historyButton: {
		backgroundColor: "white",
		borderRadius: 16,
		padding: 16,
		marginTop: 12,
		shadowColor: "#000",
		shadowOpacity: 0.08,
		shadowRadius: 4,
		shadowOffset: { width: 0, height: 2 },
		elevation: 1,
	},
	historyText: {
		fontSize: 16,
		color: "#111",
	},
});
