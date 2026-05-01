
import datetime
from uuid import UUID
from pydantic import BaseModel

class CreateRateCategoryDTO(BaseModel):
    name: str
    cost_per_mile: float


class EditRateCategoryDTO(BaseModel):
    name: str | None = None
    cost_per_mile: float | None = None

class RateCategoryResponseDTO(BaseModel):
    id: UUID
    name: str
    cost_per_mile: float
    created_at: datetime.datetime
    rate_customization_id: UUID

    class Config:
        from_attributes = True