import React, { createContext, useContext, useState, ReactNode } from "react";

// storage box that holds all the trip information for later (start/stop) api calls
export interface TripData {
    startAddress?: string;
    purpose?: string;
    vehicle?: string;
    rateCustomizationid?: string;
    rateCategoryId?: string;
    parkingCost?: number;
    gasCost?: number;
}

// type safety for typescript to shut up
interface TripContextType {
    tripData: TripData | null;
    setTripData: (data: TripData) => void;
    clearTripData: () => void;
    updateTripField: <K extends keyof TripData>(field: K, value: TripData[K]) => void;
}

const TripContext = createContext<TripContextType | undefined>(undefined);

export const TripProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [tripData, setTripData] = useState<TripData | null>(null);

    const setTripDataHandler = (data: TripData) => {
        setTripData(data);
    };

    const clearTripData = () => {
        setTripData(null);
    };

    const updateTripField = <K extends keyof TripData>(field: K, value: TripData[K]) => {
        setTripData(prev => prev ? { ...prev, [field]: value } : { [field]: value } as TripData);
    };

    return (
        <TripContext.Provider value={{
            tripData,
            setTripData: setTripDataHandler,
            clearTripData,
            updateTripField,
        }}>
            {children}
        </TripContext.Provider>
    );
};

export const useTrip = (): TripContextType => {
    const context = useContext(TripContext);
    if (context === undefined) {
        throw new Error('useTrip must be used within a TripProvider');
    }
    return context;
};