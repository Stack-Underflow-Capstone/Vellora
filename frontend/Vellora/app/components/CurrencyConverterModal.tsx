import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, TextInput, ActivityIndicator, StyleSheet } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import Dropdown from './Dropdown';
import Button from './Button';

type Props = {
    onClose: () => void;
    onApply: (field: 'parking' | 'gas' | 'tolls', convertedValue: string) => void;
};

const EXPENSE_FIELDS = [
    { label: 'Parking', value: 'parking' },
    { label: 'Gas', value: 'gas' },
    { label: 'Tolls', value: 'tolls' },
];

const CurrencyConverterModal: React.FC<Props> = ({ onClose, onApply }) => {
    const [amount, setAmount] = useState('');
    const [currency, setCurrency] = useState<string | null>('EUR');
    const [targetField, setTargetField] = useState<string | null>('parking');

    // dynamic list of currencies for dropdown
    const [currencyList, setCurrencyList] = useState<{ label: string; value: string }[]>([]);

    const [rate, setRate] = useState<number | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // fetch all available currencies
    useEffect(() => {
        const fetchCurrencies = async () => {
            try {
                const response = await fetch('https://api.frankfurter.app/currencies');
                const data = await response.json();

                // map the data
                const formattedList = Object.keys(data)
                    .filter(key => key !== 'USD') // exclude USD since it's the default
                    .map(key => ({
                        label: `${key} - ${data[key]}`,
                        value: key
                    }));

                    setCurrencyList(formattedList);
            } catch (err) {
                console.error('Failed to fetch currencies', err);
            }
        };

        fetchCurrencies();
    }, []);

    // fetch the rate whenever the seelcted currency changes
    useEffect(() => {
        if (!currency) {
            return;
        }

        const fetchRate = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`https://api.frankfurter.app/latest?from=${currency}&to=USD`);
                
                if(!response.ok) {
                    throw new Error(`Failed to fetch exchange rate: ${response.status}`);
                }

                const data = await response.json();
                setRate(data.rates.USD);
            } catch (err) {
                setError('Failed to fetch exchange rate');
                setRate(null);
            } finally {
                setLoading(false);
            }
        };

        fetchRate();
    }, [currency]);

    const convertedAmount = (rate && amount) ? (parseFloat(amount) * rate).toFixed(2) : '0.00';
    
    const handleApply = () => {
        if (targetField && convertedAmount !== '0.00') {
            onApply(targetField as 'parking' | 'gas' | 'tolls', convertedAmount);
            setAmount('');
            onClose();
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Currency Calculator</Text>
                <TouchableOpacity onPress={onClose} style={{ padding: 4 }}>
                    <FontAwesome name="times" size={18} color='#666'/>
                </TouchableOpacity>
            </View>

            <View style={{ gap: 12, marginBottom: 16 }}>
                <TextInput 
                    style={styles.input}
                    placeholder="Foreign amount (e.g. 15.50)"
                    value={amount}
                    onChangeText={setAmount}
                    keyboardType="numeric"
                />

                <Dropdown
                    placeholder='Select Currency'
                    items={currencyList}
                    value={currency}
                    onValueChange={setCurrency}
                />

                <Dropdown
                    placeholder='Apply to which expense?'
                    items={EXPENSE_FIELDS}
                    value={targetField}
                    onValueChange={setTargetField}
                />
            </View>

            <View style={styles.resultContainer}>
                {loading ? (
                    <ActivityIndicator size="small" color="#3F46D6" />
                ) : error ? (
                    <Text style={styles.errorText}>{error}</Text>
                ) : rate ? (
                    <>
                        <Text style={styles.rateText}>1 {currency} = ${rate.toFixed(4)} USD</Text>
                        <Text style={styles.finalAmount}>${convertedAmount}</Text>
                    </>
                ) : null}
            </View>

            <Button 
                title={`Apply $${convertedAmount} to ${targetField}`}
                onPress={handleApply}
                disabled={loading || !!error || !amount}
                className='w-full py-3 px-5'
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: { 
        backgroundColor: '#F9FAFB', 
        padding: 16, 
        borderRadius: 12, 
        borderWidth: 1, 
        borderColor: '#E5E7EB',
        marginBottom: 16
    },

    header: { 
        flexDirection: 'row', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: 16 
    },

    title: { 
        fontSize: 16, 
        fontWeight: 'bold', 
        color: '#3F46D6' 
    },

    input: { 
        borderWidth: 1, 
        borderColor: '#D1D5DB', 
        borderRadius: 8, 
        padding: 12, 
        fontSize: 16, 
        backgroundColor: 'white',
        color: 'black' 
    },

    resultContainer: { 
        backgroundColor: '#EEF2FF', 
        padding: 12, 
        borderRadius: 8, 
        alignItems: 'center', 
        marginBottom: 16 
    },

    rateText: { 
        color: '#6B7280', 
        fontSize: 12, 
        marginBottom: 4 
    },

    finalAmount: { 
        color: '#3F46D6', 
        fontSize: 20, 
        fontWeight: 'bold' 
    },

    errorText: { 
        color: '#EF4444', 
        fontStyle: 'italic', 
        fontSize: 12 
    }
});

export default CurrencyConverterModal;