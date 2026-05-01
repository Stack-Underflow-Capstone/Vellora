import React, { useEffect, useMemo, useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";
import Entypo from "@expo/vector-icons/Entypo";

interface MonthYearDropdownProps {
  currentDate: Date;
  onDateChange: (date: Date) => void;
}

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

const MIN_YEAR = 2020;
const MAX_YEAR = 2050;

const MonthYearDropdown: React.FC<MonthYearDropdownProps> = ({
  currentDate,
  onDateChange,
}) => {
  const [show, setShow] = useState<boolean>(false);
  const [year, setYear] = useState<number>(currentDate.getFullYear());
  const [month, setMonth] = useState<number>(currentDate.getMonth());

  useEffect(() => {
    setYear(currentDate.getFullYear());
    setMonth(currentDate.getMonth());
  }, [currentDate]);

  const displayLabel = useMemo(
    () => new Date(year, month, 1).toLocaleDateString("en-us", { month: "long", year: "numeric" }),
    [month, year],
  );

  const updateDate = (nextYear: number, nextMonth: number) => {
    const totalMonths = nextYear * 12 + nextMonth;
    const minTotalMonths = MIN_YEAR * 12;
    const maxTotalMonths = MAX_YEAR * 12 + 11;
    const boundedMonths = Math.max(minTotalMonths, Math.min(maxTotalMonths, totalMonths));

    const normalizedYear = Math.floor(boundedMonths / 12);
    const normalizedMonth = boundedMonths % 12;

    setYear(normalizedYear);
    setMonth(normalizedMonth);
    onDateChange(new Date(normalizedYear, normalizedMonth, 1));
  };

  return (
    <View style={{ justifyContent: "center", alignItems: "center" }}>
      <TouchableOpacity onPress={() => setShow((prev) => !prev)} style={{ flexDirection: "row" }}>
        <Text className="text-xl font-bold text-primaryPurple text-center mr-2">{displayLabel}</Text>
        <Entypo name="chevron-down" size={24} color="#404CCF" />
      </TouchableOpacity>

      {show && (
        <View
          style={{
            marginTop: 10,
            width: "100%",
            maxWidth: 280,
            borderWidth: 1,
            borderColor: "#d4d4d8",
            borderRadius: 12,
            paddingHorizontal: 12,
            paddingVertical: 10,
            backgroundColor: "#ffffff",
            gap: 10,
          }}
        >
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <TouchableOpacity
              onPress={() => updateDate(year, month - 1)}
              disabled={year === MIN_YEAR && month === 0}
              style={{ opacity: year === MIN_YEAR && month === 0 ? 0.4 : 1 }}
            >
              <Entypo name="chevron-left" size={20} color="#404CCF" />
            </TouchableOpacity>
            <Text style={{ fontSize: 16, fontWeight: "700", color: "#27272a" }}>
              {MONTH_NAMES[month]} {year}
            </Text>
            <TouchableOpacity
              onPress={() => updateDate(year, month + 1)}
              disabled={year === MAX_YEAR && month === 11}
              style={{ opacity: year === MAX_YEAR && month === 11 ? 0.4 : 1 }}
            >
              <Entypo name="chevron-right" size={20} color="#404CCF" />
            </TouchableOpacity>
          </View>

          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
            <TouchableOpacity
              onPress={() => updateDate(year - 1, month)}
              disabled={year <= MIN_YEAR}
              style={{ opacity: year <= MIN_YEAR ? 0.4 : 1 }}
            >
              <Text style={{ fontSize: 14, fontWeight: "600", color: "#404CCF" }}>- Year</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => updateDate(year + 1, month)}
              disabled={year >= MAX_YEAR}
              style={{ opacity: year >= MAX_YEAR ? 0.4 : 1 }}
            >
              <Text style={{ fontSize: 14, fontWeight: "600", color: "#404CCF" }}>+ Year</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
};

export default MonthYearDropdown;
