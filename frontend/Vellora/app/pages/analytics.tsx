import React, { useEffect, useMemo, useState } from "react";
import { View, Text, StyleSheet, ScrollView, Pressable } from "react-native";
import { router } from "expo-router";
import Svg, { Circle } from "react-native-svg";
import ScreenLayout from "../components/ScreenLayout";
import Button from "../components/Button";
import MonthYearDropdown from "../components/MonthYearDropdown";
import { reportStyles } from "../styles/ReportStyles";
import { getReportAnalytics } from "../services/reports";

type ChartType = "bar" | "donut";

const CHART_COLORS = ["#4F46E5", "#F97316", "#10B981", "#EF4444", "#F59E0B", "#06B6D4", "#8B5CF6"];

export default function AnalyticsPage() {
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [chartType, setChartType] = useState<ChartType>("bar");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [totalMiles, setTotalMiles] = useState(0);
  const [grandTotal, setGrandTotal] = useState(0);

  const monthName = useMemo(
    () => currentDate.toLocaleDateString("en-US", { month: "long" }),
    [currentDate]
  );

  useEffect(() => {
    let isMounted = true;

    const loadAnalytics = async () => {
      setLoading(true);
      setError(null);

      try {
        const analytics = await getReportAnalytics(monthName);
        if (!isMounted) return;

        setCategoryCounts(analytics.category_counts ?? {});
        setTotalMiles(analytics.total_miles ?? 0);
        setGrandTotal(analytics.grand_total ?? 0);
      } catch (err) {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : "Failed to load analytics";
        setError(message);
        setCategoryCounts({});
        setTotalMiles(0);
        setGrandTotal(0);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadAnalytics();

    return () => {
      isMounted = false;
    };
  }, [monthName]);

  const chartData = useMemo(
    () =>
      Object.entries(categoryCounts).map(([label, value], index) => ({
        label,
        value,
        color: CHART_COLORS[index % CHART_COLORS.length],
      })),
    [categoryCounts]
  );

  const maxValue = Math.max(...chartData.map((d) => d.value), 1);
  const totalTrips = chartData.reduce((sum, item) => sum + item.value, 0);

  const renderDonutChart = () => {
    const size = 220;
    const strokeWidth = 26;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;

    if (totalTrips <= 0) {
      return <Text style={styles.emptyText}>No category data for this month.</Text>;
    }

    let cumulative = 0;

    return (
      <View style={styles.donutWrapper}>
        <View style={styles.donutChartContainer}>
          <Svg width={size} height={size}>
            <Circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke="#E5E7EB"
              strokeWidth={strokeWidth}
              fill="transparent"
            />

            {chartData.map((segment) => {
              const fraction = segment.value / totalTrips;
              const dashLength = circumference * fraction;
              const gapLength = circumference - dashLength;
              const rotation = (cumulative / totalTrips) * 360 - 90;

              cumulative += segment.value;

              return (
                <Circle
                  key={segment.label}
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  stroke={segment.color}
                  strokeWidth={strokeWidth}
                  fill="transparent"
                  strokeDasharray={`${dashLength} ${gapLength}`}
                  rotation={rotation}
                  originX={size / 2}
                  originY={size / 2}
                  strokeLinecap="butt"
                />
              );
            })}
          </Svg>

          <View style={styles.donutCenter}>
            <Text style={styles.donutTotal}>{totalTrips}</Text>
            <Text style={styles.donutTotalLabel}>Trips</Text>
          </View>
        </View>
      </View>
    );
  };


  return (
    <ScreenLayout
      footer={
        <View>
          <Button title="Generate Reports" onPress={() => router.back()} className="mt-3 py-4 px-5" />
        </View>
      }>
      <ScrollView contentContainerStyle={{ padding: 24 }}>
        <Text style={reportStyles.title}>Analytics</Text>

        <Text style={reportStyles.sectionLabel}>Select Month</Text>
        <View style={{ marginBottom: 18 }}>
          <MonthYearDropdown currentDate={currentDate} onDateChange={setCurrentDate} />
        </View>

        <View style={styles.metricsRow}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Total Miles</Text>
            <Text style={styles.metricValue}>{totalMiles.toFixed(1)}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Grand Total</Text>
            <Text style={styles.metricValue}>${grandTotal.toFixed(2)}</Text>
          </View>
        </View>

        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={reportStyles.sectionLabel}>Trips by Category</Text>
            <View style={styles.toggleRow}>
              <Pressable
                style={[styles.toggleButton, chartType === "bar" && styles.toggleButtonActive]}
                onPress={() => setChartType("bar")}>
                <Text style={[styles.toggleText, chartType === "bar" && styles.toggleTextActive]}>Bar</Text>
              </Pressable>
              <Pressable
                style={[styles.toggleButton, chartType === "donut" && styles.toggleButtonActive]}
                onPress={() => setChartType("donut")}>
                <Text style={[styles.toggleText, chartType === "donut" && styles.toggleTextActive]}>Donut</Text>
              </Pressable>
            </View>
          </View>

          {loading && <Text style={styles.loadingText}>Loading analytics...</Text>}
          {error && <Text style={styles.errorText}>{error}</Text>}

          {!loading && !error && (
            <View style={styles.chartContainer}>
              {chartType === "bar" ? (
                totalTrips > 0 ? (
                  <View style={styles.barsRow}>
                    {chartData.map((d) => {
                      const height = (d.value / maxValue) * 180;
                      return (
                        <View key={d.label} style={styles.barWrapper}>
                          <View style={[styles.bar, { height, backgroundColor: d.color }]} />
                          <Text style={styles.barLabel}>{d.label}</Text>
                          <Text style={styles.barValue}>{d.value}</Text>
                        </View>
                      );
                    })}
                  </View>
                ) : (
                  <Text style={styles.emptyText}>No category data for this month.</Text>
                )
              ) : (
                renderDonutChart()
              )}

              {totalTrips > 0 && (
                <View style={styles.legendContainer}>
                  {chartData.map((d) => (
                    <View key={`legend-${d.label}`} style={styles.legendRow}>
                      <View style={[styles.legendDot, { backgroundColor: d.color }]} />
                      <Text style={styles.legendText}>{d.label}</Text>
                      <Text style={styles.legendValue}>{d.value}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          )}
        </View>

        <View style={{ height: 48 }} />
      </ScrollView>
    </ScreenLayout>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "white",
    padding: 20,
    borderRadius: 16,
    shadowColor: "#000",
    shadowOpacity: 0.08,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
    marginBottom: 12,
  },
  chartContainer: {
    paddingTop: 12,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  toggleRow: {
    flexDirection: "row",
    backgroundColor: "#EEF2FF",
    borderRadius: 12,
    padding: 4,
    gap: 6,
  },
  toggleButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
  },
  toggleButtonActive: {
    backgroundColor: "#404CCF",
  },
  toggleText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#404CCF",
  },
  toggleTextActive: {
    color: "#FFFFFF",
  },
  barsRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    height: 220,
  },
  barWrapper: {
    flex: 1,
    alignItems: "center",
    marginHorizontal: 6,
  },
  bar: {
    width: 28,
    borderRadius: 6,
  },
  barLabel: {
    marginTop: 8,
    fontSize: 12,
    color: "#374151",
    textAlign: "center",
  },
  barValue: {
    marginTop: 4,
    fontSize: 12,
    fontWeight: "600",
    color: "#111827",
  },
  loadingText: {
    color: "#6B7280",
    fontSize: 14,
    marginBottom: 8,
  },
  errorText: {
    color: "#DC2626",
    fontSize: 14,
    marginBottom: 8,
  },
  emptyText: {
    color: "#6B7280",
    fontSize: 14,
    textAlign: "center",
    marginVertical: 24,
  },
  metricsRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 12,
  },
  metricCard: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    padding: 14,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 1 },
    elevation: 1,
  },
  metricLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
  },
  donutWrapper: {
    alignItems: "center",
    marginVertical: 8,
  },
  donutChartContainer: {
    width: 220,
    height: 220,
    justifyContent: "center",
    alignItems: "center",
  },
  donutCenter: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  donutTotal: {
    fontSize: 28,
    fontWeight: "700",
    color: "#111827",
  },
  donutTotalLabel: {
    fontSize: 13,
    color: "#6B7280",
    marginTop: 2,
  },
  legendContainer: {
    marginTop: 16,
    borderTopWidth: 1,
    borderTopColor: "#E5E7EB",
    paddingTop: 12,
    gap: 8,
  },
  legendRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  legendText: {
    flex: 1,
    color: "#374151",
    fontSize: 13,
  },
  legendValue: {
    color: "#111827",
    fontSize: 13,
    fontWeight: "600",
  },
});
