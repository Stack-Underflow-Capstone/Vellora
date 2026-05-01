import { StyleSheet } from "react-native";

const BLUE = "#3F46D6";
const GREEN = "#22C55E";
const LIGHT_GRAY = "#F5F5F5";

export const rateStyles = StyleSheet.create({
	safe: {
		flex: 1,
		backgroundColor: LIGHT_GRAY,
	},
	screenContainer: {
		flex: 1,
		paddingTop: 24,
		paddingHorizontal: 24,
	},
	headerRow: {
		flexDirection: "row",
		alignItems: "center",
		marginBottom: 16,
	},
	headerBackHitbox: {
		width: 32,
		height: 32,
		borderRadius: 16,
		alignItems: "center",
		justifyContent: "center",
	},
	headerBackText: {
		fontSize: 20,
	},
	headerTitle: {
		flex: 1,
		textAlign: "center",
		fontSize: 18,
		fontWeight: "700",
		color: BLUE,
		marginRight: 32,
	},
	paragraph: {
		fontSize: 14,
		color: "#111",
		marginBottom: 24,
	},
	card: {
		backgroundColor: "#fff",
		borderRadius: 16,
		overflow: "hidden",
	},
	cardSectionHeader: {
		paddingHorizontal: 16,
		paddingVertical: 12,
	},
	sectionLabel: {
		fontSize: 12,
		fontWeight: "700",
		color: BLUE,
		letterSpacing: 0.5,
	},
	divider: {
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
	},
	rateRow: {
		flexDirection: "row",
		alignItems: "center",
		paddingHorizontal: 16,
		paddingVertical: 12,
	},
	rateRowText: {
		flex: 1,
		fontSize: 14,
		color: "#111",
	},
	rateRowPrice: {
		fontSize: 14,
		color: "#111",
	},
	rowChevron: {
		fontSize: 16,
		color: "#111",
	},
	addRow: {
		flexDirection: "row",
		alignItems: "center",
		paddingHorizontal: 16,
		paddingVertical: 12,
	},
	addIconCircle: {
		width: 16,
		height: 16,
		borderRadius: 8,
		backgroundColor: GREEN,
		alignItems: "center",
		justifyContent: "center",
		marginRight: 8,
	},
	addIconText: {
		color: "#fff",
		fontSize: 12,
		fontWeight: "700",
	},
	addText: {
		fontSize: 14,
		color: GREEN,
	},
	minusIcon: {
		width: 16,
		height: 2,
		borderRadius: 1,
		backgroundColor: "#EF4444",
		marginRight: 12,
	},
	categoryInput: {
		flex: 1,
		height: 44,
		backgroundColor: "#FFF",
		borderRadius: 8,
		paddingHorizontal: 10,
		borderWidth: 1,
		borderColor: "#D1D5DB",
		color: "#000",
	},
	fullScreenWhite: {
		flex: 1,
		backgroundColor: "#fff",
		paddingTop: 24,
		paddingHorizontal: 24,
	},
	formHeaderRow: {
		flexDirection: "row",
		alignItems: "center",
		marginBottom: 16,
	},
	closeCircle: {
		width: 32,
		height: 32,
		borderRadius: 16,
		borderWidth: 1,
		borderColor: "#E5E7EB",
		alignItems: "center",
		justifyContent: "center",
	},
	closeText: {
		fontSize: 18,
		color: BLUE,
	},
	formTitle: {
		flex: 1,
		textAlign: "center",
		fontSize: 18,
		fontWeight: "700",
		color: BLUE,
		marginRight: 32,
	},
	formFieldGroup: {
		marginTop: 18,
	},
	formLabel: {
		color: BLUE,
		fontSize: 14,
		marginBottom: 8,
	},
	formInput: {
		width: "100%",
		height: 44,
		backgroundColor: "#FFF",
		borderRadius: 10,
		paddingHorizontal: 12,
		borderWidth: 1,
		borderColor: "#D1D5DB", // light gray border
		color: "#000",
	},
	formHeadingRow: {
		marginTop: 24,
		marginBottom: 4,
	},
	formSaveButton: {
		marginTop: 32,
		height: 52,
		borderRadius: 24,
		backgroundColor: GREEN,
		alignItems: "center",
		justifyContent: "center",
	},
	formSaveText: {
		color: "#fff",
		fontSize: 16,
		fontWeight: "700",
	},
	listItem: {
		fontSize: 16,
		paddingVertical: 12,
		paddingHorizontal: 8,
		borderBottomWidth: 1,
		borderBottomColor: "#e5e5e5",
	},
	addCustom: {
		fontSize: 16,
		fontWeight: "500",
		color: "#4CAF50",
		paddingVertical: 12,
		paddingHorizontal: 10,
	},
	backArrow: {
		fontSize: 22,
		fontWeight: "600",
		color: "#4F46E5",
		paddingRight: 12,
	},
	modalOverlay: {
		flex: 1,
		backgroundColor: "rgba(0,0,0,0.4)",
		justifyContent: "center",
		alignItems: "center",
	},
	modalCard: {
		width: "80%",
		backgroundColor: "white",
		borderRadius: 16,
		paddingVertical: 16,
		paddingHorizontal: 12,
	},
	modalTitle: {
		fontSize: 16,
		fontWeight: "700",
		textAlign: "center",
		marginBottom: 12,
	},
	modalItem: {
		paddingVertical: 12,
		paddingHorizontal: 12,
		borderBottomWidth: 1,
		borderBottomColor: "#E5E7EB",
	},
});
