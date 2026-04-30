import { StyleSheet, ViewStyle } from "react-native";

export const onboardingStyles = StyleSheet.create({
	safeArea: {
		flex: 1,
		backgroundColor: "#fff",
	},
	container: {
		flex: 1,
		backgroundColor: "#3F46D6",
	},
	whiteSection: {
		flex: 0.4,
		backgroundColor: "#fff",
		justifyContent: "flex-end",
		alignItems: "center",
		paddingBottom: 0,
	},
	image: {
		width: 160,
		height: 160,
	},
	blueSection: {
		flex: 0.6,
		backgroundColor: "#3F46D6",
		paddingHorizontal: 24,
		paddingTop: 50,
		paddingBottom: 120,
		overflow: "hidden",
	},
	textContainer: {
		flex: 1,
		justifyContent: "center",
		alignItems: "center",
	},
	title: {
		color: "#fff",
		fontSize: 22,
		fontWeight: "700",
		textAlign: "center",
		marginBottom: 12,
	},
	subtitle: {
		color: "#fff",
		fontSize: 16,
		fontWeight: "400",
		textAlign: "center",
		opacity: 0.9,
	},
	bottomContainer: {
		position: "absolute",
		bottom: 40,
		left: 0,
		right: 0,
		alignItems: "center",
		paddingHorizontal: 24,
	},
	dotsContainer: {
		flexDirection: "row",
		gap: 6,
		marginBottom: 30,
	},
	continueButton: {
		width: "100%",
		paddingVertical: 14,
		backgroundColor: "#fff",
		borderRadius: 12,
	},
	continueButtonText: {
		color: "#3F46D6",
		textAlign: "center",
		fontSize: 16,
		fontWeight: "600",
	},
});

export const getPageContainerStyle = (width: number): ViewStyle => ({
	width: width,
	flex: 1,
});

export const getCurveOverlayStyle = (width: number): ViewStyle => ({
	position: "absolute",
	top: -120,
	left: -width * 0.2,
	right: -width * 0.2,
	height: 240,
	backgroundColor: "#fff",
	borderRadius: 240,
});

export const getDotStyle = (isActive: boolean): ViewStyle => ({
	width: 8,
	height: 8,
	borderRadius: 4,
	backgroundColor: "#fff",
	opacity: isActive ? 1 : 0.3,
});
