import { View, Image, Pressable, StyleSheet, Text } from 'react-native'
import React from 'react'
import { Tabs, router } from 'expo-router'
import { Colors } from '../Colors';
import { FontAwesome } from '@expo/vector-icons';

const _layout = () => {
  return (
    <View style={styles.container}>
      <View style={styles.mascotImageContainer}>
        <Image 
          source={require("../assets/veloWithHands.png")} 
          style={styles.mascotImage} 
          resizeMode="contain"
        />
      </View>
      
      <View style={styles.questionMarkContainer}>
        <FontAwesome name="question" size={14} color="#303DC9" />
      </View>
      
      <Pressable 
        style={styles.mascotClickableButton}
        onPress={() => router.push("/chatBot")}
      >
        <View />
      </Pressable>
      
      <Tabs
      screenOptions={{
        tabBarShowLabel: false, // Hide the labels

        // For the tabs background color
        tabBarStyle: {
          backgroundColor: '#404CCF',
          height: 80,
          borderTopWidth: 0, // remove top line
        },
      }}
    
    
    >
        <Tabs.Screen
            name='index'
            options={{
                title: 'Home', // home tab
                headerShown: false,
                tabBarIcon: ({ focused }) => ( // load icon
                  <TabIcon 
                    icon="home"
                    color={focused ? Colors.primaryPurple : Colors.textWhite} // change color when clicked
                    focused={focused}
                  />
                )
            }}
        />

        <Tabs.Screen
            name='history'
            options={{
                title: 'History', // history tab
                headerShown: false,
                tabBarIcon: ({ focused }) => ( // load icon
                  <TabIcon 
                    icon="history"
                    color={focused ? Colors.primaryPurple : Colors.textWhite} // change color when clicked
                    focused={focused}
                  />
                )
            }}
        />

        <Tabs.Screen   
            name='stats'
            options={{
                title: 'Statistics', // stats tab
                headerShown: false,
                tabBarIcon: ({ focused }) => ( // load icon
                  <TabIcon 
                    icon="bar-chart"
                    color={focused ? Colors.primaryPurple : Colors.textWhite} // change color when clicked
                    focused={focused}
                  />
                )
            }}
        />

        <Tabs.Screen 
            name='profile' 
            options={{
                title: 'Profile', // profile tab
                headerShown: false,
                tabBarIcon: ({ focused }) => ( // load icon
                  <TabIcon 
                    icon="user"
                    color={focused ? Colors.primaryPurple : Colors.textWhite} // change color when clicked
                    focused={focused}
                  />
                )
            }}
        />
        
    </Tabs>
    </View>
  )
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  mascotImageContainer: {
    position: "absolute",
    bottom: 13, 
    right: -47,
    zIndex: 1,
    width: 200,
    height: 200,
    justifyContent: "center",
    alignItems: "center",
    pointerEvents: "none",
  },
  questionMarkContainer: {
    position: "absolute",
    bottom: 145,
    right: 0,
    zIndex: 2,
    width: 20,
    height: 20,
    borderRadius: 10,
    transform: [{ rotate: "20deg" }],
  },
  mascotClickableButton: {
    position: "absolute",
    bottom: 83,
    right: 20,
    zIndex: 10,
    width: 65,
    height: 70,
    borderRadius: 10,
    //temp just to see clickable area
    //borderWidth: 2,
    //borderColor: "red", 
  },
  mascotImage: {
    width: 180,
    height: 180,
  },
});

// Helper reusable component for the tab icons
const TabIcon = ({ icon, color, focused }: { icon: any; color: string; focused: boolean }) => {
  return (

    // Return contained for the icon
    <View
      style={{
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: focused ? Colors.textWhite : 'transparent',
        marginTop: 30,
        height: 50,
        width: 50,
        borderRadius: 12,
      }}
    >
      <FontAwesome name={icon} size={28} color={color}/>


    </View>
  )
}

export default _layout