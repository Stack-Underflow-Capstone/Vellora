from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common_places.models import CommonPlace


class CommonPlaceRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, common_place: CommonPlace) -> CommonPlace:
        self.db.add(common_place)
        await self.db.commit()
        await self.db.refresh(common_place)
        return common_place

    async def get_all_by_user(self, user_id: UUID):
        query = select(CommonPlace).where(CommonPlace.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, user_id: UUID, id: UUID) -> CommonPlace | None:
        query = select(CommonPlace).where(CommonPlace.user_id == user_id, CommonPlace.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_and_commonplace_name(self, user_id: UUID, name: str) -> CommonPlace | None:
        query = select(CommonPlace).where(CommonPlace.user_id == user_id, CommonPlace.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, common_place: CommonPlace) -> CommonPlace:
        
        await self.db.commit()
        await self.db.refresh(common_place)
        return common_place

    async def delete(self, common_place: CommonPlace) -> None:
        await self.db.delete(common_place)
        await self.db.commit()
