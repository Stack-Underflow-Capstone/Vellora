from datetime import datetime, timezone
import logging
from uuid import UUID
from app.modules.trips.repository import TripRepo
from app.modules.trips.schemas import (
    CreateTripDTO,
    EditTripDTO,
    EndTripDTO,
    ManualCreateTripDTO,
    ScheduleTripDTO,
    TripResponseDTO,
)
from app.modules.trips.utils.crypto import encrypt_address, encrypt_geometry
from app.modules.trips.models import Trip, TripStatus
from app.modules.trips.exceptions import InvalidTripDataError, TripNotFoundError, TripPersistenceError, TripAlreadyActiveError
from app.modules.rate_categories.repository import RateCategoryRepo
from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.rate_customizations.exceptions import RateCustomizationNotFoundError
from app.modules.rate_categories.exceptions import InvalidRateCategoryDataError, RateCategoryNotFoundError
from app.modules.expenses.models import Expense
from app.modules.expenses.repository import ExpenseRepo
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.exceptions import VehicleNotFoundError
from app.modules.audit_trail.service import AuditTrailService
from app.modules.audit_trail.models import AuditAction
from app.modules.notifications.service import NotificationService


class TripsService:
    def __init__(self, repo: TripRepo, category_repo: RateCategoryRepo, customization_repo: RateCustomizationRepo, vehicle_repo: VehicleRepository = None, expense_service=None, audit_service: AuditTrailService = None, notification_service: NotificationService = None):
        self.repo = repo
        self.category_repo = category_repo
        self.customization_repo = customization_repo
        self.vehicle_repo = vehicle_repo
        self.expense_service = expense_service
        self.audit_service = audit_service
        self.notification_service = notification_service

    async def _validate_vehicle_ownership(self, user_id: UUID, vehicle_id: UUID):
        if not self.vehicle_repo:
            return
            
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id, user_id)
        if not vehicle:
            raise VehicleNotFoundError("Vehicle not found or not owned by user")
        
        if not vehicle.is_active:
            raise InvalidTripDataError("Cannot use inactive vehicle for trips")

    async def _validate_vehicle_ownership(self, user_id: UUID, vehicle_id: UUID):
        if not self.vehicle_repo:
            return
            
        vehicle = await self.vehicle_repo.get_by_id(vehicle_id, user_id)
        if not vehicle:
            raise VehicleNotFoundError("Vehicle not found or not owned by user")
        
        if not vehicle.is_active:
            raise InvalidTripDataError("Cannot use inactive vehicle for trips")

    async def start_trip(self, user_id: UUID, data: CreateTripDTO):

        if not data.start_address.strip():
            raise InvalidTripDataError("Start address is required")
        
        # Check if user already has an active trip
        active_trip = await self.repo.get_active_trip(user_id)
        if active_trip:
            raise TripAlreadyActiveError("You already have an active trip")
        
        customization = await self.customization_repo.get(data.rate_customization_id, user_id)
        if not customization:
            customization = await self.customization_repo.get(data.rate_customization_id)
            if customization:
                from app.modules.users.models import User
                from sqlalchemy import select
                irs_user_result = await self.customization_repo.db.execute(
                    select(User.id).where(User.email == 'system@irs.gov')
                )
                irs_user_id = irs_user_result.scalar_one_or_none()
                
                if not (irs_user_id and customization.user_id == irs_user_id):
                    customization = None
        
        if not customization:
            raise RateCustomizationNotFoundError("Rate customization not found or not accessible to user")
        
        category = await self.category_repo.get(data.rate_category_id)
        if not category:
            raise RateCategoryNotFoundError("Rate category not found")

        if category.rate_customization_id != customization.id:
            raise InvalidRateCategoryDataError("Category does not belong to this customization")
        
        if data.vehicle_id:
            await self._validate_vehicle_ownership(user_id, data.vehicle_id)
        
        reimbursement_rate = category.cost_per_mile

        try:
            encrypted_address = encrypt_address(data.start_address)

            trip = Trip(
                user_id=user_id,
                start_address_encrypted = encrypted_address,
                purpose = data.purpose,
                vehicle_id = data.vehicle_id,
                reimbursement_rate=reimbursement_rate,
                rate_customization_id=data.rate_customization_id,
                rate_category_id=data.rate_category_id,
            )
                    
            saved_trip = await self.repo.save(trip)
            
            #log audit trail
            if self.audit_service:
                await self.audit_service.log_action(
                    user_id=user_id,
                    action=AuditAction.TRIP_STARTED,
                    resource="trip",
                    resource_id=str(saved_trip.id),
                    details=f"Started trip to {data.start_address[:50]}..."
                )
            
            #for when scheduled trips are implemnted
            if self.notification_service:
                try:
                    #check if trip is scheduled
                    # is_scheduled? (implement check later)
                    # await self.notification_service.notify_trip_started(
                    #     user_id=user_id,
                    #     trip_id=saved_trip.id,
                    #     is_scheduled=is_scheduled
                    # )
                    pass
                except Exception as e:
                    logging.getLogger(__name__).error(f"Failed to send trip start notification: {e}")
                
            return saved_trip

        except Exception as e:
            raise TripPersistenceError(f"Unexpected error occurred while saving trip: {e}") from e
    
    async def manual_create_trip(self, user_id: UUID, data: ManualCreateTripDTO):
        if not data.start_address.strip():
            raise InvalidTripDataError("Start address is required")
        
        if not data.end_address.strip():
            raise InvalidTripDataError("End address is required")
        
        if data.miles <= 0:
            raise InvalidTripDataError("Miles must be greater than 0")
        
        if data.ended_at <= data.started_at:
            raise InvalidTripDataError("End time must be after start time")
        
        customization = await self.customization_repo.get(data.rate_customization_id)
        if not customization:
            raise RateCustomizationNotFoundError("Rate customization not found")
        
        category = await self.category_repo.get(data.rate_category_id)
        if not category:
            raise RateCategoryNotFoundError("Rate category not found")

        if category.rate_customization_id != customization.id:
            raise InvalidRateCategoryDataError("Category does not belong to this customization")
        
        if data.vehicle_id:
            await self._validate_vehicle_ownership(user_id, data.vehicle_id)
        
        try:
            encrypted_start_address = encrypt_address(data.start_address)
            encrypted_end_address = encrypt_address(data.end_address)
            encrypted_geometry = encrypt_geometry(data.geometry) if data.geometry else None
            
            reimbursement_rate = category.cost_per_mile
            mileage_total = data.miles * reimbursement_rate

            trip = Trip(
                user_id=user_id,
                status=TripStatus.completed,
                start_address_encrypted=encrypted_start_address,
                end_address_encrypted=encrypted_end_address,
                purpose=data.purpose,
                vehicle_id=data.vehicle_id,
                miles=data.miles,
                geometry_encrypted=encrypted_geometry,
                reimbursement_rate=reimbursement_rate,
                mileage_reimbursement_total=mileage_total,
                expense_reimbursement_total=0.0, 
                started_at=data.started_at,
                ended_at=data.ended_at,
                rate_customization_id=data.rate_customization_id,
                rate_category_id=data.rate_category_id,
            )
            
            saved_trip = await self.repo.save(trip)
            
            #log audit trail
            if self.audit_service:
                await self.audit_service.log_action(
                    user_id=user_id,
                    action=AuditAction.TRIP_MANUAL_CREATED,
                    resource="trip",
                    resource_id=str(saved_trip.id),
                    details=f"Manual trip created: {saved_trip.miles} miles, ${saved_trip.mileage_reimbursement_total:.2f} reimbursement"
                )
            
            if data.expenses and self.expense_service:
                for expense_data in data.expenses:
                    await self.expense_service.create_expense(user_id, saved_trip.id, expense_data)
                    
            return saved_trip

        except Exception as e:
            raise TripPersistenceError(f"Unexpected error occurred while saving manual trip: {e}") from e

    async def schedule_trip(self, user_id: UUID, data: ScheduleTripDTO):
        if data.scheduled_end_at <= data.scheduled_start_at:
            raise InvalidTripDataError("Scheduled end time must be after start time")

        customization = await self.customization_repo.get(data.rate_customization_id, user_id)
        if not customization:
            customization = await self.customization_repo.get(data.rate_customization_id)
            if customization:
                from app.modules.users.models import User
                from sqlalchemy import select
                irs_user_result = await self.customization_repo.db.execute(
                    select(User.id).where(User.email == 'system@irs.gov')
                )
                irs_user_id = irs_user_result.scalar_one_or_none()

                if not (irs_user_id and customization.user_id == irs_user_id):
                    customization = None

        if not customization:
            raise RateCustomizationNotFoundError("Rate customization not found or not accessible to user")

        category = await self.category_repo.get(data.rate_category_id)
        if not category:
            raise RateCategoryNotFoundError("Rate category not found")

        if category.rate_customization_id != customization.id:
            raise InvalidRateCategoryDataError("Category does not belong to this customization")

        if data.vehicle_id:
            await self._validate_vehicle_ownership(user_id, data.vehicle_id)

        reimbursement_rate = category.cost_per_mile

        try:
            encrypted_start_address = (
                encrypt_address(data.start_address)
                if data.start_address and data.start_address.strip()
                else None
            )
            encrypted_end_address = (
                encrypt_address(data.end_address)
                if data.end_address and data.end_address.strip()
                else None
            )

            trip = Trip(
                user_id=user_id,
                status=TripStatus.scheduled,
                start_address_encrypted=encrypted_start_address,
                end_address_encrypted=encrypted_end_address,
                purpose=data.purpose,
                vehicle_id=data.vehicle_id,
                reimbursement_rate=reimbursement_rate,
                rate_customization_id=data.rate_customization_id,
                rate_category_id=data.rate_category_id,
                scheduled_start_at=data.scheduled_start_at,
                scheduled_end_at=data.scheduled_end_at,
                calendar_provider=data.calendar_provider,
                calendar_event_id=data.calendar_event_id,
                calendar_event_url=data.calendar_event_url,
            )

            saved_trip = await self.repo.save(trip)

            return saved_trip

        except Exception as e:
            raise TripPersistenceError(f"Unexpected error occurred while scheduling trip: {e}") from e
    
    async def get_trip_by_id(self, user_id: UUID, trip_id: UUID):
        trip = await self.repo.get(trip_id, user_id)

        if trip:
            return trip
        
        raise TripNotFoundError("Trip doesn't exist or not owned by user")
    
    async def end_trip(self, user_id: UUID, trip_id: UUID, data: EndTripDTO):
        if not data.end_address.strip():
            raise InvalidTripDataError("End address is required")
        
        #check if trip exists first
        trip = await self.get_trip_by_id(user_id, trip_id)
      
        if trip.status == TripStatus.completed:
            raise InvalidTripDataError("Trip already ended")
        
        if trip.status == TripStatus.cancelled:
            raise InvalidTripDataError("Cannot end a cancelled trip")
        
        #idk if i wanna add this. just to make sure start and end addrr arent the same
        # if data.end_address.strip().lower() == trip.start_address_encrypted:
        #     raise InvalidTripDataError("Start and end addresses cannot be the same")

        miles = data.miles
        if miles < 0:
            raise InvalidTripDataError("Miles must be non-negative")
                
        try: 

            trip.miles = miles
            trip.geometry_encrypted = encrypt_geometry(data.geometry)
            trip.mileage_reimbursement_total = miles * (trip.reimbursement_rate or 0.0)
            trip.status = TripStatus.completed
            trip.end_address_encrypted = encrypt_address(data.end_address)
            trip.ended_at = datetime.now(timezone.utc)

            saved_trip = await self.repo.save(trip)
            
            #log audit trail
            if self.audit_service:
                await self.audit_service.log_action(
                    user_id=trip.user_id,
                    action=AuditAction.TRIP_COMPLETED,
                    resource="trip",
                    resource_id=str(trip.id),
                    details=f"Trip completed: {miles:.2f} miles, ${trip.mileage_reimbursement_total:.2f} reimbursement"
                )
            
            #for when scheduled trips are implemnted
            if self.notification_service:
                try:
                    # Future: check if trip is scheduled
                    # is_scheduled (implement later)
                    # await self.notification_service.notify_trip_ended(
                    #     user_id=user_id,
                    #     trip_id=saved_trip.id,
                    #     is_scheduled=is_scheduled
                    # )
                    pass
                except Exception as e:
                    logging.getLogger(__name__).error(f"Failed to send trip end notification: {e}")

            return saved_trip
               
        except Exception as e:
            await self.repo.db.rollback()
            raise TripPersistenceError(f"Unexpected error occurred while ending trip: {e}") from e

        
    async def edit_trip(self, user_id: UUID, trip_id: UUID, data: EditTripDTO):
        #check if trip exists first
        trip = await self.get_trip_by_id(user_id, trip_id)
        
        try:

            if data.status is not None:
                trip.status = data.status
                
            if data.purpose is not None:
                trip.purpose = data.purpose

            if data.vehicle_id is not None:
                await self._validate_vehicle_ownership(user_id, data.vehicle_id)
                trip.vehicle_id = data.vehicle_id
                
            if data.miles is not None:
                if data.miles < 0:
                    raise InvalidTripDataError("Miles must be non-negative")
                trip.miles = data.miles

                if trip.reimbursement_rate:
                    trip.mileage_reimbursement_total = data.miles * trip.reimbursement_rate

            if data.rate_customization_id is not None:
                customization = await self.customization_repo.get(data.rate_customization_id)
                if not customization:
                    raise RateCustomizationNotFoundError("Rate customization not found")
                trip.rate_customization_id = data.rate_customization_id

            if data.rate_category_id is not None:
                category = await self.category_repo.get(data.rate_category_id)
                if not category:
                    raise RateCategoryNotFoundError("Rate category not found")

                if data.rate_customization_id is not None:
                    customization_id = data.rate_customization_id
                else:
                    customization_id = trip.rate_customization_id

                if category.rate_customization_id != customization_id:
                    raise InvalidRateCategoryDataError("Category does not belong to this customization")

                trip.rate_category_id = data.rate_category_id
                trip.reimbursement_rate = category.cost_per_mile

            if data.scheduled_start_at is not None:
                trip.scheduled_start_at = data.scheduled_start_at

            if data.scheduled_end_at is not None:
                start_at = data.scheduled_start_at or trip.scheduled_start_at
                if start_at and data.scheduled_end_at <= start_at:
                    raise InvalidTripDataError("Scheduled end time must be after start time")
                trip.scheduled_end_at = data.scheduled_end_at

            if data.calendar_provider is not None:
                trip.calendar_provider = data.calendar_provider

            if data.calendar_event_id is not None:
                trip.calendar_event_id = data.calendar_event_id

            if data.calendar_event_url is not None:
                trip.calendar_event_url = data.calendar_event_url

            return await self.repo.save(trip)
        
        except Exception as e:
            await self.repo.db.rollback()
            raise TripPersistenceError(f"Unexpected error occurred while editing trip: {e}") from e

    async def cancel_trip(self, user_id: UUID, trip_id: UUID):

        trip = await self.get_trip_by_id(user_id, trip_id)

        if trip.status not in (TripStatus.active, TripStatus.scheduled):
            raise InvalidTripDataError("Only active or scheduled trips can be cancelled")

        try:
            trip.status = TripStatus.cancelled
            trip.ended_at = datetime.now(timezone.utc)
            return await self.repo.save(trip)

        except Exception as e:
            await self.repo.db.rollback()
            raise TripPersistenceError(f"Unexpected error occurred while cancelling trip {e}") from e


    async def get_active_trip(self, user_id: UUID):
        return await self.repo.get_active_trip(user_id)

    async def get_trips_by_userId(self, user_id: UUID):
        return await self.repo.get_user_trips(user_id)
    
    async def get_monthly_stats(self, user_id: UUID, month: int, year: int):
        stats = await self.repo.get_monthly_stats(user_id, month, year)
        
        stats['total_reimbursement'] = stats['total_mileage_reimbursement'] + stats['total_expense_reimbursement']
        stats['month'] = month
        stats['year'] = year
        
        return stats

    async def get_monthly_trip_details(self, user_id: UUID, month: int, year: int):
       
        trips = await self.repo.get_monthly_trips(user_id, month, year)
        stats = await self.repo.get_monthly_stats(user_id, month, year)
        
        total_reimbursement = stats['total_mileage_reimbursement'] + stats['total_expense_reimbursement']
        
        return {
            'trips': trips,
            'month': month,
            'year': year,
            'total_drives': stats['total_drives'],
            'total_miles': stats['total_miles'],
            'total_mileage_reimbursement': stats['total_mileage_reimbursement'],
            'total_expense_reimbursement': stats['total_expense_reimbursement'],
            'total_reimbursement': total_reimbursement
        }
    
    async def get_total_trips_count(self, user_id: UUID) -> int:
        return await self.repo.get_total_trips_count(user_id)

    async def get_scheduled_trips_count(self, user_id: UUID) -> int:
        return await self.repo.get_scheduled_trips_count(user_id)

    
