import { View } from "react-native";
import React from "react";
import { Tabs } from "expo-router";
import { Colors } from "../Colors";
import { FontAwesome } from "@expo/vector-icons";

const _layout = () => {
	return (
		<Tabs
			screenOptions={{
				tabBarShowLabel: false,
				tabBarStyle: {
					backgroundColor: "#404CCF",
					height: 80,
					borderTopWidth: 0,
				},
			}}>
			<Tabs.Screen
				name="index"
				options={{
					title: "Home",
					headerShown: false,
					href: null,
					tabBarIcon: ({ focused }) => (
						<TabIcon
							icon="home"
							color={focused ? Colors.primaryPurple : Colors.textWhite}
							focused={focused}
						/>
					),
				}}
			/>

			<Tabs.Screen
				name="history"
				options={{
					title: "History",
					headerShown: false,
					tabBarIcon: ({ focused }) => (
						<TabIcon
							icon="history"
							color={focused ? Colors.primaryPurple : Colors.textWhite}
							focused={focused}
						/>
					),
				}}
			/>

			<Tabs.Screen
				name="stats"
				options={{
					title: "Statistics",
					headerShown: false,
					tabBarIcon: ({ focused }) => (
						<TabIcon
							icon="bar-chart"
							color={focused ? Colors.primaryPurple : Colors.textWhite}
							focused={focused}
						/>
					),
				}}
			/>

			<Tabs.Screen
				name="profile"
				options={{
					title: "Profile",
					headerShown: false,
					href: null,
					tabBarIcon: ({ focused }) => (
						<TabIcon
							icon="user"
							color={focused ? Colors.primaryPurple : Colors.textWhite}
							focused={focused}
						/>
					),
				}}
			/>
		</Tabs>
	);
};

const TabIcon = ({
	icon,
	color,
	focused,
}: {
	icon: any;
	color: string;
	focused: boolean;
}) => {
	return (
		<View
			style={{
				alignItems: "center",
				justifyContent: "center",
				backgroundColor: focused ? Colors.textWhite : "transparent",
				marginTop: 30,
				height: 50,
				width: 50,
				borderRadius: 12,
			}}>
			<FontAwesome name={icon} size={28} color={color} />
		</View>
	);
};

export default _layout;
