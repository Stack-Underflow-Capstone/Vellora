from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from app.infra.db import AsyncSession
from app.modules.rate_customizations.service import RateCustomizationsService
from app.container import get_db
from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.rate_customizations.schemas import CreateRateCustomizationDTO, EditRateCustomizationDTO, RateCustomizationResponseDTO
from app.core.error_handler import error_handler
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.audit_trail.service import AuditTrailService



router = APIRouter(prefix="/rate-customizations", tags=["Rate Customizations"])

def get_rate_customizations_service(db: AsyncSession = Depends(get_db)):
    from app.modules.audit_trail.repository import AuditTrailRepo
    audit_service = AuditTrailService(AuditTrailRepo(db))
    return RateCustomizationsService(RateCustomizationRepo(db), audit_service)

@router.post("/", response_model=RateCustomizationResponseDTO)
@error_handler
async def create_rate_customization(
    body: CreateRateCustomizationDTO, 
    svc = Depends(get_rate_customizations_service),
    current_user: User = Depends(get_current_user)
):
    rate_customization = await svc.create_rate_customization(current_user.id, body)
    return rate_customization

@router.get("/{customization_id}", response_model=RateCustomizationResponseDTO)
@error_handler
async def get_customization(
    customization_id: UUID, 
    svc = Depends(get_rate_customizations_service),
    current_user: User = Depends(get_current_user)
):
    rate_customization = await svc.get_customization(current_user.id, customization_id)
    return rate_customization

@router.patch("/{customization_id}", response_model=RateCustomizationResponseDTO)
@error_handler
async def edit_customization(
    customization_id: UUID, 
    body: EditRateCustomizationDTO, 
    svc = Depends(get_rate_customizations_service),
    current_user: User = Depends(get_current_user)
):
    rate_customization = await svc.edit_customization(current_user.id, customization_id, body)
    return rate_customization

@router.delete("/{customization_id}")
@error_handler
async def delete_customization(
    customization_id: UUID, 
    svc = Depends(get_rate_customizations_service),
    current_user: User = Depends(get_current_user)
):
    await svc.delete_customization(current_user.id, customization_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/", response_model=list[RateCustomizationResponseDTO])
@error_handler
async def get_user_customizations(
    svc = Depends(get_rate_customizations_service),
    current_user: User = Depends(get_current_user)
):
    customizations = await svc.get_user_customizations(current_user.id)
    return customizations