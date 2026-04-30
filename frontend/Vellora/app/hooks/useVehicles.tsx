import { useState, useEffect } from "react";
import { getVehicles, Vehicle } from "../services/vehicles";

export const useVehicles = () => {
    const [vehicles, setVehicles] = useState<Vehicle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getVehicles();
            setVehicles(data);
        } catch (err) {
            setError("Failed to load vehicles. Please try again.");
            console.error("Error fetching vehicles:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVehicles();
    }, []);

    // change vehiclees into the format required by the dropdown component
    const vehicleItems = vehicles.map((v) => ({
        label: `${v.name} (${v.model})`,
        value: v.id,
    }));
    return { vehicles, vehicleItems, loading, error, refreshVehicles: fetchVehicles};
}