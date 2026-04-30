# AI Trip Assistant

This file documents the AI endpoints that live in the backend.

## Endpoints

- `POST /api/v1/ai/trip-assistant`
- `POST /api/v1/ai/route-weather`

## `POST /api/v1/ai/trip-assistant`

Request body:

```json
{
  "message": "I have a client meeting tomorrow, what category should this be?",
  "trip_id": "optional-trip-uuid",
  "current_location": { "lat": 32.7767, "lon": -96.7970 },
  "destination_location": { "lat": 33.2148, "lon": -97.1331 },
  "metadata": { "source": "mobile" }
}
```

Response includes:

- `assistant_message`
- `suggested_category`
- `missing_details`
- `weather_summary`
- `ai_enabled`

## `POST /api/v1/ai/route-weather`

Request body:

```json
{
  "current_location": { "lat": 32.7767, "lon": -96.7970 },
  "destination_location": { "lat": 33.2148, "lon": -97.1331 }
}
```

Response:

```json
{
  "weather_summary": "Current location: clear, 26C, wind 8 km/h, precip 0 mm | Destination: partly cloudy, 24C, wind 10 km/h, precip 0 mm"
}
```

## Required Environment Variables

- `AI_AGENT_ENABLED`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_BASE_URL`
- `AI_TIMEOUT_SECONDS`
- `AI_RATE_LIMIT_PER_MINUTE`
- `AI_MAX_METADATA_KEYS`
- `AI_MAX_METADATA_VALUE_LENGTH`
- `AI_MAX_MISSING_DETAILS`
- `WEATHER_BASE_URL`
- `WEATHER_TIMEOUT_SECONDS`

## Notes

- If `AI_AGENT_ENABLED=false`, the backend returns a deterministic fallback response and does not call the AI provider.
- AI endpoints are rate limited per user.
- Metadata payloads have guardrails on key count and value size.
- If you want a real API key, get it from the [OpenAI platform](https://platform.openai.com/).
