import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException

from app.modules.trips.router import get_trips_service
from app.modules.trips.service import TripsService
from app.modules.trips.schemas import CreateTripDTO, EditTripDTO, EndTripDTO, ManualCreateTripDTO, ScheduleTripDTO
from app.modules.trips.models import Trip, TripStatus
from app.modules.trips.exceptions import (
    InvalidTripDataError,
    TripNotFoundError,
    TripPersistenceError
)
from app.modules.rate_customizations.exceptions import RateCustomizationNotFoundError
from app.modules.rate_categories.exceptions import InvalidRateCategoryDataError, RateCategoryNotFoundError
from app.modules.users.models import User, UserRole


class TestStartTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.active
        trip.start_address_encrypted = "encrypted"
        trip.purpose = "Business"
        trip.reimbursement_rate = 0.65
        trip.rate_customization_id = uuid4()
        trip.rate_category_id = uuid4()
        trip.expenses = []
        return trip

    @pytest.mark.asyncio
    async def test_start_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import start_trip
        
        body = CreateTripDTO(
            start_address="123 Main St",
            purpose="Business",
            vehicle="Honda Accord",
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.start_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await start_trip(body, mock_service, current_user=mock_user)

        mock_service.start_trip.assert_called_once_with(mock_user.id, body)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_start_trip_invalid_data(self, mock_service, mock_user):
        from app.modules.trips.router import start_trip
        
        body = CreateTripDTO(
            start_address="",
            purpose="Business",
            vehicle="Toyota Prius",
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.start_trip.side_effect = InvalidTripDataError("Start address is required")

        with pytest.raises(HTTPException) as exc_info:
            await start_trip(body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_start_trip_customization_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import start_trip
        
        body = CreateTripDTO(
            start_address="123 Main St",
            purpose="Business",
            vehicle="Ford Explorer",
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.start_trip.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await start_trip(body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_start_trip_category_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import start_trip
        
        body = CreateTripDTO(
            start_address="123 Main St",
            purpose="Business",
            vehicle="Chevy Tahoe",
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.start_trip.side_effect = RateCategoryNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await start_trip(body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestManualCreateTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.completed
        trip.start_address_encrypted = "encrypted"
        trip.end_address_encrypted = "encrypted"
        trip.purpose = "Business"
        trip.vehicle = "Honda Civic"
        trip.miles = 25.5
        trip.reimbursement_rate = 0.65
        trip.rate_customization_id = uuid4()
        trip.rate_category_id = uuid4()
        trip.expenses = []
        return trip

    @pytest.mark.asyncio
    async def test_manual_create_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import manual_create_trip
        
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=2)
        
        body = ManualCreateTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            purpose="Business meeting",
            vehicle="Honda Civic",
            miles=25.5,
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.manual_create_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await manual_create_trip(body, mock_service, current_user=mock_user)

        mock_service.manual_create_trip.assert_called_once_with(mock_user.id, body)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_manual_create_trip_invalid_data(self, mock_service, mock_user):
        from app.modules.trips.router import manual_create_trip
        
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=1)
        
        body = ManualCreateTripDTO(
            start_address="",
            end_address="456 Oak Ave",
            miles=10.0,
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.manual_create_trip.side_effect = InvalidTripDataError("Start address is required")

        with pytest.raises(HTTPException) as exc_info:
            await manual_create_trip(body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_manual_create_trip_customization_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import manual_create_trip
        
        started_time = datetime.now(timezone.utc)
        ended_time = started_time + timedelta(hours=1)
        
        body = ManualCreateTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            miles=10.0,
            started_at=started_time,
            ended_at=ended_time,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4()
        )
        mock_service.manual_create_trip.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await manual_create_trip(body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestScheduleTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.scheduled
        return trip

    @pytest.mark.asyncio
    async def test_schedule_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import schedule_trip

        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(hours=2)
        body = ScheduleTripDTO(
            start_address="123 Main St",
            end_address="456 Oak Ave",
            purpose="Business meeting",
            vehicle_id=None,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4(),
            scheduled_start_at=start_time,
            scheduled_end_at=end_time,
        )
        mock_service.schedule_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await schedule_trip(body, mock_service, current_user=mock_user)

        mock_service.schedule_trip.assert_called_once_with(mock_user.id, body)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_schedule_trip_invalid_data(self, mock_service, mock_user):
        from app.modules.trips.router import schedule_trip

        start_time = datetime.now(timezone.utc)
        end_time = start_time - timedelta(hours=2)
        body = ScheduleTripDTO(
            start_address=None,
            end_address=None,
            purpose=None,
            vehicle_id=None,
            rate_customization_id=uuid4(),
            rate_category_id=uuid4(),
            scheduled_start_at=start_time,
            scheduled_end_at=end_time,
        )
        mock_service.schedule_trip.side_effect = InvalidTripDataError("Scheduled end time must be after start time")

        with pytest.raises(HTTPException) as exc_info:
            await schedule_trip(body, mock_service, current_user=mock_user)

        assert exc_info.value.status_code == 400


class TestGetTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.active
        return trip

    @pytest.mark.asyncio
    async def test_get_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import get_trip
        
        trip_id = uuid4()
        mock_service.get_trip_by_id.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await get_trip(trip_id, mock_service, current_user=mock_user)

        mock_service.get_trip_by_id.assert_called_once_with(mock_user.id, trip_id)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_get_trip_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import get_trip
        
        trip_id = uuid4()
        mock_service.get_trip_by_id.side_effect = TripNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_trip(trip_id, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestEndTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.completed
        return trip

    @pytest.mark.asyncio
    async def test_end_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import end_trip
        
        trip_id = uuid4()
        body = EndTripDTO(end_address="456 Oak Ave", geometry={"type":"LineString","coordinates":[[-122.4194,37.7749],[-122.4094,37.7849]]}, distance_meters=81320.0)
        mock_service.end_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await end_trip(trip_id, body, mock_service, current_user=mock_user)

        mock_service.end_trip.assert_called_once_with(mock_user.id, trip_id, body)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_end_trip_invalid_data(self, mock_service, mock_user):
        from app.modules.trips.router import end_trip
        
        trip_id = uuid4()
        body = EndTripDTO(end_address="", geometry={"type":"Point","coordinates":[-122.4194,37.7749]}, distance_meters=81320.0)
        mock_service.end_trip.side_effect = InvalidTripDataError("End address is required")

        with pytest.raises(HTTPException) as exc_info:
            await end_trip(trip_id, body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_end_trip_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import end_trip
        
        trip_id = uuid4()
        body = EndTripDTO(end_address="456 Oak Ave", geometry={"type":"Polygon","coordinates":[[[-122.4,37.8],[-122.4,37.7],[-122.3,37.7],[-122.3,37.8],[-122.4,37.8]]]}, distance_meters=81320.0)
        mock_service.end_trip.side_effect = TripNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await end_trip(trip_id, body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404


class TestEditTripEndpoint:

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.active
        trip.purpose = "Updated"
        return trip

    @pytest.mark.asyncio
    async def test_edit_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import edit_trip
        
        trip_id = uuid4()
        body = EditTripDTO(purpose="Updated")
        mock_service.edit_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await edit_trip(trip_id, body, mock_service, current_user=mock_user)

        mock_service.edit_trip.assert_called_once_with(mock_user.id, trip_id, body)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_edit_trip_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import edit_trip
        
        trip_id = uuid4()
        body = EditTripDTO(purpose="Updated")
        mock_service.edit_trip.side_effect = TripNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await edit_trip(trip_id, body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_edit_trip_invalid_category(self, mock_service, mock_user):
        from app.modules.trips.router import edit_trip
        
        trip_id = uuid4()
        body = EditTripDTO(rate_category_id=uuid4())
        mock_service.edit_trip.side_effect = InvalidRateCategoryDataError("Category mismatch")

        with pytest.raises(HTTPException) as exc_info:
            await edit_trip(trip_id, body, mock_service, current_user=mock_user)
        
        assert exc_info.value.status_code == 400


class TestCancelTripEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=TripsService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_trip(self):
        trip = MagicMock(spec=Trip)
        trip.id = uuid4()
        trip.status = TripStatus.cancelled
        return trip

    @pytest.mark.asyncio
    async def test_cancel_trip_success(self, mock_service, mock_trip, mock_user):
        from app.modules.trips.router import cancel_trip
        
        trip_id = uuid4()
        mock_service.cancel_trip.return_value = mock_trip

        with patch('app.modules.trips.router.TripResponseDTO.model_validate') as mock_validate:
            mock_validate.return_value = MagicMock()
            result = await cancel_trip(trip_id, mock_service, mock_user)

        mock_service.cancel_trip.assert_called_once_with(mock_user.id, trip_id)
        mock_validate.assert_called_once_with(mock_trip)

    @pytest.mark.asyncio
    async def test_cancel_trip_not_found(self, mock_service, mock_user):
        from app.modules.trips.router import cancel_trip
        
        trip_id = uuid4()
        mock_service.cancel_trip.side_effect = TripNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await cancel_trip(trip_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_trip_invalid_status(self, mock_service, mock_user):
        from app.modules.trips.router import cancel_trip
        
        trip_id = uuid4()
        mock_service.cancel_trip.side_effect = InvalidTripDataError("Only active or scheduled trips can be cancelled")

        with pytest.raises(HTTPException) as exc_info:
            await cancel_trip(trip_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400
        
        assert exc_info.value.status_code == 400


class TestGetTripsServiceDependency:

    def test_get_service_returns_service(self):
        from unittest.mock import MagicMock
        
        mock_db = MagicMock()
        
        service = get_trips_service(mock_db)
        
        assert isinstance(service, TripsService)
