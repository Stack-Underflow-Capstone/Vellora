import { StyleSheet, View } from 'react-native';
import React from 'react';
import MapboxGL from '@rnmapbox/maps';

interface GeometryMapProps {
    geometry?: object | null;
}

// get mapbox access token
const MAPBOX_KEY = process.env.EXPO_PUBLIC_API_KEY_MAPBOX_PUBLIC_ACCESS_TOKEN;
MapboxGL.setAccessToken(`${MAPBOX_KEY}`);

const GeometryMap: React.FC<GeometryMapProps> = ({ geometry }) => {

    // dynamically receive geometry
    const shape = geometry;
    const shapeWithCoords = shape as any;

    // calculate the center coordinate
    const getCenterCoordinate = (): number[] => {
        if (shapeWithCoords?.coordinates && Array.isArray(shapeWithCoords.coordinates)) {
            const coordinates = shapeWithCoords.coordinates;
            if (coordinates.length > 0){
                return coordinates[Math.floor(coordinates.length / 2)];
            }
        }
        return [0, 0];
    };

    const centerCoordinate = getCenterCoordinate();
    const hasValidCoordinates = shapeWithCoords?.coordinates && Array.isArray(shapeWithCoords.coordinates) && shapeWithCoords.coordinates.length > 0;
    return (
        <View style={styles.container}>

            {/* main map component */}
            <MapboxGL.MapView style={styles.map}>

                {/* configure the map's view point */}
                <MapboxGL.Camera 
                    zoomLevel={12}                              // zoom in
                    centerCoordinate={centerCoordinate}        // center the coordinate
                    animationMode={'none'}                      // disable animations
                />

                {/* load the geoJSON data source for the map. "as any" bypasses typescript checks */}
                <MapboxGL.ShapeSource id="line-source" shape={shape as any}>

                    {/* linelayer to visualize the geoJSON */}
                    <MapboxGL.LineLayer 
                        id="linelayer"
                        style={{
                            // style the route line
                            lineCap: 'round',
                            lineJoin: 'round',
                            lineOpacity: 1,
                            lineWidth: 5.0,
                            lineColor: '#404CCF',
                        }}
                    />
                </MapboxGL.ShapeSource>

                {/* Start and end point markers on the geometry line. Green - start. Red - end */}
                {hasValidCoordinates && (
                    <>
                        {/* Start point marker */}
                        <MapboxGL.ShapeSource
                        id="start-source"
                        shape={{
                            type: 'Feature',
                            geometry: {
                            type: 'Point',
                            coordinates: shapeWithCoords.coordinates[0],
                            },
                            properties: {},
                        }}
                        >
                        <MapboxGL.CircleLayer
                            id="start-point"
                            style={{
                            circleRadius: 8,
                            circleColor: '#4CAF50', // Green for start
                            }}
                        />
                        </MapboxGL.ShapeSource>

                        {/* End point marker */}
                        <MapboxGL.ShapeSource
                        id="end-source"
                        shape={{
                            type: 'Feature',
                            geometry: {
                            type: 'Point',
                            coordinates: shapeWithCoords.coordinates[shapeWithCoords.coordinates.length - 1],
                            },
                            properties: {},
                        }}
                        >
                        <MapboxGL.CircleLayer
                            id="end-point"
                            style={{
                            circleRadius: 8,
                            circleColor: '#F44336', // Red for end
                            }}
                        />
                        </MapboxGL.ShapeSource>
                    </>
                )}

            </MapboxGL.MapView>
        </View>
    )
}

export default GeometryMap

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',       // center veritcally
        alignItems: 'center',           // center horizontally
    },
    map: {
        flex: 1,
        alignSelf: 'stretch',           // stretch full container width
    },
})