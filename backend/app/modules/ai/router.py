from fastapi import APIRouter, Depends

from app.container import get_db
from app.core.dependencies import get_current_user
from app.core.error_handler import error_handler
from app.infra.db import AsyncSession
from app.modules.ai.schemas import (
    RouteWeatherRequestDTO,
    RouteWeatherResponseDTO,
    TripAssistantRequestDTO,
    TripAssistantResponseDTO,
)
from app.modules.ai.service import AiAssistantService
from app.modules.trips.repository import TripRepo
from app.modules.users.models import User


router = APIRouter(prefix="/ai", tags=["AI"])


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AiAssistantService:
    return AiAssistantService(TripRepo(db))


@router.post("/trip-assistant", response_model=TripAssistantResponseDTO)
@error_handler
async def trip_assistant(
    body: TripAssistantRequestDTO,
    svc: AiAssistantService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
):
    return await svc.ask_trip_assistant(current_user.id, body)


@router.post("/route-weather", response_model=RouteWeatherResponseDTO)
@error_handler
async def route_weather(
    body: RouteWeatherRequestDTO,
    svc: AiAssistantService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
):
    summary = await svc.get_route_weather_for_user(
        current_user.id,
        body.current_location,
        body.destination_location,
    )
    return RouteWeatherResponseDTO(weather_summary=summary)
