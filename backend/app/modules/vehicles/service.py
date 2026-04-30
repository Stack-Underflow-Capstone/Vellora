from typing import List
from uuid import UUID

from app.modules.vehicles.models import Vehicle
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas import CreateVehicleDTO, EditVehicleDTO
from app.modules.vehicles.exceptions import DuplicateVehicleError, InvalidVehicleDataError, VehicleNotFoundError, VehiclePersistenceError


class VehicleService:
    
    def __init__(self, repository: VehicleRepository):
        self.repository = repository
    
    async def create_vehicle(self, user_id: UUID, data: CreateVehicleDTO) -> Vehicle:
        if not data.name or not data.name.strip():
            raise InvalidVehicleDataError("Vehicle name is required")
        
        if not data.license_plate or not data.license_plate.strip():
            raise InvalidVehicleDataError("License plate is required")
        
        if not data.model or not data.model.strip():
            raise InvalidVehicleDataError("Vehicle model is required")
        
        if data.year is not None and (data.year < 1900 or data.year > 2100):
            raise InvalidVehicleDataError("Vehicle year must be between 1900 and 2100")
        
        cleaned_name = data.name.strip()
        cleaned_license_plate = data.license_plate.strip().upper()
        cleaned_model = data.model.strip()
        
        existing_by_name = await self.repository.get_by_name(user_id, cleaned_name)
        if existing_by_name:
            raise DuplicateVehicleError("A vehicle with this name already exists")
        
        existing_by_license = await self.repository.get_by_license_plate(user_id, cleaned_license_plate)
        if existing_by_license:
            raise DuplicateVehicleError("A vehicle with this license plate already exists")
        
        try:
            vehicle = Vehicle(
                user_id=user_id,
                name=cleaned_name,
                license_plate=cleaned_license_plate,
                model=cleaned_model,
                year=data.year,
                color=data.color.strip() if data.color and data.color.strip() else None,
                is_active=True
            )
            
            return await self.repository.save(vehicle)
        except Exception as e:
            raise VehiclePersistenceError("Failed to create vehicle") from e
    
    async def get_user_vehicles(self, user_id: UUID, include_inactive: bool = False) -> List[Vehicle]:
        return await self.repository.get_by_user(user_id, include_inactive)
    
    async def get_vehicle(self, user_id: UUID, vehicle_id: UUID) -> Vehicle:
        vehicle = await self.repository.get_by_id(vehicle_id, user_id)
        if not vehicle:
            raise VehicleNotFoundError("Vehicle not found")
        return vehicle
    
    async def update_vehicle(self, user_id: UUID, vehicle_id: UUID, data: EditVehicleDTO) -> Vehicle:
        vehicle = await self.get_vehicle(user_id, vehicle_id)
        
        if data.year is not None and (data.year < 1900 or data.year > 2100):
            raise InvalidVehicleDataError("Vehicle year must be between 1900 and 2100")
        
        if data.name is not None:
            if not data.name or not data.name.strip():
                raise InvalidVehicleDataError("Vehicle name cannot be empty")
            
            cleaned_name = data.name.strip()
            if cleaned_name != vehicle.name:
                existing = await self.repository.get_by_name(user_id, cleaned_name)
                if existing:
                    raise DuplicateVehicleError("A vehicle with this name already exists")
            vehicle.name = cleaned_name
        
        if data.license_plate is not None:
            if not data.license_plate or not data.license_plate.strip():
                raise InvalidVehicleDataError("License plate cannot be empty")
            
            cleaned_license_plate = data.license_plate.strip().upper()
            if cleaned_license_plate != vehicle.license_plate:
                existing = await self.repository.get_by_license_plate(user_id, cleaned_license_plate)
                if existing:
                    raise DuplicateVehicleError("A vehicle with this license plate already exists")
            vehicle.license_plate = cleaned_license_plate
        
        if data.model is not None:
            if not data.model or not data.model.strip():
                raise InvalidVehicleDataError("Vehicle model cannot be empty")
            vehicle.model = data.model.strip()
        
        if data.year is not None:
            vehicle.year = data.year
        
        if data.color is not None:
            vehicle.color = data.color.strip() if data.color and data.color.strip() else None
        
        if data.is_active is not None:
            vehicle.is_active = data.is_active
        
        try:
            return await self.repository.update(vehicle)
        except Exception as e:
            raise VehiclePersistenceError("Failed to update vehicle") from e
    
    async def delete_vehicle(self, user_id: UUID, vehicle_id: UUID) -> None:
        vehicle = await self.get_vehicle(user_id, vehicle_id)
        
        try:
            await self.repository.delete(vehicle)
        except Exception as e:
            raise VehiclePersistenceError("Failed to delete vehicle") from e