from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from app.infra.db import AsyncSession
from app.modules.common_places.service import CommonPlaceService
from app.container import get_db
from app.modules.common_places.repository import CommonPlaceRepo
from app.modules.common_places.schemas import CommonPlaceCreate, CommonPlaceUpdate, CommonPlaceResponse
from app.core.error_handler import error_handler
from app.core.dependencies import get_current_user
from app.modules.users.models import User


router = APIRouter(prefix="/common-places", tags=["Common Places"])

def get_common_place_service(db: AsyncSession = Depends(get_db)):
    return CommonPlaceService(CommonPlaceRepo(db))

@router.post("/", response_model=CommonPlaceResponse)
@error_handler
async def create_common_place(
    body: CommonPlaceCreate, 
    svc = Depends(get_common_place_service),
    current_user: User = Depends(get_current_user)
):
    common_place = await svc.create_common_place(current_user.id, body)
    return CommonPlaceResponse.model_validate(common_place)

@router.get("/{place_id}", response_model=CommonPlaceResponse)
@error_handler
async def get_common_place(
    place_id: UUID, 
    svc = Depends(get_common_place_service),
    current_user: User = Depends(get_current_user)
):
    common_place = await svc.get_common_place(current_user.id, place_id)
    return CommonPlaceResponse.model_validate(common_place)

@router.patch("/{place_id}", response_model=CommonPlaceResponse)
@error_handler
async def update_common_place(
    place_id: UUID, 
    body: CommonPlaceUpdate, 
    svc = Depends(get_common_place_service),
    current_user: User = Depends(get_current_user)
):
    common_place = await svc.update_common_place(current_user.id, place_id, body)
    return CommonPlaceResponse.model_validate(common_place)

@router.delete("/{place_id}")
@error_handler
async def delete_common_place(
    place_id: UUID, 
    svc = Depends(get_common_place_service),
    current_user: User = Depends(get_current_user)
):
    await svc.delete_common_place(current_user.id, place_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/", response_model=list[CommonPlaceResponse])
@error_handler
async def get_user_common_places(
    svc = Depends(get_common_place_service),
    current_user: User = Depends(get_current_user)
):
    places = await svc.get_all_common_places(current_user.id)
    return [CommonPlaceResponse.model_validate(place) for place in places]
