import { StyleSheet } from "react-native";
import { Colors } from "../Colors";

export const reportPageStyles = StyleSheet.create({
	headerContainer: {
		backgroundColor: "white",
		paddingHorizontal: 24,
		paddingTop: 48,
		paddingBottom: 16,
		flexDirection: "row",
		alignItems: "center",
		justifyContent: "space-between",
		borderBottomWidth: 1,
		borderBottomColor: "#E5E7EB",
	},
	backArrow: {
		fontSize: 24,
		fontWeight: "600",
		color: Colors.primaryPurple,
		padding: 8,
	},
	headerTitle: {
		fontSize: 20,
		fontWeight: "700",
		color: Colors.primaryPurple,
		flex: 1,
		textAlign: "center",
	},
	refreshButton: {
		backgroundColor: Colors.accentGreen,
		paddingHorizontal: 16,
		paddingVertical: 8,
		borderRadius: 8,
	},
	refreshButtonText: {
		color: Colors.textWhite,
		fontWeight: "600",
		fontSize: 14,
	},
	tableHeader: {
		backgroundColor: "white",
		paddingHorizontal: 24,
		paddingVertical: 12,
		flexDirection: "row",
		borderBottomWidth: 1,
		borderBottomColor: "#E5E7EB",
	},
	tableHeaderText: {
		fontSize: 14,
		fontWeight: "600",
		color: Colors.primaryPurple,
	},
	tableRow: {
		backgroundColor: "white",
		paddingHorizontal: 24,
		paddingVertical: 16,
		flexDirection: "row",
		alignItems: "center",
		borderBottomWidth: 1,
		borderBottomColor: "#E5E7EB",
	},
	tableCell: {
		flex: 1,
	},
	tableCellText: {
		fontSize: 14,
		color: Colors.textBlack,
	},
	statusCompleted: {
		color: Colors.accentGreen,
	},
	statusFailed: {
		color: "#EF4444",
	},
	statusExpired: {
		color: "#6B7280",
	},
	statusProcessing: {
		color: "#3B82F6",
	},
	actionText: {
		fontSize: 14,
		textDecorationLine: "underline",
		color: Colors.primaryPurple,
	},
	actionTextDisabled: {
		fontSize: 14,
		textDecorationLine: "underline",
		color: "#9CA3AF",
	},
	loadingContainer: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
	},
	loadingText: {
		color: "#6B7280",
	},
	errorContainer: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
		paddingHorizontal: 24,
	},
	errorText: {
		color: "#EF4444",
		textAlign: "center",
		marginBottom: 16,
	},
	retryText: {
		color: Colors.primaryPurple,
		textDecorationLine: "underline",
	},
	emptyContainer: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
		paddingVertical: 32,
	},
	emptyText: {
		color: "#6B7280",
		textAlign: "center",
	},
	generatingContainer: {
		flex: 1,
		paddingHorizontal: 24,
		paddingTop: 24,
		justifyContent: "center",
		alignItems: "center",
	},
	generatingTitle: {
		fontSize: 30,
		fontWeight: "700",
		color: Colors.textBlack,
		marginBottom: 32,
	},
	progressBarContainer: {
		width: "100%",
		marginBottom: 16,
	},
	progressBarBackground: {
		width: "100%",
		height: 12,
		backgroundColor: Colors.backgroundGrey,
		borderRadius: 9999,
		overflow: "hidden",
	},
	progressBarFill: {
		height: "100%",
		borderRadius: 9999,
	},
	statusLabelsContainer: {
		flexDirection: "row",
		justifyContent: "space-between",
		width: "100%",
		marginBottom: 8,
	},
	statusLabel: {
		fontSize: 14,
		fontWeight: "600",
	},
	statusLabelActive: {
		color: Colors.primaryPurple,
	},
	statusLabelInactive: {
		color: "#9CA3AF",
	},
	statusLabelCompleted: {
		color: Colors.accentGreen,
	},
	statusText: {
		fontSize: 16,
		color: "#6B7280",
		marginTop: 16,
	},
	errorMessage: {
		color: "#EF4444",
		marginBottom: 16,
		textAlign: "center",
	},
});

export const getStatusColor = (status: string): string => {
	switch (status) {
		case "pending":
			return "#F59E0B";
		case "processing":
			return "#3B82F6";
		case "completed":
			return Colors.accentGreen;
		case "failed":
			return "#EF4444";
		case "expired":
			return "#6B7280";
		default:
			return "#6B7280";
	}
};

export const getStatusTextColor = (status: string): string => {
	switch (status) {
		case "completed":
			return Colors.accentGreen;
		case "failed":
			return "#EF4444";
		case "expired":
			return "#6B7280";
		case "pending":
		case "processing":
			return "#3B82F6";
		default:
			return Colors.textBlack;
	}
};

export const getProgressPercent = (status: string): number => {
	switch (status) {
		case "pending":
			return 20;
		case "processing":
			return 60;
		case "completed":
			return 100;
		case "failed":
			return 0;
		case "expired":
			return 0;
		default:
			return 0;
	}
};
