from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RoutePointDTO(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class TripAssistantRequestDTO(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    trip_id: UUID | None = None
    current_location: RoutePointDTO | None = None
    destination_location: RoutePointDTO | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RouteWeatherRequestDTO(BaseModel):
    current_location: RoutePointDTO | None = None
    destination_location: RoutePointDTO | None = None


class RouteWeatherResponseDTO(BaseModel):
    weather_summary: str | None = None


class TripAssistantResponseDTO(BaseModel):
    assistant_message: str
    suggested_category: str | None = None
    missing_details: list[str] = Field(default_factory=list)
    weather_summary: str | None = None
    ai_enabled: bool

