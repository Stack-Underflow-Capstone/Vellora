import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from app.modules.rate_customizations.router import get_rate_customizations_service
from app.modules.rate_customizations.service import RateCustomizationsService
from app.modules.rate_customizations.schemas import CreateRateCustomizationDTO, EditRateCustomizationDTO
from app.modules.rate_customizations.models import RateCustomization
from app.modules.rate_customizations.exceptions import (
    RateCustomizationNotFoundError,
    InvalidRateCustomizationDataError,
    RateCustomizationPersistenceError
)
from app.modules.users.models import User, UserRole


class TestCreateRateCustomizationEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCustomizationsService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_customization(self):
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        customization.name = "Business Rates 2024"
        customization.description = "Standard business mileage rates"
        customization.year = 2024
        return customization

    @pytest.mark.asyncio
    async def test_create_customization_success(self, mock_service, mock_customization, mock_user):
        from app.modules.rate_customizations.router import create_rate_customization
        
        body = CreateRateCustomizationDTO(
            name="Business Rates 2024",
            description="Standard business mileage rates",
            year=2024
        )
        mock_service.create_rate_customization.return_value = mock_customization

        result = await create_rate_customization(body, mock_service, mock_user)

        assert result == mock_customization
        mock_service.create_rate_customization.assert_called_once_with(mock_user.id, body)

    @pytest.mark.asyncio
    async def test_create_customization_invalid_data(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import create_rate_customization
        
        body = CreateRateCustomizationDTO(name="", description="Test", year=2024)
        mock_service.create_rate_customization.side_effect = InvalidRateCustomizationDataError("Name is required")

        with pytest.raises(HTTPException) as exc_info:
            await create_rate_customization(body, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_customization_persistence_error(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import create_rate_customization
        
        body = CreateRateCustomizationDTO(name="Test", description="Test", year=2024)
        mock_service.create_rate_customization.side_effect = RateCustomizationPersistenceError("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await create_rate_customization(body, mock_service, mock_user)
        
        assert exc_info.value.status_code == 500


class TestGetCustomizationEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCustomizationsService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_customization(self):
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        customization.name = "Business Rates 2024"
        return customization

    @pytest.mark.asyncio
    async def test_get_customization_success(self, mock_service, mock_customization, mock_user):
        from app.modules.rate_customizations.router import get_customization
        
        customization_id = uuid4()
        mock_service.get_customization.return_value = mock_customization

        result = await get_customization(customization_id, mock_service, mock_user)

        assert result == mock_customization
        mock_service.get_customization.assert_called_once_with(mock_user.id, customization_id)

    @pytest.mark.asyncio
    async def test_get_customization_not_found(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import get_customization
        
        customization_id = uuid4()
        mock_service.get_customization.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_customization(customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404


class TestEditCustomizationEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCustomizationsService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_customization(self):
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        customization.name = "Updated Name"
        customization.description = "Updated Description"
        customization.year = 2025
        return customization

    @pytest.mark.asyncio
    async def test_edit_customization_success(self, mock_service, mock_customization, mock_user):
        from app.modules.rate_customizations.router import edit_customization
        
        customization_id = uuid4()
        body = EditRateCustomizationDTO(
            name="Updated Name",
            description="Updated Description",
            year=2025
        )
        mock_service.edit_customization.return_value = mock_customization

        result = await edit_customization(customization_id, body, mock_service, mock_user)

        assert result == mock_customization
        mock_service.edit_customization.assert_called_once_with(mock_user.id, customization_id, body)

    @pytest.mark.asyncio
    async def test_edit_customization_partial_update(self, mock_service, mock_customization, mock_user):
        from app.modules.rate_customizations.router import edit_customization
        
        customization_id = uuid4()
        body = EditRateCustomizationDTO(name="Updated Name")
        mock_service.edit_customization.return_value = mock_customization

        result = await edit_customization(customization_id, body, mock_service, mock_user)

        assert result == mock_customization

    @pytest.mark.asyncio
    async def test_edit_customization_not_found(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import edit_customization
        
        customization_id = uuid4()
        body = EditRateCustomizationDTO(name="Updated Name")
        mock_service.edit_customization.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await edit_customization(customization_id, body, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_edit_customization_invalid_data(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import edit_customization
        
        customization_id = uuid4()
        body = EditRateCustomizationDTO(name="")
        mock_service.edit_customization.side_effect = InvalidRateCustomizationDataError("Name cannot be empty")

        with pytest.raises(HTTPException) as exc_info:
            await edit_customization(customization_id, body, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400


class TestDeleteCustomizationEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCustomizationsService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.mark.asyncio
    async def test_delete_customization_success(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import delete_customization
        
        customization_id = uuid4()
        mock_service.delete_customization.return_value = None

        result = await delete_customization(customization_id, mock_service, mock_user)

        mock_service.delete_customization.assert_called_once_with(mock_user.id, customization_id)
        assert result.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_customization_not_found(self, mock_service, mock_user):
        from app.modules.rate_customizations.router import delete_customization
        
        customization_id = uuid4()
        mock_service.delete_customization.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_customization(customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetRateCustomizationsServiceDependency:

    def test_get_service_returns_service(self):
        from unittest.mock import MagicMock
        
        mock_db = MagicMock()
        service = get_rate_customizations_service(mock_db)
        
        assert isinstance(service, RateCustomizationsService)
