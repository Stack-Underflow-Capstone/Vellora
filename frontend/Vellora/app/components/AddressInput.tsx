import { TextInput, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator, Text, View } from 'react-native'
import React, {useState, useEffect } from 'react'
import { FontAwesome } from '@expo/vector-icons'

const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;

//  shape of a common place that gets passed from the parent
export type CommonPlaceItem = {
    id: string;
    title: string;
    address: string;
    lat?: number;
    lng?: number;
}

// type safety
type AddressInputProps = {
    label?: string;
    placeholder?: string;
    value: string;
    onChangeText: (text: string) => void;
    onAddressSelect: (addressData: any) => void;    // callback with address details
    mapboxAccessToken: string;
    icon?: React.ReactNode;
    className?: string;
    commonPlaces?: CommonPlaceItem[];           // list of common places
}

const AddressInput: React.FC<AddressInputProps> = ({
    label,
    placeholder = "Enter address",
    value,
    onChangeText,
    onAddressSelect,
    mapboxAccessToken,
    icon,
    className = '',
    commonPlaces = [],
}) => {

    const [suggestions, setSuggestions] = useState<any[]>([]);  // suggested addresses based on users input
    const [isLoading, setIsLoading] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    // filter common places based on input
    const getLocalMatches = (query: string) => {
        if (!query || query.length < 1) {
            return [];
        }

        const lowerQuery = query.toLowerCase();
        return commonPlaces.filter(place =>
            place.title.toLowerCase().includes(lowerQuery) ||
            place.address.toLowerCase().includes(lowerQuery)
        ).map(place => ({
            id: `common-${place.id}`,
            place_name: place.title,
            secondary_text: place.address,
            center: (place.lng && place.lat) ? [place.lng, place.lat] : null,
            isCommonPlace: true
        }));

    };

    // wait for 500 ms after typing stops before calling the API for locations
    useEffect(() => {

        // don't search if not focused on the address input
        if (!isFocused) {
            return;
        }

        // handle the case when the user did not type in anything yet
        if (!value || value.length < 3) {
            setSuggestions([]);
            return;
        }

        // immediately show local matches from common places
        const localResults = getLocalMatches(value);
        setSuggestions(localResults);

        // if input is short, don't hit the api yet
        if (value.length < 3) {
            return;
        }

        // otherwise, fetch suggested addresses
        const timer = setTimeout(() => {
            fetchAddressSuggestions(value, localResults);
        }, 500);

        return () => clearTimeout(timer);
    }, [value, isFocused]);

    // mapbox api call
    const fetchAddressSuggestions = async (query: string, existingLocalResults: any[]) => {
        setIsLoading(true);

        try {
            const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${MAPBOX_KEY}&autocomplete=true&types=address,poi`);
            const data = await response.json();
            if (data.features) {
                // common places are suggested on top, mapbox results bellow
                setSuggestions([...existingLocalResults, ...data.features]);
            } else {
                setSuggestions(existingLocalResults);  // only local results
            }
        } catch (error) {
            console.error("Mapbox geocoding error: ", error);

            // keep showing local results even if api fails:
            setSuggestions(existingLocalResults);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelect = (item: any) => {       // receive an address object

        // if it is a common place, we use the address. if mapbox, use place_name
        const finalText = item.isCommonPlace ? item.secondary_text : item.place_name;

        onChangeText(finalText);          // update the text in the input box
        setSuggestions([]);              // empty suggested addresses
        onAddressSelect({                // send address details back to the parent page
            place_name: finalText,
            center: item.center,
        });    
        setIsFocused(false);          // remove focus to hide suggestions              
    };

    return (
        <View className={`mb-4 ${className}`}>

            {/* return the label if any */}
            {label && <Text className='text-sm text-gray-500 mb-1'>{label}</Text>}

            <View className='flex-row border items-center border-gray-300 bg-white rounded-lg px-3 py-3'>
                <View className='w-6 items-center'>{icon}</View>

                <TextInput 
                    style={{ flex: 1, fontSize: 16, marginLeft: 10, color: 'black' }}
                    placeholder={placeholder}
                    placeholderTextColor="gray"
                    value={value}
                    onChangeText={onChangeText}

                    // handle focus events
                    onFocus={() => setIsFocused(true)}

                    // set timeouw to allow the click on the list item to refuster before hiding it
                    onBlur={() => setTimeout(() => setIsFocused(false), 200)}
                />
                {isLoading && <ActivityIndicator size="small" color="#4DBF69" />}
            
            </View>

            {suggestions.length > 0 && isFocused && (
                <View style={styles.suggestionsContainer}>
                    <FlatList
                        data={suggestions}
                        keyExtractor={(item) => item.id}
                        scrollEnabled={false}
                        keyboardShouldPersistTaps="handled"     // tap handling
                        renderItem={({ item }) => (
                            <TouchableOpacity
                                style={styles.suggestionsItem}
                                onPress={() => handleSelect(item)}
                            >
                                <View className='flex-row items-center'>

                                    {/* show different icon for common places */}
                                    {item.isCommonPlace ? (
                                        <FontAwesome name="star" size={14} color="#FBBF24" className='mr-2' />
                                    ) : (
                                        <FontAwesome name="map-marker" size={14} color="#6B7280" className='mr-2' />
                                    )}

                                    <View>
                                        <Text style={styles.suggestionText}>
                                            {item.place_name}
                                        </Text>

                                        {/* show address subtitle for common places */}
                                        {item.isCommonPlace && (
                                            <Text style={[styles.suggestionText, { fontSize: 12, color: '#6B7280' }]}>
                                                {item.secondary_text}
                                            </Text>
                                        )}
                                    </View>
                                </View>
                            </TouchableOpacity>
                        )}
                    />
                </View>
            )}
        </View>
    );
};


export default AddressInput

const styles = StyleSheet.create({
    suggestionsContainer: {
        backgroundColor: 'white',
        borderWidth: 1,
        borderColor: '#ddd',
        borderTopWidth: 0,
        borderBottomLeftRadius: 8,
        borderBottomRightRadius: 8,
        marginTop: -2,
        zIndex: 10,
    },
    suggestionsItem: {
        padding: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    suggestionText: {
        color: '#333',
        fontSize: 14,
    },
});