import { Stack } from "expo-router";
import './globals.css';
import { TripProvider } from './contexts/TripContext';

export default function RootLayout() {
  return (
    <TripProvider>  {/* trip context wrapper */}
      <Stack>
        <Stack.Screen 
          name="(tabs)"
          options={{ headerShown: false}}
        />
      </Stack>
    </TripProvider>
  );
}