from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.notifications.models import Notification, UserDeviceToken


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def get_by_id(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        result = await self.db.execute(
            select(Notification)
            .options(selectinload(Notification.trip))
            .where(Notification.id == notification_id, Notification.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_notifications(self, user_id: UUID, limit: int = 50, unread_only: bool = False) -> List[Notification]:
        query = (
            select(Notification)
            .options(selectinload(Notification.trip))
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def mark_as_read(self, notification_ids: List[UUID], user_id: UUID) -> int:
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.id.in_(notification_ids),
                Notification.user_id == user_id,
                Notification.read_at.is_(None)
            )
            .values(read_at=func.now())
        )
        await self.db.commit()
        return result.rowcount
    
    async def get_unread_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        return result.scalar() or 0
    
    async def update_push_sent_status(self, notification_id: UUID, sent: bool) -> None:
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(push_sent=sent)
        )
        await self.db.commit()


class DeviceTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register_device_token(self, user_id: UUID, device_token: str, device_type: str) -> UserDeviceToken:
        device_token_obj = UserDeviceToken(user_id=user_id, device_token=device_token, device_type=device_type)
        self.db.add(device_token_obj)
        await self.db.commit()
        await self.db.refresh(device_token_obj)
        return device_token_obj
    
    async def get_by_token(self, device_token: str) -> Optional[UserDeviceToken]:
        result = await self.db.execute(select(UserDeviceToken).where(UserDeviceToken.device_token == device_token))
        return result.scalar_one_or_none()
    
    async def update(self, device_token: UserDeviceToken) -> UserDeviceToken:
        await self.db.commit()
        await self.db.refresh(device_token)
        return device_token
    
    async def get_user_device_tokens(self, user_id: UUID, active_only: bool = True) -> List[UserDeviceToken]:
        query = select(UserDeviceToken).where(UserDeviceToken.user_id == user_id)
        
        if active_only:
            query = query.where(UserDeviceToken.is_active == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def deactivate_device_token(self, device_token: str) -> bool:
        result = await self.db.execute(
            update(UserDeviceToken)
            .where(UserDeviceToken.device_token == device_token)
            .values(is_active=False, updated_at=func.now())
        )
        await self.db.commit()
        return result.rowcount > 0
