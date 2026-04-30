from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, extract
from app.modules.trips.models import Trip

class TripRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, trip: Trip) -> Trip:

        self.db.add(trip)
        await self.db.commit()
        result = await self.db.execute(
            select(Trip)
            .options(
                selectinload(Trip.expenses),
                selectinload(Trip.receipts),
                selectinload(Trip.rate_customization),
                selectinload(Trip.rate_category),
                selectinload(Trip.vehicle),
            )
            .where(Trip.id == trip.id)
        )
        return result.scalar_one()
    
    async def get(self, trip_id: UUID, user_id: UUID = None):
        query = select(Trip).options(
            selectinload(Trip.expenses),
            selectinload(Trip.receipts),
            selectinload(Trip.rate_customization),
            selectinload(Trip.rate_category),
            selectinload(Trip.vehicle),
        ).where(Trip.id == trip_id)
        
        if user_id is not None:
            query = query.where(Trip.user_id == user_id)
            
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_trips(self, user_id: UUID):
        result = await self.db.execute(
            select(Trip)
            .options(
                selectinload(Trip.expenses),
                selectinload(Trip.receipts),
                selectinload(Trip.rate_customization),
                selectinload(Trip.rate_category),
                selectinload(Trip.vehicle),
            )
            .where(Trip.user_id == user_id)
            .order_by(Trip.started_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_trip(self, user_id: UUID):
        result = await self.db.execute(
            select(Trip)
            .options(
                selectinload(Trip.expenses),
                selectinload(Trip.receipts),
                selectinload(Trip.rate_customization),
                selectinload(Trip.rate_category),
                selectinload(Trip.vehicle),
            )
            .where(Trip.user_id == user_id, Trip.status == "active")
        )
        return result.scalar_one_or_none()

    async def get_monthly_stats(self, user_id: UUID, month: int, year: int):
        result = await self.db.execute(
            select(Trip)
            .where(
                Trip.user_id == user_id,
                Trip.status == "completed",
                extract('year', Trip.started_at) == year,
                extract('month', Trip.started_at) == month
            )
        )
        trips = result.scalars().all()
        
        total_drives = len(trips)
        total_miles = sum(trip.miles or 0 for trip in trips)
        total_mileage_reimbursement = sum(trip.mileage_reimbursement_total or 0 for trip in trips)
        total_expense_reimbursement = sum(trip.expense_reimbursement_total or 0 for trip in trips)
        
        return {
            'total_drives': total_drives,
            'total_miles': total_miles,
            'total_mileage_reimbursement': total_mileage_reimbursement,
            'total_expense_reimbursement': total_expense_reimbursement
        }

    async def get_total_trips_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Trip)
            .where(
                Trip.user_id == user_id,
                Trip.status == "completed",
            )
        )
        return len(result.scalars().all())

    async def get_scheduled_trips_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(Trip)
            .where(
                Trip.user_id == user_id,
                Trip.status == "scheduled",
            )
        )
        return len(result.scalars().all())
    async def get_monthly_trips(self, user_id: UUID, month: int, year: int):
        result = await self.db.execute(
            select(Trip)
            .options(
                selectinload(Trip.expenses),
                selectinload(Trip.receipts),
                selectinload(Trip.rate_customization),
                selectinload(Trip.rate_category),
                selectinload(Trip.vehicle),
            )
            .where(
                Trip.user_id == user_id,
                Trip.status == "completed",
                extract('year', Trip.started_at) == year,
                extract('month', Trip.started_at) == month
            )
            .order_by(Trip.started_at.desc())
        )
        return result.scalars().all()
