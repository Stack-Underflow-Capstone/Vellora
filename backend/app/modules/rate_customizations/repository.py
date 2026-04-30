from uuid import UUID
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.rate_customizations.models import RateCustomization
from app.modules.users.models import User

class RateCustomizationRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, rate_customization: RateCustomization) -> RateCustomization:
        self.db.add(rate_customization)
        await self.db.commit()
        await self.db.refresh(rate_customization)

        return rate_customization
    
    async def get(self, customization_id: UUID, user_id: UUID = None) -> RateCustomization:
        query = select(RateCustomization).where(RateCustomization.id == customization_id)
        if user_id is not None:
            query = query.where(RateCustomization.user_id == user_id)
        return await self.db.scalar(query)
    
    async def delete(self, customization : RateCustomization) -> None:
        await self.db.delete(customization)
        await self.db.commit()

    async def get_by_user_and_name(self, user_id: UUID, name: str) -> RateCustomization | None:
        query = select(RateCustomization).where(
            RateCustomization.user_id == user_id,
            RateCustomization.name == name
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_customizations(self, user_id: UUID):
        #get IRS system user id to include global IRS rates
        irs_user_result = await self.db.execute(
            select(User.id).where(User.email == 'system@irs.gov')
        )
        irs_user_id = irs_user_result.scalar_one_or_none()
        
        #include both users own customizations and the global IRS customization
        query = select(RateCustomization).where(
            or_(
                RateCustomization.user_id == user_id,
                RateCustomization.user_id == irs_user_id if irs_user_id else False
            )
        ).order_by(RateCustomization.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def is_irs_customization(self, customization_id: UUID) -> bool:
        irs_user_result = await self.db.execute(
            select(User.id).where(User.email == 'system@irs.gov')
        )
        irs_user_id = irs_user_result.scalar_one_or_none()
        
        if not irs_user_id:
            return False
            
        customization = await self.get(customization_id)
        return customization and customization.user_id == irs_user_id