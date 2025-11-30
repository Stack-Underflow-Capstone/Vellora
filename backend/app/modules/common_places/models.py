import uuid
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base


class CommonPlace(Base):
    __tablename__ = "common_places"
    __table_args__ = (
        sa.UniqueConstraint("user_id", "name", name="uq_common_places_customization_name"),
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    address: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="common_places")