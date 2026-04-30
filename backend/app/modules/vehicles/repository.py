from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.vehicles.models import Vehicle


class VehicleRepository:
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save(self, vehicle: Vehicle) -> Vehicle:
        self.db.add(vehicle)
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle
    
    async def get_by_id(self, vehicle_id: UUID, user_id: UUID) -> Optional[Vehicle]:
        result = await self.db.execute(
            select(Vehicle)
            .options(selectinload(Vehicle.user))
            .where(and_(Vehicle.id == vehicle_id, Vehicle.user_id == user_id))
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, user_id: UUID, include_inactive: bool = False) -> List[Vehicle]:
        query = select(Vehicle).options(selectinload(Vehicle.user)).where(Vehicle.user_id == user_id)
        
        if not include_inactive:
            query = query.where(Vehicle.is_active == True)
        
        query = query.order_by(desc(Vehicle.created_at))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_license_plate(self, user_id: UUID, license_plate: str) -> Optional[Vehicle]:
        result = await self.db.execute(
            select(Vehicle)
            .where(and_(Vehicle.user_id == user_id, Vehicle.license_plate == license_plate, Vehicle.is_active == True))
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, user_id: UUID, name: str) -> Optional[Vehicle]:
        result = await self.db.execute(
            select(Vehicle)
            .where(and_(Vehicle.user_id == user_id, Vehicle.name == name, Vehicle.is_active == True))
        )
        return result.scalar_one_or_none()
    
    async def update(self, vehicle: Vehicle) -> Vehicle:
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle
    
    async def delete(self, vehicle: Vehicle) -> None:
        await self.db.delete(vehicle)
        await self.db.commit()
    
    async def soft_delete(self, vehicle: Vehicle) -> Vehicle:
        vehicle.is_active = False
        return await self.update(vehicle)
    
    async def count_active_vehicles(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Vehicle).where(
                and_(Vehicle.user_id == user_id, Vehicle.is_active == True)
            )
        )
        return len(result.scalars().all())