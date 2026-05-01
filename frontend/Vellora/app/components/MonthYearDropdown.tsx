import React, { useState, useCallback, useEffect } from "react";
import { View, Text, TouchableOpacity, Button } from 'react-native';
import MonthPicker from 'react-native-month-year-picker';
import Entypo from '@expo/vector-icons/Entypo';

interface MonthYearDropdownProps {
  currentDate: Date
  onDateChange: (date: Date) => void;
}



const MonthYearDropdown: React.FC<MonthYearDropdownProps> = ({ currentDate, onDateChange }) => {
    const [date, setDate] = useState<Date>(currentDate);
    const [show, setShow] = useState<boolean>(false);

    useEffect(() => {
      setDate(currentDate);
    }, [currentDate]);
    
    const showPicker = useCallback((value: boolean | ((prevState: boolean) => boolean)) => setShow(value), []);

    const onValueChange = useCallback((event: any, newDate: Date) => {
      const selectedDate = newDate || date;
      setDate(selectedDate);
      onDateChange(selectedDate);
      setShow(false);
    },
    [date, showPicker, onDateChange],
  );

  return (
    <View style={{justifyContent: 'center', alignItems: 'center'}}>
        <TouchableOpacity onPress={() => showPicker(true)} style={{ flexDirection: "row"}}>
            <Text className='text-xl font-bold text-primaryPurple text-center mr-2'>{date.toLocaleDateString('en-us', { month: 'long', year: 'numeric'})}</Text>
            <Entypo name='chevron-down' size={24} color='#404CCF' /> 
        </TouchableOpacity>
        { show && (
          <View style={{ width: "100%", alignItems: "center", height: 300, paddingBottom: 52 }}>
            <MonthPicker
            onChange={onValueChange}
            value={date}
            minimumDate={new Date(2020, 0)}
            maximumDate={new Date(2050, 11)} />
          </View>
        )}
    </View>
  )


}

export default MonthYearDropdown;