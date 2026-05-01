from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from dataclasses import dataclass
from app.modules.notifications.models import NotificationType, NotificationStatus


class RegisterDeviceTokenDTO(BaseModel):
    device_token: str
    device_type: str

class UserStoppedMovingEventDTO(BaseModel):
    trip_id: UUID | None = None

class NotificationResponseDTO(BaseModel):
    id: UUID
    type: NotificationType
    title: str
    message: str
    status: NotificationStatus
    push_sent: bool
    read_at: datetime | None = None
    trip_id: UUID | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationListResponseDTO(BaseModel):
    notifications: list[NotificationResponseDTO]
    unread_count: int

class MarkNotificationReadDTO(BaseModel):
    notification_ids: list[UUID]

@dataclass
class NotificationEventDTO:
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    trip_id: UUID | None = None
