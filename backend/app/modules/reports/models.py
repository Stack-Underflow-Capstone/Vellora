from datetime import date, datetime
import enum
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base


class ReportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    expired = "expired"

class Report(Base):
    __tablename__="reports"
    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    end_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(sa.Enum(ReportStatus, name="report_status"), default=ReportStatus.pending, nullable=False)
    file_url: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    file_name: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    requested_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    completed_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    processing_started_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    retry_attempts: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0")


    user: Mapped["User"] = relationship("User", back_populates="reports")

