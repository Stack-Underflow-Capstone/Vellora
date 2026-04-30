const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");
const path = require("path");

const config = getDefaultConfig(__dirname);

const defaultResolveRequest = config.resolver.resolveRequest;
config.resolver.resolveRequest = (context, moduleName, platform) => {
	if (platform === "web" && moduleName === "react-native-month-year-picker") {
		return {
			filePath: path.resolve(__dirname, "shims/react-native-month-year-picker.web.js"),
			type: "sourceFile",
		};
	}

	if (defaultResolveRequest) {
		return defaultResolveRequest(context, moduleName, platform);
	}

	return context.resolveRequest(context, moduleName, platform);
};

module.exports = withNativeWind(config, { input: "./app/globals.css" });