import enum
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, DOUBLE_PRECISION
from app.core.base import Base


class TripStatus(str, enum.Enum):
    active = "active"
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[TripStatus] = mapped_column(sa.Enum(TripStatus, name="trip_status"), default=TripStatus.active, nullable=False)
    start_address_encrypted: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    end_address_encrypted: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    purpose: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True, index=True)
    reimbursement_rate: Mapped[float | None] = mapped_column(DOUBLE_PRECISION, nullable=True)
    miles: Mapped[float | None] = mapped_column(DOUBLE_PRECISION, nullable=True)
    geometry_encrypted: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    mileage_reimbursement_total: Mapped[float | None] = mapped_column(DOUBLE_PRECISION, nullable=True)
    expense_reimbursement_total: Mapped[float | None] = mapped_column(DOUBLE_PRECISION, nullable=True)
    started_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    scheduled_start_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    scheduled_end_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    ended_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    calendar_provider: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    calendar_event_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    calendar_event_url: Mapped[str | None] = mapped_column(sa.String(1024), nullable=True)
    expenses: Mapped[list["Expense"]] = relationship("Expense", back_populates="trip", cascade="all, delete-orphan")
    receipts: Mapped[list["ExpenseReceipt"]] = relationship(
        "ExpenseReceipt",
        back_populates="trip",
        cascade="all, delete-orphan",
    )
    rate_customization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("rate_customizations.id", ondelete="RESTRICT"), nullable=False)
    rate_customization: Mapped["RateCustomization"] = relationship("RateCustomization", back_populates="trips")
    rate_category_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("rate_categories.id", ondelete="RESTRICT"), nullable=False)
    rate_category: Mapped["RateCategory"] = relationship("RateCategory", back_populates="trips")
    updated_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="trips")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="trips")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="trip", cascade="all, delete-orphan", lazy="select")


    

     
