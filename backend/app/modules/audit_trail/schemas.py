import datetime
from uuid import UUID
from pydantic import BaseModel
from .models import AuditAction


class CreateAuditTrailDTO(BaseModel):
    user_id: UUID | None = None
    action: AuditAction
    resource: str
    resource_id: str | None = None
    details: str | None = None
    success: bool = True
    error_message: str | None = None


class EditAuditTrailDTO(BaseModel):
    details: str | None = None
    success: bool | None = None
    error_message: str | None = None


class AuditTrailResponseDTO(BaseModel):
    id: UUID
    user_id: UUID | None
    action: AuditAction
    resource: str
    resource_id: str | None
    timestamp: datetime.datetime
    details: str | None
    success: bool
    error_message: str | None

    class Config:
        from_attributes = True