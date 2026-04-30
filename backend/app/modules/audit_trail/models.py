import enum
import uuid
import sqlalchemy as sa
from app.core.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


class AuditAction(str, enum.Enum):
    REPORT_REQUESTED = "report_requested"
    REPORT_GENERATED = "report_generated"
    REPORT_FAILED = "report_failed"
    REPORT_DOWNLOADED = "report_downloaded"
    
    TRIP_STARTED = "trip_started"
    TRIP_COMPLETED = "trip_completed"
    TRIP_CANCELLED = "trip_cancelled"
    TRIP_MANUAL_CREATED = "trip_manual_created"
    TRIP_UPDATED = "trip_updated"
    
    RATE_CUSTOMIZATION_CREATED = "rate_customization_created"
    RATE_CUSTOMIZATION_UPDATED = "rate_customization_updated"
    RATE_CUSTOMIZATION_DELETED = "rate_customization_deleted"
    
    RATE_CATEGORY_CREATED = "rate_category_created"
    RATE_CATEGORY_UPDATED = "rate_category_updated"
    RATE_CATEGORY_DELETED = "rate_category_deleted"


class AuditTrail(Base):
    __tablename__ = "audit_trails"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)    
    action: Mapped[AuditAction] = mapped_column(sa.Enum(AuditAction, name="audit_action"), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(sa.String(100), nullable=False, index=True)
    resource_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, index=True)
    timestamp: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True)
    details: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    success: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="audit_trails")






















