import { useState, useEffect, useCallback } from "react";
import { getCommonPlaces, CommonPlace } from "../services/commonPlaces";
import { useFocusEffect } from "expo-router";

export function useCommonPlaces() {
    const [places, setPlaces] = useState<CommonPlace[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPlaces = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getCommonPlaces();
            setPlaces(data);
        } catch (err: any) {
            console.error("Error fetching common places:", err);
            setError(err.message || "Failed to load common places");
        } finally {
            setLoading(false);
        }
    }, []);

    // fetch automatically when the screen comes into focus
    useFocusEffect(
        useCallback(() => {
            fetchPlaces();
        }, [fetchPlaces])
    );

    return { places, loading, refreshPlaces: fetchPlaces}
}