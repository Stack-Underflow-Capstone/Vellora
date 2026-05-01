import enum
import uuid
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base


class NotificationType(str, enum.Enum):
    TRIP_STARTED = "trip_started"
    TRIP_ENDED = "trip_ended"
    TRIP_STOP_REMINDER = "trip_stop_reminder"
    TRIP_START_REMINDER = "trip_start_reminder"
    #for when scheduled trips are implemented
    SCHEDULED_TRIP_STARTED = "scheduled_trip_started"
    SCHEDULED_TRIP_ENDED = "scheduled_trip_ended"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[NotificationType] = mapped_column(sa.Enum(NotificationType, name="notification_type"), nullable=False)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    message: Mapped[str] = mapped_column(sa.Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(sa.Enum(NotificationStatus, name="notification_status"), default=NotificationStatus.PENDING, nullable=False)
    push_sent: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    trip_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="notifications")
    trip: Mapped["Trip"] = relationship("Trip", back_populates="notifications")


class UserDeviceToken(Base):
    __tablename__ = "user_device_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_token: Mapped[str] = mapped_column(sa.String(500), nullable=False, unique=True)
    device_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    
    user: Mapped["User"] = relationship("User", back_populates="device_tokens")
