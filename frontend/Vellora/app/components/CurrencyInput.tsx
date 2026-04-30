import { Text, View, TextInput } from 'react-native'
import React from 'react'

// typescript types for the expected props
type CurrencyInputProps = {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    className?: string;
    style?: any;
}
const CurrencyInput: React.FC<CurrencyInputProps> = ({
    label,
    value,
    onChangeText,
    className = ''
}) => {

    // handle changes while the user is typing
    // ensures numeric validity
    const handleTextChange = (text: string) => {

        // remove non digit characters
        const formattedText = text.replace(/[^0-9.]/g, '');

        // make sure there are no multiple deicmal points like 1.20.23
        const parts = formattedText.split('.');

        if (text === ''){
            onChangeText('');
            return;
        }

        if (parts.length > 2){
            onChangeText(value);
            return;
        }

        // accept only two decimal points
        if (parts[1] && parts[1].length > 2){
            onChangeText(value);
            return;
        }

        onChangeText(formattedText);
    };


    // apply formatting when the user is done typing
    const handleFormatting = () => {

        // automatically put 0 if the input is empty
        if (value === '' || value === '.' || value === '0'){
            onChangeText('0.00');
            return;
        }

        // parse to floating point and ensure its success
        const num = parseFloat(value);

        if (!isNaN(num)){
            onChangeText(num.toFixed(2));
        }
    };
    
    return (
        <View className={`${className}`}>
            <Text className='text-sm text-gray-500 mb-1'>{label}</Text>
            <View className={`flex-row py-3 px-2.5 items-center border border-gray-300 rounded-lg text-black bg-white`}>
                <Text className='text-base text-black font-bold w-5'>$</Text>
                <TextInput 
                    className="flex-1"
                    placeholderTextColor='gray'
                    placeholder="0.00"
                    editable
                    value={value}
                    onChangeText={handleTextChange}
                    onEndEditing={handleFormatting}
                    keyboardType="numeric"
                
                />
            </View>
        </View>
    )
}

export default CurrencyInput
