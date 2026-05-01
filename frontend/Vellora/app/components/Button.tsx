import { ActivityIndicator, Text, TouchableOpacity, TouchableOpacityProps } from 'react-native'
import React from 'react'

// typescript types for the expected props
type ButtonProps = TouchableOpacityProps & {
    title: string;
    className?: string;
    isLoading?: boolean;
}

const Button: React.FC<ButtonProps> = ({
    title,
    onPress,
    className,
    isLoading = false,
    disabled = false,
    ...props
}) => {

    const toggleDisabled = disabled || isLoading;

    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={toggleDisabled}
            className={`bg-accentGreen rounded-xl items-center disabled:opacity-50 ${className}`}
            {...props}
        >
            {isLoading ? (
                <ActivityIndicator color="#FFFFFF" />
            ) : (
                <Text className="text-textWhite text-base font-bold">
                    {title}
                </Text>
            )}



        </TouchableOpacity>
    )
}

export default Button
