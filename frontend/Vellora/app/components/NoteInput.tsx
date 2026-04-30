import React from 'react';
import { TextInput, TextInputProps } from 'react-native';

// define prop types by extending the standard textinputprops
type NoteInputProps = TextInputProps & {
    className?: string;
    multiline?: boolean;
}

// this component is made for note inputs that are either multiline or single line
const NoteInput: React.FC<NoteInputProps> = ({ 
    className = '',
    multiline = false,
    ...props 
}) => {

    const multilineStyle = multiline ? 'h-24 pr-8' : '';

    return (
        <TextInput
            // add base styles through classname. Append other passed classNames
            className={`text-base py-3 px-2.5 border border-gray-300 rounded-lg text-black bg-white ${multilineStyle} ${className}`}
            
            multiline={multiline}
            textAlignVertical={multiline ? 'top' : 'auto'}
            placeholderTextColor='gray'
            {...props}                  // pass all other props
        />
    );
};

export default NoteInput;
