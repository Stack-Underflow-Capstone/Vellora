from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from app.infra.db import AsyncSession
from app.modules.rate_categories.service import RateCategoriesService
from app.container import get_db
from app.modules.rate_categories.repository import RateCategoryRepo
from app.modules.rate_categories.schemas import CreateRateCategoryDTO, EditRateCategoryDTO, RateCategoryResponseDTO
from app.core.error_handler import error_handler
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.audit_trail.service import AuditTrailService



router = APIRouter(prefix="/rate-customizations/{customization_id}/categories", tags=["Rate Categories"])

def get_rate_category_service(db: AsyncSession = Depends(get_db)):
    from app.modules.audit_trail.repository import AuditTrailRepo
    audit_service = AuditTrailService(AuditTrailRepo(db))
    return RateCategoriesService(RateCategoryRepo(db), RateCustomizationRepo(db), audit_service)

@router.post("/", response_model=RateCategoryResponseDTO)
@error_handler
async def create_rate_category(
    body: CreateRateCategoryDTO, 
    customization_id: UUID, 
    svc = Depends(get_rate_category_service),
    current_user: User = Depends(get_current_user)
):
    rate_category = await svc.create_rate_category(current_user.id, customization_id, body)
    return rate_category

@router.get("/", response_model=list[RateCategoryResponseDTO])
@error_handler
async def get_categories_by_customization(
    customization_id: UUID, 
    svc = Depends(get_rate_category_service),
    current_user: User = Depends(get_current_user)
):
    categories_by_customization = await svc.get_categories_by_customization(current_user.id, customization_id)
    return categories_by_customization

@router.get("/{category_id}", response_model=RateCategoryResponseDTO)
@error_handler
async def get_category(
    category_id: UUID, 
    svc = Depends(get_rate_category_service),
    current_user: User = Depends(get_current_user)
):
    rate_category = await svc.get_category(current_user.id, category_id)
    return rate_category


@router.patch("/{category_id}", response_model=RateCategoryResponseDTO)
@error_handler
async def edit_category(
    body: EditRateCategoryDTO, 
    category_id: UUID, 
    svc = Depends(get_rate_category_service),
    current_user: User = Depends(get_current_user)
):
    rate_category = await svc.edit_category(current_user.id, category_id, body)
    return rate_category

@router.delete("/{category_id}")
@error_handler
async def delete_category(
    category_id: UUID, 
    svc = Depends(get_rate_category_service),
    current_user: User = Depends(get_current_user)
):
    await svc.delete_category(current_user.id, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)