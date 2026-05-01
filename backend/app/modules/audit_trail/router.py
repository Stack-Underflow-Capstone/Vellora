from uuid import UUID
from fastapi import APIRouter, Depends
from app.infra.db import AsyncSession
from app.modules.audit_trail.repository import AuditTrailRepo
from app.modules.audit_trail.service import AuditTrailService
from app.container import get_db
from app.modules.audit_trail.schemas import CreateAuditTrailDTO, AuditTrailResponseDTO
from app.core.error_handler import error_handler
from app.core.dependencies import get_current_user
from app.modules.users.models import User


router = APIRouter(prefix="/audit-trails", tags=["Audit Trails"])

def get_audit_trail_service(db: AsyncSession = Depends(get_db)):
    return AuditTrailService(AuditTrailRepo(db))

@router.get("/me", response_model=list[AuditTrailResponseDTO])
@error_handler
async def get_my_audit_history(svc: AuditTrailService = Depends(get_audit_trail_service), current_user: User = Depends(get_current_user)):
    audit_trails = await svc.get_user_audit_history(current_user.id)
    return audit_trails

@router.get("/resource/{resource}/{resource_id}", response_model=list[AuditTrailResponseDTO])
@error_handler
async def get_resource_audit_history(resource: str, resource_id: str, svc: AuditTrailService = Depends(get_audit_trail_service),):
    audit_trails = await svc.get_resource_audit_history(resource, resource_id)
    return audit_trails

@router.get("/{audit_id}", response_model=AuditTrailResponseDTO)
@error_handler
async def get_audit_trail(audit_id: UUID, svc: AuditTrailService = Depends(get_audit_trail_service), current_user: User = Depends(get_current_user)):
    audit_trail = await svc.get_audit_trail(audit_id, current_user.id)
    return audit_trail