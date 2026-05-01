import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "license_plate", name="uq_vehicles_user_license_plate"),
        sa.UniqueConstraint("user_id", "name", name="uq_vehicles_user_name"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    license_plate: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    year: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    color: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="vehicles")
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="vehicle")