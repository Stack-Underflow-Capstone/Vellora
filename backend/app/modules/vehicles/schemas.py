from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateVehicleDTO(BaseModel):
    name: str
    license_plate: str
    model: str
    year: int | None = None
    color: str | None = None


class EditVehicleDTO(BaseModel):
    name: str | None = None
    license_plate: str | None = None
    model: str | None = None
    year: int | None = None
    color: str | None = None
    is_active: bool | None = None
    


class VehicleResponse(BaseModel):
    id: UUID
    name: str
    license_plate: str
    model: str
    year: Optional[int]
    color: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VehicleListResponse(BaseModel):
    vehicles: list[VehicleResponse]
    total: int