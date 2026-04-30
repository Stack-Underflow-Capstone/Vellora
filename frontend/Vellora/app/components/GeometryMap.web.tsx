import React, { useMemo } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface GeometryMapProps {
  geometry?: object | null;
}

type Coordinates = [number, number][];

type LineGeometry = {
  type?: string;
  coordinates?: Coordinates;
};

const GeometryMap: React.FC<GeometryMapProps> = ({ geometry }) => {
  const line = geometry as LineGeometry | null;
  const coordinates = useMemo(() => {
    if (!line?.coordinates || !Array.isArray(line.coordinates)) {
      return [] as Coordinates;
    }
    return line.coordinates;
  }, [line]);

  const start = coordinates[0];
  const end = coordinates[coordinates.length - 1];

  return (
    <View style={styles.container}>
      <View style={styles.badge}>
        <Text style={styles.badgeText}>Web Route Preview</Text>
      </View>

      {coordinates.length > 0 ? (
        <View style={styles.infoContainer}>
          <Text style={styles.label}>Points: {coordinates.length}</Text>
          <Text style={styles.coordsText} numberOfLines={1}>
            Start: {start[1].toFixed(5)}, {start[0].toFixed(5)}
          </Text>
          <Text style={styles.coordsText} numberOfLines={1}>
            End: {end[1].toFixed(5)}, {end[0].toFixed(5)}
          </Text>
        </View>
      ) : (
        <Text style={styles.emptyText}>No route geometry available.</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 10,
    backgroundColor: '#EEF2FF',
    borderWidth: 1,
    borderColor: '#C7D2FE',
    padding: 8,
    justifyContent: 'space-between',
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    backgroundColor: '#404CCF',
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
  },
  infoContainer: {
    gap: 4,
  },
  label: {
    color: '#1F2937',
    fontSize: 12,
    fontWeight: '700',
  },
  coordsText: {
    color: '#374151',
    fontSize: 11,
  },
  emptyText: {
    color: '#4B5563',
    fontSize: 12,
  },
});

export default GeometryMap;
