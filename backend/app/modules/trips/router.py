from uuid import UUID
from app.container import get_db
from app.modules.trips.repository import TripRepo
from app.modules.trips.schemas import (
    CreateTripDTO,
    EditTripDTO,
    EndTripDTO,
    TripResponseDTO,
    TripCountsResponseDTO,
    ManualCreateTripDTO,
    MonthlyTripStatsResponseDTO,
    MonthlyTripDetailsResponseDTO,
    ScheduleTripDTO,
)
from app.modules.trips.service import TripsService
from app.core.error_handler  import error_handler
from app.core.dependencies import get_current_user, get_receipt_storage
from app.modules.users.models import User
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from app.infra.db import AsyncSession
from app.modules.rate_categories.repository import RateCategoryRepo
from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.expenses.repository import ExpenseRepo
from app.modules.expenses.receipts_repository import ExpenseReceiptRepo
from app.modules.expenses.receipts_service import ExpenseReceiptsService
from app.modules.expenses.schemas import ExpenseReceiptDTO
from app.modules.expenses.service import ExpensesService
from app.modules.vehicles.repository import VehicleRepository
from app.modules.audit_trail.repository import AuditTrailRepo
from app.modules.audit_trail.service import AuditTrailService
from app.modules.notifications.repository import NotificationRepository, DeviceTokenRepository
from app.modules.notifications.service import NotificationService
from app.infra.adapters.expo_notification_adapter import ExpoNotificationAdapter


router = APIRouter(prefix="/trips", tags=["Trips"])

def get_trips_service(db: AsyncSession = Depends(get_db)):
    trip_repo = TripRepo(db)
    expense_repo = ExpenseRepo(db)
    expense_service = ExpensesService(expense_repo, trip_repo)
    vehicle_repo = VehicleRepository(db)
    audit_service = AuditTrailService(AuditTrailRepo(db))   
    notification_repo = NotificationRepository(db)
    device_token_repo = DeviceTokenRepository(db)
    expo_adapter = ExpoNotificationAdapter(device_token_storage=device_token_repo)
    notification_service = NotificationService(notification_repo=notification_repo, device_token_repo=device_token_repo, push_adapter=expo_adapter, trip_repo=trip_repo)
    
    return TripsService(trip_repo, RateCategoryRepo(db), RateCustomizationRepo(db), vehicle_repo, expense_service, audit_service, notification_service)

def get_trip_receipts_service(
    db: AsyncSession = Depends(get_db),
    storage=Depends(get_receipt_storage),
):
    return ExpenseReceiptsService(TripRepo(db), ExpenseReceiptRepo(db), storage)

@router.post("/", response_model = TripResponseDTO)
@error_handler
async def start_trip(body: CreateTripDTO, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.start_trip(current_user.id, body)
    return TripResponseDTO.model_validate(trip)

@router.post("/manual", response_model = TripResponseDTO)
@error_handler
async def manual_create_trip(body: ManualCreateTripDTO, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.manual_create_trip(current_user.id, body)
    return TripResponseDTO.model_validate(trip)

@router.post("/scheduled", response_model=TripResponseDTO)
@error_handler
async def schedule_trip(body: ScheduleTripDTO, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.schedule_trip(current_user.id, body)
    return TripResponseDTO.model_validate(trip)

@router.patch("/{trip_id}", response_model=TripResponseDTO)
@error_handler
async def edit_trip(trip_id: UUID, body: EditTripDTO, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.edit_trip(current_user.id, trip_id, body)
    return TripResponseDTO.model_validate(trip)
   
@router.patch("/{trip_id}/end", response_model=TripResponseDTO)
@error_handler
async def end_trip(trip_id: UUID, body: EndTripDTO, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.end_trip(current_user.id, trip_id, body)
    return TripResponseDTO.model_validate(trip)

@router.patch("/{trip_id}/cancel", response_model=TripResponseDTO)
@error_handler
async def cancel_trip(trip_id: UUID, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.cancel_trip(current_user.id, trip_id)
    return TripResponseDTO.model_validate(trip)
    
@router.get("/active", response_model=TripResponseDTO)
@error_handler
async def get_active_trip(svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.get_active_trip(current_user.id)
    if not trip:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active trip found")
    return TripResponseDTO.model_validate(trip)

@router.get("/counts", response_model=TripCountsResponseDTO)
@error_handler
async def get_trip_counts(svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    total_trips = await svc.get_total_trips_count(current_user.id)
    total_scheduled = await svc.get_scheduled_trips_count(current_user.id)
    return TripCountsResponseDTO(total_trips=total_trips, total_scheduled=total_scheduled)

@router.get("/{trip_id}", response_model=TripResponseDTO)
@error_handler
async def get_trip(trip_id: UUID, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trip = await svc.get_trip_by_id(current_user.id, trip_id)
    return TripResponseDTO.model_validate(trip)

@router.post("/{trip_id}/receipts", response_model=ExpenseReceiptDTO, status_code=status.HTTP_201_CREATED)
@error_handler
async def upload_trip_receipt(
    trip_id: UUID,
    file: UploadFile = File(...),
    svc=Depends(get_trip_receipts_service),
    current_user: User = Depends(get_current_user),
):
    return await svc.upload_receipt(current_user.id, trip_id, None, file)

@router.get("/{trip_id}/receipts", response_model=list[ExpenseReceiptDTO])
@error_handler
async def list_trip_receipts(
    trip_id: UUID,
    svc=Depends(get_trip_receipts_service),
    current_user: User = Depends(get_current_user),
):
    return await svc.list_receipts(current_user.id, trip_id, None)

@router.get("/", response_model=list[TripResponseDTO])
@error_handler
async def get_user_trips(svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    trips = await svc.get_trips_by_userId(current_user.id)
    return [TripResponseDTO.model_validate(trip) for trip in trips]

@router.get("/monthly-stats/{month}/{year}", response_model=MonthlyTripStatsResponseDTO)
@error_handler
async def get_monthly_trip_stats(month: int, year: int, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    stats = await svc.get_monthly_stats(current_user.id, month, year)
    return MonthlyTripStatsResponseDTO(**stats)

@router.get("/monthly-details/{month}/{year}", response_model=MonthlyTripDetailsResponseDTO)
@error_handler
async def get_monthly_trip_details(month: int, year: int, svc: TripsService = Depends(get_trips_service), current_user: User = Depends(get_current_user)):
    details = await svc.get_monthly_trip_details(current_user.id, month, year)
    
    details['trips'] = [TripResponseDTO.model_validate(trip) for trip in details['trips']]
    
    return MonthlyTripDetailsResponseDTO(**details)
