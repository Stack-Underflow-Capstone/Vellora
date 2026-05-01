from uuid import UUID
from fastapi import APIRouter, Depends, Response, status
from app.infra.db import AsyncSession
from app.container import get_db
from app.core.dependencies import get_current_user
from app.core.error_handler import error_handler
from app.modules.users.models import User
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.service import VehicleService
from app.modules.vehicles.schemas import CreateVehicleDTO, EditVehicleDTO, VehicleResponse


router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def get_vehicle_service(db: AsyncSession = Depends(get_db)):
    return VehicleService(VehicleRepository(db))


@router.post("/", response_model=VehicleResponse)
@error_handler
async def create_vehicle(body: CreateVehicleDTO, svc = Depends(get_vehicle_service), current_user: User = Depends(get_current_user)):
    vehicle = await svc.create_vehicle(current_user.id, body)
    return VehicleResponse.model_validate(vehicle)


@router.get("/", response_model=list[VehicleResponse])
@error_handler
async def get_user_vehicles(include_inactive: bool = False, svc = Depends(get_vehicle_service), current_user: User = Depends(get_current_user)):
    vehicles = await svc.get_user_vehicles(current_user.id, include_inactive)
    return [VehicleResponse.model_validate(v) for v in vehicles]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
@error_handler
async def get_vehicle(vehicle_id: UUID, svc = Depends(get_vehicle_service), current_user: User = Depends(get_current_user)):
    vehicle = await svc.get_vehicle(current_user.id, vehicle_id)
    return VehicleResponse.model_validate(vehicle)


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
@error_handler
async def update_vehicle(vehicle_id: UUID, body: EditVehicleDTO, svc = Depends(get_vehicle_service), current_user: User = Depends(get_current_user)):
    vehicle = await svc.update_vehicle(current_user.id, vehicle_id, body)
    return VehicleResponse.model_validate(vehicle)


@router.delete("/{vehicle_id}")
@error_handler
async def delete_vehicle(vehicle_id: UUID, svc = Depends(get_vehicle_service), current_user: User = Depends(get_current_user)):
    await svc.delete_vehicle(current_user.id, vehicle_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)