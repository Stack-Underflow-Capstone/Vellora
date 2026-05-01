class TripError(Exception):
    """Base class for all trip related exceptions."""

class InvalidTripDataError(TripError):
    """Bad input or missing fields."""

class TripAlreadyActiveError(TripError):
    """when a user tries to start a new trip while another is active"""

class TripPersistenceError(TripError):
    """database or commit error"""

class TripNotFoundError(TripError):
    """when a trip doesnt exist"""