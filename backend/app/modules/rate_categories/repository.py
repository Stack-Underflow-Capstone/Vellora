from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.rate_categories.models import RateCategory

class RateCategoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, rate_category: RateCategory) -> RateCategory:
        self.db.add(rate_category)
        await self.db.commit()
        await self.db.refresh(rate_category)

        return rate_category
    
    async def get(self, category_id: UUID) -> RateCategory:
        return await self.db.scalar(select(RateCategory).where(RateCategory.id == category_id))
    
    async def delete(self, category : RateCategory) -> None:
        await self.db.delete(category)
        await self.db.commit()

    async def get_by_customization_id(self, customization_id: UUID):
        query = select(RateCategory).where(RateCategory.rate_customization_id == customization_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_customization_and_name(self, customization_id: UUID, name: str) -> RateCategory | None:
        query = select(RateCategory).where(
            RateCategory.rate_customization_id == customization_id,
            RateCategory.name == name
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()