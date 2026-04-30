import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException

from app.modules.rate_categories.router import get_rate_category_service
from app.modules.rate_categories.service import RateCategoriesService
from app.modules.rate_categories.schemas import CreateRateCategoryDTO, EditRateCategoryDTO
from app.modules.rate_categories.models import RateCategory
from app.modules.rate_categories.exceptions import (
    RateCategoryNotFoundError,
    InvalidRateCategoryDataError,
    DuplicateRateCategoryError
)
from app.modules.rate_customizations.exceptions import RateCustomizationNotFoundError
from app.modules.users.models import User, UserRole


class TestCreateRateCategoryEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCategoriesService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        category.cost_per_mile = 0.65
        category.rate_customization_id = uuid4()
        return category

    @pytest.mark.asyncio
    async def test_create_category_success(self, mock_service, mock_category, mock_user):
        from app.modules.rate_categories.router import create_rate_category
        
        customization_id = uuid4()
        body = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        mock_service.create_rate_category.return_value = mock_category

        result = await create_rate_category(body, customization_id, mock_service, mock_user)

        assert result == mock_category
        mock_service.create_rate_category.assert_called_once_with(mock_user.id, customization_id, body)

    @pytest.mark.asyncio
    async def test_create_category_customization_not_found(self, mock_service, mock_user):
        from app.modules.rate_categories.router import create_rate_category
        
        customization_id = uuid4()
        body = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        mock_service.create_rate_category.side_effect = RateCustomizationNotFoundError("Customization not found")

        with pytest.raises(HTTPException) as exc_info:
            await create_rate_category(body, customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_category_invalid_data(self, mock_service, mock_user):
        from app.modules.rate_categories.router import create_rate_category
        
        customization_id = uuid4()
        body = CreateRateCategoryDTO(name="", cost_per_mile=0.65)
        mock_service.create_rate_category.side_effect = InvalidRateCategoryDataError("Name is required")

        with pytest.raises(HTTPException) as exc_info:
            await create_rate_category(body, customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_category_duplicate(self, mock_service, mock_user):
        from app.modules.rate_categories.router import create_rate_category
        
        customization_id = uuid4()
        body = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        mock_service.create_rate_category.side_effect = DuplicateRateCategoryError("Already exists")

        with pytest.raises(HTTPException) as exc_info:
            await create_rate_category(body, customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 409


class TestGetCategoriesEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCategoriesService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.mark.asyncio
    async def test_get_categories_success(self, mock_service, mock_user):
        from app.modules.rate_categories.router import get_categories_by_customization
        
        customization_id = uuid4()
        mock_categories = [MagicMock(spec=RateCategory), MagicMock(spec=RateCategory)]
        mock_service.get_categories_by_customization.return_value = mock_categories

        result = await get_categories_by_customization(customization_id, mock_service, mock_user)

        assert result == mock_categories
        mock_service.get_categories_by_customization.assert_called_once_with(mock_user.id, customization_id)

    @pytest.mark.asyncio
    async def test_get_categories_empty_list(self, mock_service, mock_user):
        from app.modules.rate_categories.router import get_categories_by_customization
        
        customization_id = uuid4()
        mock_service.get_categories_by_customization.return_value = []

        result = await get_categories_by_customization(customization_id, mock_service, mock_user)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_categories_customization_not_found(self, mock_service, mock_user):
        from app.modules.rate_categories.router import get_categories_by_customization
        
        customization_id = uuid4()
        mock_service.get_categories_by_customization.side_effect = RateCustomizationNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_categories_by_customization(customization_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetCategoryEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCategoriesService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        return category

    @pytest.mark.asyncio
    async def test_get_category_success(self, mock_service, mock_category, mock_user):
        from app.modules.rate_categories.router import get_category
        
        category_id = uuid4()
        mock_service.get_category.return_value = mock_category

        result = await get_category(category_id, mock_service, mock_user)

        assert result == mock_category
        mock_service.get_category.assert_called_once_with(mock_user.id, category_id)

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, mock_service, mock_user):
        from app.modules.rate_categories.router import get_category
        
        category_id = uuid4()
        mock_service.get_category.side_effect = RateCategoryNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await get_category(category_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404


class TestEditCategoryEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCategoriesService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Premium"
        category.cost_per_mile = 0.85
        return category

    @pytest.mark.asyncio
    async def test_edit_category_success(self, mock_service, mock_category, mock_user):
        from app.modules.rate_categories.router import edit_category
        
        category_id = uuid4()
        body = EditRateCategoryDTO(name="Premium", cost_per_mile=0.85)
        mock_service.edit_category.return_value = mock_category

        result = await edit_category(body, category_id, mock_service, mock_user)

        assert result == mock_category
        mock_service.edit_category.assert_called_once_with(mock_user.id, category_id, body)

    @pytest.mark.asyncio
    async def test_edit_category_partial_update(self, mock_service, mock_category, mock_user):
        from app.modules.rate_categories.router import edit_category
        
        category_id = uuid4()
        body = EditRateCategoryDTO(name="Premium")
        mock_service.edit_category.return_value = mock_category

        result = await edit_category(body, category_id, mock_service, mock_user)

        assert result == mock_category

    @pytest.mark.asyncio
    async def test_edit_category_not_found(self, mock_service, mock_user):
        from app.modules.rate_categories.router import edit_category
        
        category_id = uuid4()
        body = EditRateCategoryDTO(name="Premium")
        mock_service.edit_category.side_effect = RateCategoryNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await edit_category(body, category_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_edit_category_invalid_data(self, mock_service, mock_user):
        from app.modules.rate_categories.router import edit_category
        
        category_id = uuid4()
        body = EditRateCategoryDTO(name="")
        mock_service.edit_category.side_effect = InvalidRateCategoryDataError("Name cannot be empty")

        with pytest.raises(HTTPException) as exc_info:
            await edit_category(body, category_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_edit_category_duplicate(self, mock_service, mock_user):
        from app.modules.rate_categories.router import edit_category
        
        category_id = uuid4()
        body = EditRateCategoryDTO(name="Premium")
        mock_service.edit_category.side_effect = DuplicateRateCategoryError("Already exists")

        with pytest.raises(HTTPException) as exc_info:
            await edit_category(body, category_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 409


class TestDeleteCategoryEndpoint:

    @pytest.fixture
    def mock_service(self):
        return AsyncMock(spec=RateCategoriesService)

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.role = UserRole.EMPLOYEE
        return user

    @pytest.mark.asyncio
    async def test_delete_category_success(self, mock_service, mock_user):
        from app.modules.rate_categories.router import delete_category
        
        category_id = uuid4()
        mock_service.delete_category.return_value = None

        result = await delete_category(category_id, mock_service, mock_user)

        mock_service.delete_category.assert_called_once_with(mock_user.id, category_id)
        assert result.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, mock_service, mock_user):
        from app.modules.rate_categories.router import delete_category
        
        category_id = uuid4()
        mock_service.delete_category.side_effect = RateCategoryNotFoundError("Not found")

        with pytest.raises(HTTPException) as exc_info:
            await delete_category(category_id, mock_service, mock_user)
        
        assert exc_info.value.status_code == 404


class TestGetRateCategoryServiceDependency:

    def test_get_service_returns_service(self):
        from unittest.mock import MagicMock
        
        mock_db = MagicMock()
        service = get_rate_category_service(mock_db)
        
        assert isinstance(service, RateCategoriesService)
