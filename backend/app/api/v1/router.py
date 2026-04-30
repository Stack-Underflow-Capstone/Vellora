from fastapi import APIRouter
from app.modules.trips.router import router as trips_router
from app.modules.expenses.router import router as expenses_router
from app.modules.rate_customizations.router import router as rate_customizations_router
from app.modules.rate_categories.router import router as rate_categories_router
from app.modules.common_places.router import router as common_places_router
from app.modules.reports.router import router as reports_router
from app.modules.audit_trail.router import router as audit_trail_router
from app.modules.vehicles.router import router as vehicles_router
from app.modules.notifications.router import router as notifications_router
from app.modules.ai.router import router as ai_router

from app.modules.auth.router import router as auth_router


router = APIRouter(prefix="/api/v1")

router.include_router(trips_router)
router.include_router(expenses_router)
router.include_router(rate_customizations_router)
router.include_router(rate_categories_router)
router.include_router(common_places_router)
router.include_router(vehicles_router)
router.include_router(notifications_router)
router.include_router(ai_router)
router.include_router(auth_router)
router.include_router(reports_router)
router.include_router(audit_trail_router)

#Triggering Backend!