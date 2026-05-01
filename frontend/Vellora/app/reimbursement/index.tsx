import { useState, useEffect } from "react";
import { useLocalSearchParams, router } from "expo-router";
import { View, Text, ActivityIndicator } from "react-native";
import ReimbursementRateListPage from "../components/ReimbursementRateListPage";
import {
	getRateCustomizations,
	RateCustomization,
	deleteRateCustomization,
} from "../services/rateCustomizations";
import { tokenStorage } from "../services/tokenStorage";

export type CustomRate = {
	id: string;
	name: string;
	description: string;
	year: string;
	categories: {
		id: string;
		name: string;
		rate: string;
	}[];
};

function mapToCustomRate(customization: RateCustomization): CustomRate {
	return {
		id: customization.id,
		name: customization.name,
		description: customization.description || "",
		year: customization.year.toString(),
		categories: (customization.categories || []).map((cat) => ({
			id: cat.id,
			name: cat.name,
			rate: cat.cost_per_mile.toFixed(2),
		})),
	};
}

export default function Index() {
	const params = useLocalSearchParams();
	const [customRates, setCustomRates] = useState<CustomRate[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [redirecting, setRedirecting] = useState(false);
	const [deletingId, setDeletingId] = useState<string | null>(null);
	const [currentToken, setCurrentToken] = useState<string | null>(null);

	const fetchRates = async () => {
		const token = tokenStorage.getToken();
		if (!token) {
			if (!redirecting) {
				setRedirecting(true);
				router.replace({
					pathname: "/login",
					params: { redirect: "/reimbursement" },
				} as any);
			}
			return;
		}

		setLoading(true);
		setError(null);
		setRedirecting(false);
		try {
			setCurrentToken(token);
			const rates = await getRateCustomizations(token || undefined);
			const mappedRates = rates
				.map(mapToCustomRate)
				.filter((rate) => rate.name !== "IRS Standard Rates");
			setCustomRates(mappedRates);
		} catch (err) {
			if (
				(err instanceof Error &&
					(err.message.includes("Authentication required") ||
						err.message.includes("Unauthorized"))) ||
				(err as any).status === 401
			) {
				if (!redirecting) {
					setRedirecting(true);
					tokenStorage.clearToken();
					router.replace({
						pathname: "/login",
						params: { redirect: "/reimbursement" },
					} as any);
					return;
				}
			}
			setError(err instanceof Error ? err.message : "Failed to load rates");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		const timer = setTimeout(() => {
			fetchRates();
		}, 500);
		return () => clearTimeout(timer);
	}, []);

	useEffect(() => {
		if (params.newRate && typeof params.newRate === "string") {
			try {
				const parsed = JSON.parse(params.newRate);
				setCustomRates((prev) => {
					if (prev.some((r) => r.id === parsed.id)) return prev;
					return [...prev, parsed];
				});
				fetchRates();
			} catch {}
		}
	}, [params.newRate]);

	const handleDelete = async (id: string) => {
		if (deletingId) return;
		setDeletingId(id);
		try {
			const token = currentToken || tokenStorage.getToken();
			if (!token) {
				setError("Please log in to delete rates");
				setDeletingId(null);
				return;
			}

			await deleteRateCustomization(id, token);
			setCustomRates((prev) => prev.filter((rate) => rate.id !== id));
			setError(null);
		} catch (err) {
			if (
				(err instanceof Error &&
					(err.message.includes("Authentication required") ||
						err.message.includes("Unauthorized"))) ||
				(err as any).status === 401
			) {
				setError("Your session has expired. Please log in again.");
				tokenStorage.clearToken();
				setTimeout(() => {
					if (!redirecting) {
						setRedirecting(true);
						router.replace({
							pathname: "/login",
							params: { redirect: "/reimbursement" },
						} as any);
					}
				}, 2000);
			} else {
				setError(err instanceof Error ? err.message : "Failed to delete rate");
			}
		} finally {
			setDeletingId(null);
		}
	};

	if (loading) {
		return (
			<View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
				<ActivityIndicator size="large" color="#3F46D6" />
				<Text style={{ marginTop: 10 }}>Loading rates...</Text>
			</View>
		);
	}

	if (error) {
		return (
			<View
				style={{
					flex: 1,
					justifyContent: "center",
					alignItems: "center",
					padding: 20,
				}}>
				<Text style={{ color: "red", marginBottom: 10 }}>{error}</Text>
				<Text
					onPress={fetchRates}
					style={{ color: "#3F46D6", textDecorationLine: "underline" }}>
					Retry
				</Text>
			</View>
		);
	}

	return (
		<ReimbursementRateListPage
			rates={customRates}
			onCreateCustom={() => router.push("/reimbursement/add")}
			onOpenIRS={() => router.push("/reimbursement/irs")}
			onOpenCustomRate={(id) =>
				router.push({
					pathname: "/reimbursement/details",
					params: { id },
				})
			}
			onDelete={handleDelete}
			deletingId={deletingId}
		/>
	);
}
