import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import React from 'react';
import { useState } from 'react';


interface filterButtonProps {
    label: string,
    count: number,
    isSelected: boolean | false
}



const FilterButton: React.FC<filterButtonProps> = ({ label, count, isSelected }) => {

    const [selected, setIsSelected] = useState<boolean>(isSelected);

    return (
        selected ? (
        <TouchableOpacity onPress={() => setIsSelected(false)}>
            <View style={styles.buttonContainerIsSelected}>
                <Text style={styles.textStyleIsSelected}>{label}</Text>
                <Text style={styles.textStyleIsSelected}>{count}</Text>
            </View>
        </TouchableOpacity>
        ) : (
            <TouchableOpacity onPress={() => setIsSelected(true)}>
            <View style={styles.buttonContainerNotSelected}>
                <Text style={styles.textStyleisNotSelected}>{label}</Text>
                <Text style={styles.textStyleisNotSelected}>{count}</Text>
            </View>
            </TouchableOpacity>
        )
    )
}


const styles = StyleSheet.create({
    buttonContainerNotSelected: {
        backgroundColor: '#c0c0c0',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 15,
        height: 25,
        width: 'auto',
        minWidth: 75,
        overflow: 'hidden',
        flexDirection: 'row',
        gap: 15
    },
    buttonContainerIsSelected: {
        backgroundColor: '#404CCF',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 15,
        height: 25,
        width: 'auto',
        minWidth: 75,
        overflow: 'hidden',
        flexDirection: 'row',
        gap: 15
    },

    textStyleisNotSelected: {
        fontSize: 15,
        fontWeight: 'bold',
    },
    textStyleIsSelected: {
        fontSize: 15,
        fontWeight: 'bold',
        color: 'white'
    }
})




export default FilterButton;