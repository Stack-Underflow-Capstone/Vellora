
#1 mile = 1609.34 meters
METERS_PER_MILE = 1609.34


def meters_to_miles(meters: float) -> float:
    if meters < 0:
        raise ValueError("Distance in meters cannot be negative")
    
    miles = meters / METERS_PER_MILE
    return round(miles, 2)


def miles_to_meters(miles: float) -> float:
    if miles < 0:
        raise ValueError("Distance in miles cannot be negative")
    
    meters = miles * METERS_PER_MILE
    return round(meters, 2)
