from app.core.base import Base
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
class RateCustomization(Base):
    __tablename__ = "rate_customizations"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "name", name="uq_rate_customizations_user_name"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4) 
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    year: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)

    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="rate_customization")
    categories: Mapped[list["RateCategory"]] = relationship("RateCategory", back_populates="rate_customization", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User", back_populates="rate_customizations")