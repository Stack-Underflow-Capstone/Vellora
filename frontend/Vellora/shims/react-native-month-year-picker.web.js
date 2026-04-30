import React from 'react';
import { Text, View } from 'react-native';

export default function MonthPickerFallback() {
  return (
    <View style={{ padding: 8 }}>
      <Text style={{ fontSize: 12, color: '#71717a' }}>
        Month picker is not supported on web.
      </Text>
    </View>
  );
}
