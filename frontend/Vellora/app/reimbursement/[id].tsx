import { router, useLocalSearchParams } from "expo-router";
import ViewCustomRatePage from "../components/ViewCustomRatePage";

export default function Page() {
  const params = useLocalSearchParams();
  const id = params.id;

  return <ViewCustomRatePage onBack={() => router.back()} />;
}
