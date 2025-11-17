import React, { createContext, useContext, useState, ReactNode } from "react";
import { createManualTripPayload, createTripPayload } from "../services/Trips";

// storage box that holds all the trip information for later (start/stop) api calls
export interface TripData {
    // required by createTripPayload
    startAddress: string;
    purpose?: string | null;
    vechicle?: string | null;
    rateCustomizationid: string;
    rateCategoryId: string;

    // extra UI fields (not in API payload)
    parkingCost?: number;
    gasCost?: number;

    // fields needed for manual trips later
    endAddress?: string;
    miles?: number;
}

// type safety for typescript to shut up
// define the type of the context as well as all the functions it provides
interface TripContextType {
    tripData: TripData | null;                          // the data in the box itself
    setTripData: (data: TripData) => void;              // a function that lets you replace everything in the box at once
    clearTripData: () => void;                          // a function that lets you empty the box
    updateTripField: <K extends keyof TripData>(field: K, value: TripData[K]) => void;          // a function that lets you change a signle field (for example, purpose)

    // format data for LIVE TRIP CREATION API
    getCreateTripPayload: () => createTripPayload;              // format for API use

    // format data for MANUAL TRIP CREATION API
    getCreateManualTripPayload: () => createTripPayload;

    // validation
    isTripDataComplete: () => boolean;                          // check if required fields exist before POSTing
    isManualTripDataComplete: () => boolean;
}

// create the actual context. this is a box that doesn't store data yet. define what could be inside
const TripContext = createContext<TripContextType | undefined>(undefined);

// make a provider (a component that owns the box), so later we can use the context as <TripProvider> "component"
export const TripProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [tripData, setTripData] = useState<TripData | null>(null);

    // set all data at once
    const setTripDataHandler = (data: TripData) => {
        setTripData(data);
    };

    // empty the box
    const clearTripData = () => {
        setTripData(null);
    };

    // update one piece at a time
    const updateTripField = <K extends keyof TripData>(field: K, value: TripData[K]) => {
        
        setTripData(prev => {
            
            // if the trip alreadt exists, change just one property
            if (prev) {
                return { ...prev, [field]: value };
            } 
            // if the trip does not exist, create a minimal object so that fiel updates still work
            else {
                // create initial object with required fields as empty strings
                return {
                    [field]: value,
                    startAddress: "",
                    rateCustomizationid: "",
                    rateCategoryId: ""
                } as TripData;
            }
        });
    };

    // format data for the LIVE TRIP START api
    const getCreateTripPayload = (): createTripPayload => {
        if (!tripData || !isTripDataComplete()) {
            throw new Error('No trip data available');
        }

        return {
            startAddress: tripData.startAddress,
            purpose: tripData.purpose || null,
            vechicle: tripData.vechicle || null,
            rateCustomizationId: tripData.rateCustomizationid,
            rateCategoryId: tripData.rateCategoryId,
        };
    };

    // format data for the MANUAL TRIP LOG api
    const getCreateManualTripPayload = (): createManualTripPayload => {
        if (!tripData || !isManualTripDataComplete()) {
            throw new Error('Manual trip data incomplete');
        }

        return {
            startAddress: tripData.startAddress,
            endAddress: tripData.endAddress!,
            startedAt: new Date(),
            endedAt: new Date(),
            miles: tripData.miles!,
            geometry: null,
            rateCustomizationId: tripData.rateCustomizationid,
            rateCategoryId: tripData.rateCategoryId,
            expenses: []
        };
    }

    // check if all required data is present for live trips
    const isTripDataComplete = (): boolean => {
        return !!(
            // tripData?.startAddress &&
            tripData?.rateCustomizationid &&
            tripData?.rateCategoryId
        );
    };

    // check if amnual trip data is complete
    const isManualTripDataComplete = (): boolean => {
        return !!(
            tripData?.startAddress &&
            tripData?.endAddress &&
            tripData?.miles &&
            tripData?.rateCustomizationid &&
            tripData?.rateCategoryId
        );
    };

    return (

        // put everything into the provider. Becomes a real storage box for our app
        <TripContext.Provider value={{
            tripData,
            setTripData: setTripDataHandler,
            clearTripData,
            updateTripField,
            getCreateTripPayload,
            getCreateManualTripPayload,
            isTripDataComplete,
            isManualTripDataComplete,
        }}>
            {children}
        </TripContext.Provider>
    );
};

// for the sake of code cleanness, export a hook for easier context call
export const useTrip = (): TripContextType => {
    const context = useContext(TripContext);
    if (context === undefined) {
        throw new Error('useTrip must be used within a TripProvider');
    }
    return context;
};