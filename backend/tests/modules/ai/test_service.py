import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from app.config import settings
from app.modules.ai.exceptions import AiConfigError, AiRateLimitError, AiValidationError
from app.modules.ai.schemas import TripAssistantRequestDTO
from app.modules.ai.service import AiAssistantService
from app.modules.trips.repository import TripRepo


class TestAiAssistantService:
    @pytest.fixture
    def service(self):
        repo = AsyncMock(spec=TripRepo)
        svc = AiAssistantService(repo)
        AiAssistantService._user_request_times.clear()
        yield svc
        AiAssistantService._user_request_times.clear()

    @pytest.mark.asyncio
    async def test_ask_trip_assistant_fallback_when_ai_disabled(self, service):
        user_id = uuid4()
        payload = TripAssistantRequestDTO(message="Client meeting in Denton", metadata={})

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "AI_AGENT_ENABLED", False)
            mp.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 10)
            result = await service.ask_trip_assistant(user_id, payload)

        assert result.ai_enabled is False
        assert result.suggested_category == "Business"
        assert "AI assistant is disabled" in result.assistant_message

    @pytest.mark.asyncio
    async def test_ask_trip_assistant_requires_api_key_when_enabled(self, service):
        user_id = uuid4()
        payload = TripAssistantRequestDTO(message="Plan this trip")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "AI_AGENT_ENABLED", True)
            mp.setattr(settings, "OPENAI_API_KEY", None)
            mp.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 10)
            with pytest.raises(AiConfigError):
                await service.ask_trip_assistant(user_id, payload)

    @pytest.mark.asyncio
    async def test_ask_trip_assistant_enforces_metadata_limits(self, service):
        user_id = uuid4()
        payload = TripAssistantRequestDTO(
            message="Plan this trip",
            metadata={"a": "1", "b": "2"},
        )

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "AI_AGENT_ENABLED", False)
            mp.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 10)
            mp.setattr(settings, "AI_MAX_METADATA_KEYS", 1)
            with pytest.raises(AiValidationError):
                await service.ask_trip_assistant(user_id, payload)

    @pytest.mark.asyncio
    async def test_ask_trip_assistant_rate_limit(self, service):
        user_id = uuid4()
        payload = TripAssistantRequestDTO(message="Business trip")

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "AI_AGENT_ENABLED", False)
            mp.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 1)
            await service.ask_trip_assistant(user_id, payload)
            with pytest.raises(AiRateLimitError):
                await service.ask_trip_assistant(user_id, payload)

    def test_parse_json_content_with_markdown_fence(self, service):
        content = """```json
{"assistant_message":"ok","suggested_category":null,"missing_details":[]}
```"""

        parsed = service._parse_json_content(content)

        assert parsed["assistant_message"] == "ok"
        assert parsed["missing_details"] == []

    @pytest.mark.asyncio
    async def test_ai_response_is_normalized(self, service):
        user_id = uuid4()
        payload = TripAssistantRequestDTO(message="Need help")
        service._call_openai = AsyncMock(
            return_value={
                "assistant_message": "   ",
                "suggested_category": "X" * 120,
                "missing_details": [" purpose ", "purpose", 123],
            }
        )

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "AI_AGENT_ENABLED", True)
            mp.setattr(settings, "OPENAI_API_KEY", "test")
            mp.setattr(settings, "AI_RATE_LIMIT_PER_MINUTE", 10)
            mp.setattr(settings, "AI_MAX_MISSING_DETAILS", 8)
            result = await service.ask_trip_assistant(user_id, payload)

        assert result.ai_enabled is True
        assert result.assistant_message == "I could not generate a response."
        assert result.suggested_category is not None
        assert len(result.suggested_category) == 80
        assert result.missing_details == ["purpose"]

    @pytest.mark.asyncio
    async def test_get_route_weather_returns_none_with_no_points(self, service):
        summary = await service.get_route_weather(None, None)
        assert summary is None
