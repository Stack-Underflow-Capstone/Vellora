import { Text, TouchableOpacity } from 'react-native'
import React from 'react'

type CommonPlaceCardProps = {
    title: string;
    address: string;
    onPress: () => void;
    className?: string;         // allow custom styles
}
const CommonPlaceCard: React.FC<CommonPlaceCardProps> = ({
    title,
    address,
    onPress,
    className = '',
}) => {

    return (
        <TouchableOpacity
            className={`bg-white w-[48%] rounded-xl shadow-sm p-6 mb-4 ${className}`}
            onPress={onPress}
            style={{ minHeight: 60,
                    shadowColor: '#000',
                    shadowOffset: { width: 0, height: 2 },
                    shadowOpacity: 0.08,
                    shadowRadius: 8,
                    elevation: 3,
             }}
        >
            <Text className='font-bold text-base mb-1 text-black' numberOfLines={1}>
                {title}
            </Text>

            <Text className='text-xs text-gray-500' numberOfLines={2}>
                {address}
            </Text>
        </TouchableOpacity>
    )
}

export default CommonPlaceCard
