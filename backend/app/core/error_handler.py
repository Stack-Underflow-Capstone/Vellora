import logging
from functools import wraps
from app.modules.trips.exceptions import InvalidTripDataError, TripAlreadyActiveError, TripNotFoundError, TripPersistenceError
from app.modules.expenses.exceptions import ExpenseNotFoundError, ExpensePersistenceError, InvalidExpenseDataError, DuplicateExpenseError
from app.modules.rate_customizations.exceptions import InvalidRateCustomizationDataError, RateCustomizationNotFoundError, RateCustomizationPersistenceError, DuplicateRateCustomizationError
from app.modules.rate_categories.exceptions import InvalidRateCategoryDataError, RateCategoryNotFoundError, RateCategoryPersistenceError, DuplicateRateCategoryError
from app.modules.common_places.exceptions import InvalidCommonPlaceDataError, CommonPlaceNotFoundError, CommonPlacePersistenceError, DuplicateCommonPlaceError, MaxCommonPlacesError
from app.modules.reports.exceptions import (
    InvalidReportDataError, ReportNotFoundError, ReportPersistenceError, 
    ReportPermissionError, ReportRateLimitError, ReportSystemLimitError,
    ReportExpiredError, ReportMaxRetriesError, ReportInvalidStateError
)
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
        
        #all
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
            raise HTTPException(status_code=500, detail="Unexpected server error")
        
    return wrapper