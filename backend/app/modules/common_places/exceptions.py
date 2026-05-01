class CommonPlaceError(Exception):
    """Base class for all common place exceptions"""

class InvalidCommonPlaceDataError(CommonPlaceError):
    """Bad input or missing fields"""

class CommonPlaceNotFoundError(CommonPlaceError):
    """when a common place doesn't exist"""

class CommonPlacePersistenceError(CommonPlaceError):
    """persistence error for common places"""

class DuplicateCommonPlaceError(CommonPlaceError):
    """when a common place with the same name already exists for the user"""

class MaxCommonPlacesError(CommonPlaceError):
    """when user tries to create more than 4 common places"""

