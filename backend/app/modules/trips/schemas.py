import datetime
from typing import List
from uuid import UUID
from app.modules.trips.models import Trip, TripStatus
from app.modules.trips.utils.crypto import decrypt_address, decrypt_geometry
from app.modules.trips.utils.distance import meters_to_miles
from app.modules.expenses.schemas import CreateExpenseDTO
from pydantic import BaseModel, Field, field_validator, ValidationError

class CreateTripDTO(BaseModel):
    start_address: str
    purpose: str | None = None
    vehicle_id: UUID | None = None
    rate_customization_id: UUID
    rate_category_id: UUID
    
    @field_validator('rate_customization_id', 'rate_category_id', 'vehicle_id')
    @classmethod
    def validate_uuids(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = v.strip()
            if len(v) > 36:
                v = v[:36]
        return v

class EndTripDTO(BaseModel):
    end_address: str
    geometry: dict
    distance_meters: float
    
    @field_validator('distance_meters')
    @classmethod
    def validate_distance(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Distance must be non-negative")
        return v
    
    @property
    def miles(self) -> float:
        return meters_to_miles(self.distance_meters)

class EditTripDTO(BaseModel):
    purpose: str | None = None
    vehicle_id: UUID | None = None
    miles: float | None = None
    rate_customization_id: UUID | None = None
    rate_category_id: UUID | None = None
    scheduled_start_at: datetime.datetime | None = None
    scheduled_end_at: datetime.datetime | None = None
    calendar_provider: str | None = None
    calendar_event_id: str | None = None
    calendar_event_url: str | None = None
    status: TripStatus | None = None
    
    @field_validator('miles')
    @classmethod
    def validate_miles(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError("Miles must be non-negative")
        return v

    @field_validator('scheduled_end_at')
    @classmethod
    def validate_scheduled_end(cls, v: datetime.datetime | None, info):
        if v is None:
            return v
        start = info.data.get('scheduled_start_at')
        if start is not None and v <= start:
            raise ValueError("Scheduled end time must be after start time")
        return v

class ManualCreateTripDTO(BaseModel):
    start_address: str
    end_address: str
    purpose: str | None = None
    vehicle_id: UUID | None = None
    miles: float
    geometry: dict | None = None
    started_at: datetime.datetime
    ended_at: datetime.datetime
    rate_customization_id: UUID
    rate_category_id: UUID
    expenses: List[CreateExpenseDTO] | None = None 

class ScheduleTripDTO(BaseModel):
    start_address: str | None = None
    end_address: str | None = None
    purpose: str | None = None
    vehicle_id: UUID | None = None
    rate_customization_id: UUID
    rate_category_id: UUID
    scheduled_start_at: datetime.datetime
    scheduled_end_at: datetime.datetime
    calendar_provider: str | None = None
    calendar_event_id: str | None = None
    calendar_event_url: str | None = None

class TripExpenseReceiptDTO(BaseModel):
    id: str
    file_name: str
    content_type: str
    size_bytes: int
    created_at: datetime.datetime


class ExpenseResponseDTO(BaseModel):
    id: str
    type: str
    amount: float
    created_at: datetime.datetime
    receipts: List[TripExpenseReceiptDTO] = []

class VehicleInfo(BaseModel):
    id: UUID
    name: str
    license_plate: str
    model: str
    
    class Config:
        from_attributes = True


class TripResponseDTO(BaseModel):
    id: str
    status: TripStatus
    start_address: str | None = None
    end_address: str | None = None
    geometry: dict | None = None
    purpose: str | None = None
    vehicle_id: UUID | None = None
    vehicle: VehicleInfo | None = None
    miles: float | None = None
    reimbursement_rate: float | None = None
    mileage_reimbursement_total: float | None = None
    expense_reimbursement_total: float | None = None
    total_reimbursement: float | None = None
    started_at: datetime.datetime
    scheduled_start_at: datetime.datetime | None = None
    scheduled_end_at: datetime.datetime | None = None
    ended_at: datetime.datetime | None = None
    updated_at: datetime.datetime
    rate_customization_id: UUID
    rate_category_id: UUID
    calendar_provider: str | None = None
    calendar_event_id: str | None = None
    calendar_event_url: str | None = None
    expenses: List[ExpenseResponseDTO] = []
    receipts: List[TripExpenseReceiptDTO] = []

    @classmethod
    def model_validate(cls, trip: Trip):

        data = {
            #convert uuid to str
            "id": str(trip.id),
            "status": trip.status,
            "start_address": decrypt_address(trip.start_address_encrypted) if trip.start_address_encrypted else None,
            "end_address": decrypt_address(trip.end_address_encrypted) if trip.end_address_encrypted else None,
            "purpose": trip.purpose,
            "vehicle_id": trip.vehicle_id,
            "vehicle": VehicleInfo.model_validate(trip.vehicle) if trip.vehicle else None,
            "miles": trip.miles,
            "reimbursement_rate": trip.reimbursement_rate,
            "geometry": decrypt_geometry(trip.geometry_encrypted) if trip.geometry_encrypted else None,
            "mileage_reimbursement_total": trip.mileage_reimbursement_total,
            "expense_reimbursement_total": trip.expense_reimbursement_total,
            "total_reimbursement": (trip.mileage_reimbursement_total or 0) + (trip.expense_reimbursement_total or 0),
            "started_at": trip.started_at,
            "scheduled_start_at": trip.scheduled_start_at,
            "scheduled_end_at": trip.scheduled_end_at,
            "ended_at": trip.ended_at,
            "updated_at": trip.updated_at,
            "rate_customization_id": trip.rate_customization_id,
            "rate_category_id": trip.rate_category_id,
            "calendar_provider": trip.calendar_provider,
            "calendar_event_id": trip.calendar_event_id,
            "calendar_event_url": trip.calendar_event_url,
            "expenses": [
                ExpenseResponseDTO(
                    id=str(e.id),
                    type=e.type,
                    amount=e.amount,
                    created_at=e.created_at,
                    receipts=[
                        TripExpenseReceiptDTO(
                            id=str(r.id),
                            file_name=r.file_name,
                            content_type=r.content_type,
                            size_bytes=r.size_bytes,
                            created_at=r.created_at,
                        )
                        for r in getattr(e, "receipts", [])
                    ],
                )
                for e in getattr(trip, "expenses", [])
            ],
            "receipts": [
                TripExpenseReceiptDTO(
                    id=str(r.id),
                    file_name=r.file_name,
                    content_type=r.content_type,
                    size_bytes=r.size_bytes,
                    created_at=r.created_at,
                )
                for r in getattr(trip, "receipts", [])
            ],
        }

        # Create and return a new instance of TripResponseDTO
        return cls(**data)

    class Config:
        from_attributes = True

class MonthlyTripStatsResponseDTO(BaseModel):
    month: int
    year: int
    total_drives: int
    total_miles: float
    total_reimbursement: float

class TripCountsResponseDTO(BaseModel):
    total_trips: int
    total_scheduled: int
class MonthlyTripDetailsResponseDTO(BaseModel):
    trips: List[TripResponseDTO]
    month: int
    year: int
    total_drives: int
    total_miles: float
    total_mileage_reimbursement: float
    total_expense_reimbursement: float
    total_reimbursement: float
