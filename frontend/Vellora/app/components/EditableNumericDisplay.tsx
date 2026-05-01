import { Text, View, TextInput, TouchableOpacity, KeyboardTypeOptions } from 'react-native'
import React, {useState} from 'react'
import { FontAwesome } from '@expo/vector-icons'

// typescript types for the expected props
type Props = {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    unit: '$' | 'mi';
}
const EditableNumericDisplay: React.FC<Props> = ({ label, value, onChangeText, unit }) => {
    const [isEditing, setIsEditing] = useState(false);      // tracks whether the component is in display or edit mode

    let keyboardType: KeyboardTypeOptions = 'numeric';      // keyboard shows only numbers
    let prefix = '';    // text to show before the value (like "$" in "$5")
    let suffix = '';    // text to show after the value (like " mi" in "5 mi")

    // if the unit is currency, allow decimals and add the correct prefix
    keyboardType = 'decimal-pad';

    if (unit === '$'){
        prefix = '$';
    }

    // if the unit is miles, add the right suffix
    else {
        suffix = ' mi';
    }

    const handleTextChange = (text: string) => {
        let formattedText = text;

        // allow only digits and decimal points
        formattedText = text.replace(/[^0-9.]/g, '');

        // ensure there are no multiple decimal points like 1.20.23
        const parts = formattedText.split('.');

        if (parts.length > 2){
            onChangeText(value);
            return;
        }

        if (parts.length === 2 && parts[1].length > 2) {
            formattedText = parts[0] + ',' + parts[1].slice(0, 2);
        }

        onChangeText(formattedText);
    };

    // format the final value when a user taps away. Switch to display mode
    const handleBlur = () => {
        setIsEditing(false);    // exit editing

        if (value){
            let num = parseFloat(value);

            if (isNaN(num)){
                num = 0;
            }
            onChangeText(num.toFixed(2));
        } else {
            onChangeText('0.00');
        }
    };

    const getDisplayValue = () => {
        if (!value) return '0.00';

        const num = parseFloat(value);
        if (isNaN(num)) return '0.00';

        return num.toFixed(2);
    }

    return (
        <View className='flex-row items-center gap-2'>

            {/* if we are in edit mode, display textinput for editing */}
            {isEditing ? (
                <View className='flex-row items-baseline border-b border-gray-300'>
                    <Text className='text-xl'>{label} : {prefix}</Text>
                    <TextInput 
                        value={value}
                        onChangeText={handleTextChange}
                        keyboardType={keyboardType}
                        onBlur={handleBlur}
                        autoFocus={true}
                        className='text-xl font-bold py-0 px-1 w-24'
                    />
                    <Text className='text-xl font-bold'>{suffix}</Text>
                </View>
            ) : (
                // if we are in display mode, just show plain text
                <View className='flex-row items-center gap-2'>
                    <Text className='text-xl'>{label}: {' '}
                        <Text className='font-bold'>{prefix}{getDisplayValue()}{suffix}</Text>
                    </Text>
                    <TouchableOpacity onPress={() => setIsEditing(true)}>

                        <FontAwesome name='pencil' size={18} color="#6B7280"></FontAwesome>
                    </TouchableOpacity>
                </View>

            )}
        </View>
    )
}

export default EditableNumericDisplay
