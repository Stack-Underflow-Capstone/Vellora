import logging
from functools import wraps
from app.modules.trips.exceptions import InvalidTripDataError, TripAlreadyActiveError, TripNotFoundError, TripPersistenceError
from app.modules.expenses.exceptions import (
    DuplicateExpenseError,
    ExpenseNotFoundError,
    ExpensePersistenceError,
    InvalidExpenseDataError,
    ReceiptNotFoundError,
    ReceiptStorageConfigError,
    ReceiptUploadError,
    ReceiptValidationError,
)
from app.modules.rate_customizations.exceptions import InvalidRateCustomizationDataError, RateCustomizationNotFoundError, RateCustomizationPersistenceError, DuplicateRateCustomizationError
from app.modules.rate_categories.exceptions import InvalidRateCategoryDataError, RateCategoryNotFoundError, RateCategoryPersistenceError, DuplicateRateCategoryError
from app.modules.common_places.exceptions import InvalidCommonPlaceDataError, CommonPlaceNotFoundError, CommonPlacePersistenceError, DuplicateCommonPlaceError, MaxCommonPlacesError
from app.modules.audit_trail.exceptions import AuditTrailNotFoundError, AuditTrailPersistenceError
from app.modules.vehicles.exceptions import VehicleNotFoundError, DuplicateVehicleError, InvalidVehicleDataError, VehiclePersistenceError, VehicleInUseError
from app.modules.reports.exceptions import (
    InvalidReportDataError, ReportNotFoundError, ReportPersistenceError, 
    ReportPermissionError, ReportRateLimitError, ReportSystemLimitError,
    ReportExpiredError, ReportMaxRetriesError, ReportInvalidStateError,
    InvalidMonthAnalyticsError, InvalidDataAnalyticsError
)

from app.modules.users.exceptions import DuplicateUsernameError, InvalidPasswordError
from app.modules.reports.exceptions import InvalidReportDataError, ReportNotFoundError, ReportPersistenceError, ReportPermissionError, ReportRateLimitError, ReportSystemLimitError,ReportExpiredError, ReportMaxRetriesError, ReportInvalidStateError
from app.modules.notifications.exceptions import NotificationNotFoundError, NotificationPersistenceError, InvalidNotificationDataError,NotificationDeliveryError, DeviceTokenError, DuplicateDeviceTokenError
from app.modules.ai.exceptions import AiConfigError, AiProviderError, AiRateLimitError, AiValidationError, WeatherProviderError

from fastapi import HTTPException



logger = logging.getLogger(__name__)

def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        
        except HTTPException:
            raise
        
        #trips
        except InvalidTripDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except TripAlreadyActiveError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except TripPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except TripNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        #expenses
        except InvalidExpenseDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateExpenseError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except ExpensePersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except ExpenseNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ReceiptValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ReceiptNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ReceiptStorageConfigError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except ReceiptUploadError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        #rateCustomizations
        except InvalidRateCustomizationDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateRateCustomizationError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except RateCustomizationPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except RateCustomizationNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        #rateCategories
        except InvalidRateCategoryDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateRateCategoryError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except RateCategoryPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except RateCategoryNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

        #common_places
        except InvalidCommonPlaceDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except MaxCommonPlacesError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateCommonPlaceError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except CommonPlacePersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except CommonPlaceNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        #vehicles
        except InvalidVehicleDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except DuplicateVehicleError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except VehicleInUseError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except VehiclePersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except VehicleNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        
        #reports
        except InvalidReportDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ReportNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ReportPermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except ReportRateLimitError as e:
            raise HTTPException(status_code=429, detail=str(e))
        except ReportSystemLimitError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except ReportExpiredError as e:
            raise HTTPException(status_code=410, detail=str(e))
        except ReportMaxRetriesError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ReportInvalidStateError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ReportPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        #analytics
        except InvalidMonthAnalyticsError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except InvalidDataAnalyticsError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
        #audit trails
        except AuditTrailNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except AuditTrailPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        #notifications
        except InvalidNotificationDataError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotificationNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except DuplicateDeviceTokenError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except DeviceTokenError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotificationDeliveryError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except NotificationPersistenceError as e:
            raise HTTPException(status_code=500, detail=str(e))

        #ai
        except AiConfigError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except AiProviderError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except WeatherProviderError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except AiRateLimitError as e:
            raise HTTPException(status_code=429, detail=str(e))
        except AiValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        #users
        except DuplicateUsernameError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except InvalidPasswordError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        #all
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
            raise HTTPException(status_code=500, detail="Unexpected server error")
        
    return wrapper
