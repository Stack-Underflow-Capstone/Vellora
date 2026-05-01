import { StyleSheet, View } from 'react-native'
import React from 'react'
import RNPickerSelect from 'react-native-picker-select'
import { FontAwesome } from '@expo/vector-icons';

// define TypeScript types for the component props
type DropdownProps = {
  items?: {label: string, value: string | number}[];      // list of options
  onValueChange: (value: string | null) => void;          // callback when a value is selected
  placeholder?: string;                                  //placeholder text
  value: string | number | null;                         // selected option
  icon?: React.ReactNode;                                // optional icon that is displayed on the left
  className?: string;                                    // optional classname for tailwind styling
}

// define dropdown functional component
const Dropdown: React.FC<DropdownProps> = ({
  items = [], 
  onValueChange, 
  placeholder = "Select an option", // default prompt 
  value, 
  icon,
  className = ''
}) => {

  // conditionally add margin if an icon exists
  const dynamicPickerStyles = {
    ...pickerSelectStyles,                        // apply base styles

    // if an icon exists, add 10 marginLeft
    inputIOS: [
      pickerSelectStyles.inputIOS,
      icon ? { marginLeft: 10 } : {},
    ],
    inputAndroid: [
      pickerSelectStyles.inputAndroid,
      icon ? { marginLeft: 10 } : {},
    ],

  }
  return (
    // align the icon and picker horizontally in the main wrapper view Tailwind class
    <View className="flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3">

      {/* apply fixed width and centering to icon wrapper*/}
      <View className='w-6 items-center'>
        {icon}
      </View>

      {/* picker component */}
      <RNPickerSelect 
        onValueChange={onValueChange}                                                 // selection callback prop
        items = {items}                                                               // displayed options
        value={value}                                                                 // selected value
        placeholder={placeholder ? { label: placeholder, value: null } : {}}          // placeholder
        style={dynamicPickerStyles}                                                   // apply dynamic styles

        // style the options in the iOS picker wheel
        pickerProps={{
          itemStyle: {
            color: 'black',
          }
        }}

        // add the chevron icon
        Icon={() => {
          return <FontAwesome name="chevron-down" size={12}/>
        }}

      />      
    </View>
  )
}

// define base styles for the picker
const pickerSelectStyles = StyleSheet.create({

  // applies styles to the picker's main wrapper
  viewContainer: {
    flex: 1,        // stretch to fill the space in a row
  },

  // applies input box styles for iOS
  inputIOS: {
    fontSize: 16,
    borderRadius: 8,
    color: 'black',
    backgroundColor: 'white',
    paddingRight: 30, // to ensure the text is never behind the icon
    flex: 1,          // stretch the text input
  },

  // applies input box styles for Android
  inputAndroid: {
    fontSize: 16,
    borderRadius: 8,
    color: 'black',
    backgroundColor: 'white',
    paddingRight: 30, // to ensure the text is never behind the icon
    flex: 1,          // stretch the text input
  },

  // applies placeholder style
  placeholder: {
    color: 'gray',
  },

  // applies styles for the wrapper <View> of the chevron icon
  iconContainer: {
    top: '50%',           // center
    marginTop: -6,
    right: 15,            // 15 px from the right edge
  },

  // applies iOS-specific container styles
  inputIOSContainer: {
    zIndex: 100,        // forces the options wheel to pop up
  },

});

export default Dropdown

