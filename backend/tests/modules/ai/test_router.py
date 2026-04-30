import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.ai.exceptions import AiRateLimitError
from app.modules.ai.router import get_ai_service, route_weather, trip_assistant
from app.modules.ai.schemas import (
    RoutePointDTO,
    RouteWeatherRequestDTO,
    TripAssistantRequestDTO,
    TripAssistantResponseDTO,
)
from app.modules.ai.service import AiAssistantService
from app.modules.users.models import User


class TestAiRouter:
    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=AiAssistantService)

    @pytest.mark.asyncio
    async def test_trip_assistant_success(self, mock_user, mock_service):
        body = TripAssistantRequestDTO(message="Help categorize this trip")
        expected = TripAssistantResponseDTO(
            assistant_message="Looks like business travel.",
            suggested_category="Business",
            missing_details=[],
            weather_summary=None,
            ai_enabled=False,
        )
        mock_service.ask_trip_assistant.return_value = expected

        result = await trip_assistant(body=body, svc=mock_service, current_user=mock_user)

        assert result == expected
        mock_service.ask_trip_assistant.assert_called_once_with(mock_user.id, body)

    @pytest.mark.asyncio
    async def test_route_weather_success(self, mock_user, mock_service):
        body = RouteWeatherRequestDTO(
            current_location=RoutePointDTO(lat=32.77, lon=-96.79),
            destination_location=RoutePointDTO(lat=33.21, lon=-97.13),
        )
        mock_service.get_route_weather_for_user.return_value = "Current location: clear, 25C"

        result = await route_weather(body=body, svc=mock_service, current_user=mock_user)

        assert result.weather_summary == "Current location: clear, 25C"
        mock_service.get_route_weather_for_user.assert_called_once_with(
            mock_user.id,
            body.current_location,
            body.destination_location,
        )

    @pytest.mark.asyncio
    async def test_route_weather_rate_limited(self, mock_user, mock_service):
        body = RouteWeatherRequestDTO(
            current_location=RoutePointDTO(lat=32.77, lon=-96.79),
            destination_location=None,
        )
        mock_service.get_route_weather_for_user.side_effect = AiRateLimitError("Too many AI requests")

        with pytest.raises(HTTPException) as exc_info:
            await route_weather(body=body, svc=mock_service, current_user=mock_user)

        assert exc_info.value.status_code == 429

    def test_get_ai_service_returns_service(self):
        mock_db = MagicMock()
        service = get_ai_service(mock_db)
        assert isinstance(service, AiAssistantService)
