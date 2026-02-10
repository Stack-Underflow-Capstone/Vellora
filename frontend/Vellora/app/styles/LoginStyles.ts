import { StyleSheet, Platform } from "react-native";

const BLUE = "#3F46D6";

export const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#fff",
  },
  container: {
    flex: 1,
    paddingHorizontal: 24,
    justifyContent: "center",
    ...Platform.select({
      web: {
        maxWidth: 400,
        width: "100%",
        alignSelf: "center",
      },
      default: {},
    }),
  },
  logoRow: {
    width: "100%",
    alignItems: "center",
    marginBottom: 32,
  },
  logoImage: {
    width: 220,
    height: 70,
    resizeMode: "contain",
  },
  fieldGroup: {
    marginTop: 16,
  },
  label: {
    color: BLUE,
    fontSize: 14,
    marginBottom: 10,
  },
  input: {
    height: 40,
    borderBottomWidth: 1,
    borderBottomColor: "#111",
    fontSize: 16,
  },
  ctaText: {
    color: BLUE,
    fontSize: 18,
    fontWeight: "700",
    borderWidth: 1,
    borderColor: "#3F46D6",
    borderRadius: 12,
    padding: 10,
  },
  secondaryButton: {
    marginTop: 16,
    height: 52,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: BLUE,
    alignItems: "center",
    justifyContent: "center",
  },
  secondaryButtonText: {
    color: BLUE,
    fontSize: 16,
    fontWeight: "600",
  },
  footerText: {
    marginTop: 18,
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
