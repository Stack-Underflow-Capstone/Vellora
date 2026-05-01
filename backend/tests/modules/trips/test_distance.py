import pytest
from app.modules.trips.utils.distance import meters_to_miles, miles_to_meters, METERS_PER_MILE


class TestMetersToMiles:

    def test_meters_to_miles_exact_conversion(self):
        meters = 1609.34
        
        result = meters_to_miles(meters)
        
        assert result == 1.0

    def test_meters_to_miles_typical_distance(self):
        meters = 81320.0
        
        result = meters_to_miles(meters)
        
        assert result == 50.53

    def test_meters_to_miles_zero(self):
        meters = 0.0
        
        result = meters_to_miles(meters)
        
        assert result == 0.0

    def test_meters_to_miles_small_distance(self):
        meters = 100.0
        
        result = meters_to_miles(meters)
        
        assert result == 0.06

    def test_meters_to_miles_negative_raises_error(self):
        meters = -100.0
        
        with pytest.raises(ValueError) as exc_info:
            meters_to_miles(meters)
        assert "cannot be negative" in str(exc_info.value)

    def test_meters_to_miles_rounds_to_two_decimals(self):
        meters = 5432.1
        
        result = meters_to_miles(meters)
        
        assert result == 3.38
        assert len(str(result).split('.')[-1]) <= 2


class TestMilesToMeters:

    def test_miles_to_meters_exact_conversion(self):
        miles = 1.0
        
        result = miles_to_meters(miles)
        
        assert result == 1609.34

    def test_miles_to_meters_typical_distance(self):
        miles = 50.0
        
        result = miles_to_meters(miles)
        
        assert result == 80467.0

    def test_miles_to_meters_zero(self):
        miles = 0.0
        
        result = miles_to_meters(miles)
        
        assert result == 0.0

    def test_miles_to_meters_fractional_miles(self):
        miles = 0.5
        
        result = miles_to_meters(miles)
        
        assert result == 804.67

    def test_miles_to_meters_negative_raises_error(self):
        miles = -10.0
        
        with pytest.raises(ValueError) as exc_info:
            miles_to_meters(miles)
        assert "cannot be negative" in str(exc_info.value)

    def test_miles_to_meters_rounds_to_two_decimals(self):
        miles = 3.14159
        
        result = miles_to_meters(miles)
        
        assert len(str(result).split('.')[-1]) <= 2


class TestRoundTripConversion:

    def test_meters_to_miles_to_meters(self):
        original_meters = 5000.0
        
        miles = meters_to_miles(original_meters)
        result_meters = miles_to_meters(miles)
        
        assert abs(result_meters - original_meters) < 10.0

    def test_miles_to_meters_to_miles(self):
        original_miles = 25.5
        
        meters = miles_to_meters(original_miles)
        result_miles = meters_to_miles(meters)
        
        assert abs(result_miles - original_miles) < 0.01
