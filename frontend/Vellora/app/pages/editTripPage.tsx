import { View, Text } from "react-native";
import { useRouter, useLocalSearchParams } from 'expo-router';
import { getTrip, Trip, getTripExpenses, updateTripExpense, editTrip, Expense, createTripExpense, addReceipt, getReceipts, expenseReceipt } from "../services/Trips";
import TripDetailsForm from "../components/TripDetailsForm";
import { useRateOptions } from "../hooks/useRateOptions";
import GeometryMap from "../components/GeometryMap";
import ScreenLayout from "../components/ScreenLayout";
import { useState, useEffect } from "react";
import EditableNumericDisplay from "../components/EditableNumericDisplay";
import Button from "../components/Button";
import * as ImagePicker from 'expo-image-picker';
import { useCommonPlaces } from "../hooks/useCommonPlaces";
import * as FileSystem from 'expo-file-system/legacy';
import * as MediaLibrary from "expo-media-library";
import React from 'react';

import { useVehicles } from "../hooks/useVehicles";
const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;


const EditTripPage = () => {
    const router = useRouter();
    const { id } = useLocalSearchParams();

    // default states before trip is loaded
    const [trip, setTrip] = useState<Trip | null>(null);
    const [expenses, setExpenses] = useState<Expense[] | null>(null);
    const [isTripLoading, setTripLoading] = useState<boolean>(false);
    const [isExpenseLoading, setExpenseLoading] = useState<boolean>(false);
    const [notes, setNotes] = useState<string>('')
    const [vehicle, setVehicle] = useState<string | null>('');
    const [tripValue, setTripValue] = useState<number | null>(0.00);
    const [rate, setRate] = useState<string | null>('');
    const [type, setType] = useState<string | null>('');
    const [parking, setParking] = useState<string>('0.00');
    const [tolls, setTolls] = useState<string>('0.00')
    const [gas, setGas] = useState<string>('0.00')
    const [tripDistance, setTripDistance] = useState<number>(0)
    const [startAddress, setStartAddress] = useState<string>('');
    const [endAddress, setEndAddress] = useState<string>('');
    const [tripGeometry, setTripGeometry] = useState<object | null>(null);
    const [tripDate, setTripDate] = useState<string | undefined>('');
    const [error, setError] = useState<string | null>(null);
    const [image, setImage] = useState<string | null>(null);
    const [imageName, setImageName] = useState<string | null>(null);
    const [receipt, setReceipt] = useState<expenseReceipt[] | null>(null);
    const [isReceiptLoading, setIsReceiptLoading] = useState<boolean>(false);

    const { rateItems, categoryItems, loading, updateSelectedRate, rates } = useRateOptions();
    const { places: commonPlaces } = useCommonPlaces();
    const { vehicleItems: dynamicVehicleItems, vehicles } = useVehicles();

    // autofill vehicles
    useEffect(() => {
        if (vehicle && vehicles.length > 0) setVehicle(vehicle);
    }, [vehicle, vehicles]);

    // autofill rates and categories
    useEffect(() => {
        if (rate && rates.length > 0) {
            updateSelectedRate(rate);
        }
    }, [rate, rates]);

    // Get the trip that will be edited
    const handleGetTrip = async () => {
        const tripId = id as string | undefined;
        if (!tripId) return;

        setTripLoading(true);
        const response = await getTrip(tripId);
        
        if (!response) {
            alert("Trip not found, please try again.");
            setTripLoading(false);
            return;
        }

        setTrip(response);
        setTripLoading(false);
    }

    const handleGetExpenses = async () => {
        const tripId = id as string | undefined;
        if (!tripId) return;
        
        setExpenseLoading(true);
        const response = await getTripExpenses(tripId);

        if (!response) {
            alert("Expenses not found. Please try again");
            setExpenseLoading(false);
            return;
        }

        // Set overall expense for updating later
        setExpenses(response);
        
        // Set the Parking, toll, and gas based on the response
        setParking(String(response.find(e => e.type === 'Parking')?.amount ?? 0.00));
        setTolls(String(response.find(e => e.type === 'Tolls')?.amount ?? 0.00));
        setGas(String(response.find(e => e.type === 'Gas')?.amount ?? 0.00));
        setExpenseLoading(false);
    }

    const handleGetReceipt = async () => {
        const tripId = id as string | undefined;

        if (!tripId) return;

        setIsReceiptLoading(true);
        const response = await getReceipts(tripId);

        if (!response) {
            setIsReceiptLoading(false);
            setReceipt(null);
            alert('Failed to get receipts, please try again.')
            return;
        }

        if (response === undefined) {
            setIsReceiptLoading(false);
            setReceipt(null);
            return; // no receipt
            
        }

        setReceipt(response);
        setIsReceiptLoading(false);
       
    }

    const handleTakePhoto = async () => {
        try {
            const permissionResults = await ImagePicker.requestMediaLibraryPermissionsAsync();

            if (!permissionResults.granted) {
                alert("Permission Required. Please allow media library permissions.")
                return;
            }

            // let the user pick a picture from the media library
            const picture = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ['images'],
                allowsEditing: true,
                aspect: [4,3],
                quality: 1 // high quality
            });

            if (!picture.canceled && picture.assets?.length) {
                const asset = picture.assets[0];
                const filename = asset.fileName || `receipt-${Date.now()}.jpg`;

                setImage(asset.uri ?? null);
                setImageName(filename);

                await handleUploadImage(asset);
            }

        } catch (error) {
            console.error("Error getting photo: ", error);
        }
    }

    const handleUploadImage = async (asset: ImagePicker.ImagePickerAsset) => {
        try {
            // Get Expense and Trip Id
            const expenseId = expenses?.find(e => e.type === 'Tolls')?.id ?? ""  // hard coded for testing purposes
            const tripId = trip?.id ?? "";

            let uri = asset.uri;
            if (!uri) {
                console.warn("Selected asset is missing a URI");
                return;
            }

            const name = asset.fileName || `receipt-${Date.now()}.jpg`;
            const type = asset.mimeType || "image/jpeg";

            // Resolve iOS library URIs to a file path Expo can read the bytes
            if (uri.startsWith("ph://") && asset.assetId) {
                const info = await MediaLibrary.getAssetInfoAsync(asset.assetId);
                if (info.localUri) {
                    uri = info.localUri;
                }
            }

            // Copy Android content URIs into the cache directory for read access
            if (uri.startsWith("content://")) {
                const cachePath = `${FileSystem.cacheDirectory}${name}`;
                try {
                    await FileSystem.copyAsync({ from: uri, to: cachePath });
                    uri = cachePath;
                } catch (copyError) {
                    console.warn("Unable to copy receipt to cache", copyError);
                }
            }

            // Check if the file:// is present for proper upload
            if (!uri.startsWith("file://")) {
                console.warn("Receipt URI is not a file path; upload may fail", uri);
            }

            const formData = new FormData();
            formData.append('file', {
                // Expo's fetch/FormData requires a file:// URI
                uri: uri.startsWith("file://") ? uri : `file://${uri}`,
                name,
                type,
            } as any);

            const response = await addReceipt(tripId, formData);
            alert("Receipt uploaded successfully.")
            setReceipt(response);
            
            

        } catch (error) {
            console.error("Error uploading photo: ", error);
            alert("Error uploading receipt. Please try again");
        }
    }

    // When the trip is modified, handle update
    const handleUpdateTrip = async () => {

        const tripId = id as string;
        try {
            const updatedTripData = {
                purpose: notes,
                vehicle_id: vehicle || undefined,
                mileage_reimbursement_total: tripValue,
                ...(rate ? { rate_customization_id: rate } : {}),
                ...(type ? { rate_category_id: type } : {}),
                miles: tripDistance,
                start_address: startAddress,
                end_address: endAddress,
                geometry: tripGeometry,
                // handle expenses...
            }

           const response = await editTrip(tripId, updatedTripData)

           if (!response) {
            alert("Failed to update trip. Please try again.")
            return;
           }

            const expenseUpdate = await handleUpdateExpenses();


           if (!expenseUpdate) {
            alert("Trip updated, but error updating expenses. Please try again.");
            return;
           }
        
            alert("Trip updated successfully.")
            router.push('/(tabs)/history');

        } catch (error) {
            console.error("Error updating trip,", error);
            alert("Failed tp update trip. Please try again.")
        }     
    }

    const handleUpdateExpenses = async () => {
        const tripId = id as string;

        const expenseUpdates = [];
        
        // Find if there's a parking expense, update if amount > 0
        const parkingExpense = expenses?.find(e => e.type === 'parking' || e.type === 'Parking');
        const parkingAmount = parseFloat(parking) || 0;
        if (parkingAmount > 0) {
            if (parkingExpense) { // add it to the expense updates
                expenseUpdates.push({
                    id: parkingExpense.id,
                    type: parkingExpense.type,
                    amount: parkingAmount
                });
            } else {
                // Create new parking expense
                expenseUpdates.push({
                    id: null, // signals creation, aka empty id and just type/amount
                    type: 'Parking',
                    amount: parkingAmount
                });
            }
        }

        // Find toll expense, update if > 0
        const tollsExpense = expenses?.find(e => e.type === 'tolls' || e.type === 'Tolls');
        const tollsAmount = parseFloat(tolls) || 0;
        if (tollsAmount > 0) {
            if (tollsExpense) {
                expenseUpdates.push({
                    id: tollsExpense.id,
                    type: tollsExpense.type,
                    amount: tollsAmount
                });
            } else { // else add it to create expenses
                expenseUpdates.push({
                    id: null,
                    type: 'Tolls',
                    amount: tollsAmount
                });
            }
        }

        // find gas expense and add it to the arr if non existant
        const gasExpense = expenses?.find(e => e.type === 'gas' || e.type === 'Gas');
        const gasAmount = parseFloat(gas) || 0;
        if (gasAmount > 0) {
            if (gasExpense) {
                expenseUpdates.push({
                    id: gasExpense.id,
                    type: gasExpense.type,
                    amount: gasAmount
                });
            } else {
                expenseUpdates.push({
                    id: null,
                    type: 'Gas',
                    amount: gasAmount
                });
            }
        }

        // if none changed, then don't update
        if (expenseUpdates.length === 0) {
            console.log('No expenses to create or update');
            return true;
        }

        console.log('Expense updates to send:', expenseUpdates);

            // Ensure for Update / Creation that all promises get settled
            const results = await Promise.allSettled(
                expenseUpdates.map((expense) => {
                    if (expense.id) {
                        // update expenses
                        return updateTripExpense(expense.id, tripId, {
                            type: expense.type,
                            amount: expense.amount
                        });
                    } else { // else create an expense for the trip
                        return createTripExpense(tripId, {
                            type: expense.type,
                            amount: expense.amount
                        });
                    }
                })
            );

            console.log('Update results:', results);
            
            // Check if there were any failures for updating/creating new expenses
            const failures = results.filter(r => r.status === 'rejected');
            if (failures.length) {
                console.warn(`Failure to update ${failures.length} expense(s).`);
                return false;
            } 
        
        return true;
    }

    const handleRateChange = (selectedRateId: string | null) => {
        setRate(selectedRateId);

        if (selectedRateId !== rate) {
            setType(null);
        }
        updateSelectedRate(selectedRateId);
    };

    const handleTypeChange = (newType: string | null) => {
        setType(newType);
    };

    // get the trip with passed id
    useEffect(() => {
        if (id) {
            handleGetTrip();
        }
    }, [id]);
    
    // use effect for syncing the current state of trip once loaded
    useEffect(() => {
        if(!trip) return;
        setNotes(trip.purpose ?? '');

        // extract vehicle id from trip.vehicle object if it exists
        let extractedVehicleId = trip.vehicle_id;
        if (!extractedVehicleId && trip.vehicle) {
            extractedVehicleId = typeof trip.vehicle === 'object' ? (trip.vehicle as any).id : trip.vehicle;
        }
        setVehicle(extractedVehicleId || null);



        setTripValue(trip.mileage_reimbursement_total ?? 0.00);
        setRate(trip.rate_customization_id ?? null);
        setType(trip.rate_category_id ?? null);    
        setTripDistance(trip.miles ?? 0);              
        setStartAddress(trip.start_address ?? '');
        setEndAddress(trip.end_address ?? '');
        setTripGeometry(trip.geometry ?? null);
        // checking if the start time is null bc typescript
        const startedAt = trip.started_at ? new Date(trip.started_at as unknown as string) : null;
        setTripDate(startedAt ? startedAt.toUTCString() : '');
        // await handle expenses to ensure expenses are loaded before update
        (async () => {
            await handleGetExpenses();
            await handleGetReceipt();
        })();
    }, [trip])

    if (isTripLoading) {
        return (
            <Text>Loading...</Text>
        )
    }

    if (error) {
        return (
            <Text>Error: {error}</Text>
        )
    }

    return (
        
        <ScreenLayout
            footer={
                <>
                    <View className='flex-row jusitfy-between mb-4'>
                        <EditableNumericDisplay
                            label='Value'
                            value={tripValue != null ? String(tripValue) : '0.00'}
                            onChangeText={(text) => {
                                const trimmed = text.trim();
                                const parsed = trimmed === '' ? null : Number(trimmed);
                                setTripValue(parsed as number | null);
                            }}
                            unit='$'
                        />
                        <EditableNumericDisplay
                            label='Distance'
                            value={tripDistance != null ? String(tripDistance) : '0.00'}
                            onChangeText={(text) => {
                                const trimmed = text.trim();
                                const parsed = trimmed === '' ? null : Number(trimmed);
                                setTripValue(parsed as number | null);
                            }}
                            unit='mi'
                        />
                    </View>
                    <Button className="py-4 px-5"
                        title="Update Trip"
                        onPress={handleUpdateTrip}
                        style={{top: 10}}
                    />
                </>
            }
        >
            <View style={{height: 300, width: '100%', overflow: 'hidden'}}>
                <GeometryMap geometry={tripGeometry}/>
            </View>
            <Text className="text-xl text-black p-6">{tripDate}</Text>

            <TripDetailsForm

            mapboxAccessToken={MAPBOX_KEY || ''}

            notes={notes} setNotes={setNotes}
            vehicle={vehicle} setVehicle={setVehicle}
            type={type} setType={handleTypeChange}
            rate={rate} setRate={handleRateChange}
            parking={parking} setParking={setParking}
            gas={gas} setGas={setGas}
            tolls={tolls} setTolls={setTolls}
            startAddress={startAddress} setStartAddress={setStartAddress}
            endAddress={endAddress} setEndAddress={setEndAddress}

            vehicleItems={dynamicVehicleItems}
            typeItems={categoryItems}
            rateItems={rateItems}

            commonPlaces={commonPlaces.map((p: { id: string; name: string; address: string }) => ({
            id: p.id,
            title: p.name,
            address: p.address
        }))}


            />
        {receipt && receipt.length > 0 ? (
             <View style={{flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 30}}>
                <Text style={{marginTop: 40}}>{receipt[0]?.file_name}</Text>
                <Button className="py-4 px-5"
                    title="+ Change Receipt"
                    onPress={handleTakePhoto}
                    style={{top: 20}}
                />
            </View>
        ) : (
            <View>
                <Button className="py-4 px-5"
                    title="+ Add Receipt"
                    onPress={handleTakePhoto}
                    style={{top: 20}}
                />
            </View>
        )}
        </ScreenLayout>
    );
}

export default EditTripPage;