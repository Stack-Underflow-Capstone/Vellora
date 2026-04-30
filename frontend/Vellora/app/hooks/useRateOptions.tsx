import { useState, useEffect } from 'react';
import { getRateCustomizations, RateCustomization, RateCategory } from '../services/rateCustomizations';

// type for dropdown items for typescript to shut up
type DropdownItem = {
    label: string;
    value: string;
    originalCategory?: RateCategory;
};

export const useRateOptions = () => {
    const [rates, setRates] = useState<RateCustomization[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedRate, setSelectedRate] = useState<RateCustomization | null>(null);

    const fetchRates = async () => {
        try {
            setLoading(true);
            setError(null);
            const userRates = await getRateCustomizations();
            setRates(userRates);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch rates');
            console.error('Error fetching rates:', err);

        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRates();
    }, []);

    // transform rates for dropdown format
    const rateItems = rates.map(rate => ({
        label: `${rate.name} (${rate.year})`,
        value: rate.id,
        originalRate: rate,
    }));

    const getCategoriesForSelectedRate = (): DropdownItem[] => {
        try {
            
            if (!selectedRate || !selectedRate.categories) {
            return [];
            }

            // type assertion
            // we know selectedRate.categories should be RateCategory[] if it exists
            const categories = selectedRate.categories as RateCategory[];
            
            if (categories.length === 0) {
            return [];
            }

            return categories.map(category => ({
            label: `${category.name} ($${category.cost_per_mile}/mi)`,
            value: category.id,
            originalCategory: category,
            }));
        } catch (error) {
            console.error('Error in getCategoriesForSelectedRate:', error);
            return [];
        }
    };

    // update selected rate when rate ID changes
    const updateSelectedRate = (rateId: string | null) => {
        try {
            
            if (!rateId) {
                setSelectedRate(null);
                return;
            }

            const rate = rates.find(r => r.id === rateId);
            setSelectedRate(rate || null);
        } catch (error) {
            console.error('Error in updateSelectedRate:', error);
            setSelectedRate(null);
        }
    };

    // ensure categoryItems is always an array
    const categoryItems: DropdownItem[] = getCategoriesForSelectedRate();

    return {
        rates,
        rateItems,
        categoryItems,
        selectedRate,
        loading,
        error,
        refreshRates: fetchRates,
        updateSelectedRate,
    };
};