from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import get_db
from app.core.dependencies import get_current_user
from app.core.error_handler import error_handler
from app.infra.adapters.expo_notification_adapter import ExpoNotificationAdapter
from app.modules.notifications.repository import DeviceTokenRepository, NotificationRepository
from app.modules.notifications.schemas import MarkNotificationReadDTO, NotificationListResponseDTO, RegisterDeviceTokenDTO,UserStoppedMovingEventDTO

from app.modules.notifications.service import NotificationService
from app.modules.trips.repository import TripRepo
from app.modules.users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])
def get_notification_service(db: AsyncSession = Depends(get_db)):
    notification_repo = NotificationRepository(db)
    device_token_repo = DeviceTokenRepository(db)
    trip_repo = TripRepo(db)
    expo_adapter = ExpoNotificationAdapter(device_token_storage=device_token_repo)
    return NotificationService(notification_repo, device_token_repo, expo_adapter, trip_repo)

@router.post("/device-token")
@error_handler
async def register_device_token(device_data: RegisterDeviceTokenDTO, svc: NotificationService = Depends(get_notification_service), current_user: User = Depends(get_current_user)):
    device_token = await svc.register_device_token(current_user.id, device_data)
    return {"message": "Device token registered successfully", "device_token_id": str(device_token.id)}

@router.get("/", response_model=NotificationListResponseDTO)
@error_handler
async def get_notifications(limit: int = 50, unread_only: bool = False, svc: NotificationService = Depends(get_notification_service), current_user: User = Depends(get_current_user)):
    return await svc.get_user_notifications(user_id=current_user.id, limit=limit, unread_only=unread_only)

@router.patch("/mark-read")
@error_handler
async def mark_notifications_read(data: MarkNotificationReadDTO, svc: NotificationService = Depends(get_notification_service), current_user: User = Depends(get_current_user)):
    count = await svc.mark_notifications_as_read(user_id=current_user.id, notification_ids=data.notification_ids)
    return {"message": f"Marked {count} notifications as read", "updated_count": count}

@router.post("/events/user-stopped-moving")
@error_handler
async def handle_user_stopped_moving(event_data: UserStoppedMovingEventDTO, svc: NotificationService = Depends(get_notification_service), current_user: User = Depends(get_current_user)):
    await svc.handle_user_stopped_moving_event(user_id=current_user.id, trip_id=event_data.trip_id)
    return {"message": "User stopped moving event processed successfully"}

@router.post("/events/user-started-moving")
@error_handler
async def handle_user_started_moving(svc: NotificationService = Depends(get_notification_service), current_user: User = Depends(get_current_user)):
    await svc.handle_user_started_moving_event(user_id=current_user.id)
    return {"message": "User started moving event processed successfully"}