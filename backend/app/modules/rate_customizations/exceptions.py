class RateCustomizationError(Exception):
    """Base class for all rate customization exceptions"""

class InvalidRateCustomizationDataError(RateCustomizationError):
    """Bad inout or missing fields"""

class RateCustomizationPersistenceError(RateCustomizationError):
    """persistence error for expenses"""

class RateCustomizationNotFoundError(RateCustomizationError):
    """for expenses that dont exist"""


class DuplicateRateCustomizationError(RateCustomizationError):
    """for when a rate customization with the same name already exists"""