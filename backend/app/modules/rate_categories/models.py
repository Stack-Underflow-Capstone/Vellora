from app.core.base import Base
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

class RateCategory(Base):
    __tablename__ = "rate_categories"
    __table_args__ = (
        sa.UniqueConstraint("rate_customization_id", "name", name="uq_rate_categories_customization_name"),
    )
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4) 
    name: Mapped[str] = mapped_column(sa.String(60), nullable=False)
    cost_per_mile: Mapped[float] = mapped_column(sa.DOUBLE_PRECISION, nullable=False)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="rate_category")
    rate_customization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("rate_customizations.id", ondelete="RESTRICT"), nullable=False)
    rate_customization: Mapped["RateCustomization"] = relationship("RateCustomization", back_populates="categories")