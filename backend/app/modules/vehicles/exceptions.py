
class VehicleError(Exception):
    """Base exception for vehicle-related errors"""
    pass


class VehicleNotFoundError(VehicleError):
    """Raised when a vehicle is not found"""
    pass


class DuplicateVehicleError(VehicleError):
    """Raised when trying to create a vehicle with duplicate name or license plate"""
    pass


class InvalidVehicleDataError(VehicleError):
    """Raised when vehicle data is invalid"""
    pass


class VehiclePersistenceError(VehicleError):
    """Raised when there's an error persisting vehicle data"""
    pass


class VehicleInUseError(VehicleError):
    """Raised when trying to delete a vehicle that is in use"""
    pass