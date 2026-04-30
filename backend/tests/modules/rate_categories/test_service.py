import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.rate_categories.service import RateCategoriesService
from app.modules.rate_categories.repository import RateCategoryRepo
from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.rate_categories.schemas import CreateRateCategoryDTO, EditRateCategoryDTO
from app.modules.rate_categories.models import RateCategory
from app.modules.rate_customizations.models import RateCustomization
from app.modules.rate_categories.exceptions import (
    RateCategoryNotFoundError,
    InvalidRateCategoryDataError,
    DuplicateRateCategoryError
)
from app.modules.rate_customizations.exceptions import RateCustomizationNotFoundError


class TestRateCategoriesServiceCreate:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def category_repo(self):
        return AsyncMock(spec=RateCategoryRepo)

    @pytest.fixture
    def customization_repo(self):
        return AsyncMock(spec=RateCustomizationRepo)

    @pytest.fixture
    def service(self, category_repo, customization_repo):
        return RateCategoriesService(category_repo, customization_repo)

    @pytest.fixture
    def mock_customization(self):
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        return customization

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        category.cost_per_mile = 0.65
        category.rate_customization_id = uuid4()
        return category

    @pytest.mark.asyncio
    async def test_create_category_success(
        self, service, category_repo, customization_repo, mock_customization, mock_category, user_id
    ):
        customization_id = uuid4()
        dto = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        customization_repo.is_irs_customization.return_value = False 
        customization_repo.get.return_value = mock_customization
        category_repo.get_by_customization_and_name.return_value = None
        category_repo.save.return_value = mock_category

        with patch('app.modules.rate_categories.service.RateCategory') as MockCategory:
            MockCategory.return_value = mock_category
            result = await service.create_rate_category(user_id, customization_id, dto)

        assert result == mock_category
        category_repo.save.assert_called()

    @pytest.mark.asyncio
    async def test_create_category_customization_not_found(
        self, service, customization_repo, user_id
    ):
        customization_id = uuid4()
        dto = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        customization_repo.is_irs_customization.return_value = False 
        customization_repo.get.return_value = None

        with pytest.raises(RateCustomizationNotFoundError):
            await service.create_rate_category(user_id, customization_id, dto)

    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(
        self, service, category_repo, customization_repo, mock_customization, mock_category, user_id
    ):
        customization_id = uuid4()
        dto = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        customization_repo.is_irs_customization.return_value = False 
        customization_repo.get.return_value = mock_customization
        category_repo.get_by_customization_and_name.return_value = mock_category

        with pytest.raises(DuplicateRateCategoryError):
            await service.create_rate_category(user_id, customization_id, dto)

    @pytest.mark.asyncio
    async def test_create_category_irs_blocked(
        self, service, customization_repo, user_id
    ):
        customization_id = uuid4()
        dto = CreateRateCategoryDTO(name="Standard", cost_per_mile=0.65)
        customization_repo.is_irs_customization.return_value = True  

        with pytest.raises(InvalidRateCategoryDataError) as exc_info:
            await service.create_rate_category(user_id, customization_id, dto)
        
        assert "Cannot add categories to IRS standard rates" in str(exc_info.value)


class TestRateCategoriesServiceGet:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def category_repo(self):
        return AsyncMock(spec=RateCategoryRepo)

    @pytest.fixture
    def customization_repo(self):
        return AsyncMock(spec=RateCustomizationRepo)

    @pytest.fixture
    def service(self, category_repo, customization_repo):
        return RateCategoriesService(category_repo, customization_repo)

    @pytest.mark.asyncio
    async def test_get_category_success(self, service, category_repo, customization_repo, user_id):
        category_id = uuid4()
        mock_category = MagicMock(spec=RateCategory)
        mock_category.rate_customization_id = uuid4()
        mock_customization = MagicMock(spec=RateCustomization)
        category_repo.get.return_value = mock_category
        customization_repo.get.return_value = mock_customization

        result = await service.get_category(user_id, category_id)

        assert result == mock_category
        category_repo.get.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, service, category_repo, user_id):
        category_id = uuid4()
        category_repo.get.return_value = None

        with pytest.raises(RateCategoryNotFoundError):
            await service.get_category(user_id, category_id)


class TestRateCategoriesServiceGetByCustomization:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def category_repo(self):
        return AsyncMock(spec=RateCategoryRepo)

    @pytest.fixture
    def customization_repo(self):
        return AsyncMock(spec=RateCustomizationRepo)

    @pytest.fixture
    def service(self, category_repo, customization_repo):
        return RateCategoriesService(category_repo, customization_repo)

    @pytest.fixture
    def mock_customization(self):
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        return customization

    @pytest.mark.asyncio
    async def test_get_categories_by_customization_success(
        self, service, category_repo, customization_repo, mock_customization, user_id
    ):
        customization_id = uuid4()
        mock_categories = [MagicMock(spec=RateCategory), MagicMock(spec=RateCategory)]
        customization_repo.get.return_value = mock_customization
        category_repo.get_by_customization_id.return_value = mock_categories

        result = await service.get_categories_by_customization(user_id, customization_id)

        assert result == mock_categories
        category_repo.get_by_customization_id.assert_called_once_with(customization_id)

    @pytest.mark.asyncio
    async def test_get_categories_customization_not_found(
        self, service, customization_repo, user_id
    ):
        customization_id = uuid4()
        customization_repo.get.return_value = None

        with pytest.raises(RateCustomizationNotFoundError):
            await service.get_categories_by_customization(user_id, customization_id)


class TestRateCategoriesServiceEdit:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def category_repo(self):
        return AsyncMock(spec=RateCategoryRepo)

    @pytest.fixture
    def customization_repo(self):
        return AsyncMock(spec=RateCustomizationRepo)

    @pytest.fixture
    def service(self, category_repo, customization_repo):
        return RateCategoriesService(category_repo, customization_repo)

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        category.cost_per_mile = 0.65
        category.rate_customization_id = uuid4()
        return category

    @pytest.mark.asyncio
    async def test_edit_category_success(
        self, service, category_repo, customization_repo, mock_category, user_id
    ):
        category_id = uuid4()
        dto = EditRateCategoryDTO(name="Premium", cost_per_mile=0.85)
        customization_repo.is_irs_customization.return_value = False 
        category_repo.get.return_value = mock_category
        category_repo.get_by_customization_and_name.return_value = None
        category_repo.save.return_value = mock_category

        with patch.object(service, 'get_category', return_value=mock_category) as mock_get:
            result = await service.edit_category(user_id, category_id, dto)

        assert result == mock_category
        mock_get.assert_called_once_with(user_id, category_id)
        category_repo.save.assert_called()

    @pytest.mark.asyncio
    async def test_edit_category_not_found(self, service, category_repo, user_id):
        category_id = uuid4()
        dto = EditRateCategoryDTO(name="Premium")
        category_repo.get.return_value = None

        with pytest.raises(RateCategoryNotFoundError):
            await service.edit_category(user_id, category_id, dto)

    @pytest.mark.asyncio
    async def test_edit_category_duplicate_name(
        self, service, category_repo, customization_repo, mock_category, user_id
    ):
        category_id = uuid4()
        dto = EditRateCategoryDTO(name="Premium")
        other_category = MagicMock(spec=RateCategory)
        other_category.id = uuid4()
        
        customization_repo.is_irs_customization.return_value = False  
        category_repo.get_by_customization_and_name.return_value = other_category

        with patch.object(service, 'get_category', return_value=mock_category):
            with pytest.raises(DuplicateRateCategoryError):
                await service.edit_category(user_id, category_id, dto)

    @pytest.mark.asyncio
    async def test_edit_category_no_changes(self, service, category_repo, customization_repo, mock_category, user_id):
        category_id = uuid4()
        dto = EditRateCategoryDTO()
        customization_repo.is_irs_customization.return_value = False  
        category_repo.save.return_value = mock_category

        with patch.object(service, 'get_category', return_value=mock_category) as mock_get:
            result = await service.edit_category(user_id, category_id, dto)

        assert result == mock_category
        mock_get.assert_called_once_with(user_id, category_id)
        category_repo.save.assert_called()

    @pytest.mark.asyncio
    async def test_edit_category_irs_blocked(
        self, service, customization_repo, mock_category, user_id
    ):
        category_id = uuid4()
        dto = EditRateCategoryDTO(name="Premium", cost_per_mile=0.85)
        customization_repo.is_irs_customization.return_value = True 

        with patch.object(service, 'get_category', return_value=mock_category):
            with pytest.raises(InvalidRateCategoryDataError) as exc_info:
                await service.edit_category(user_id, category_id, dto)
        
        assert "Cannot modify IRS standard rate categories" in str(exc_info.value)


class TestRateCategoriesServiceDelete:

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def category_repo(self):
        return AsyncMock(spec=RateCategoryRepo)

    @pytest.fixture
    def customization_repo(self):
        return AsyncMock(spec=RateCustomizationRepo)

    @pytest.fixture
    def service(self, category_repo, customization_repo):
        return RateCategoriesService(category_repo, customization_repo)

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        return category

    @pytest.mark.asyncio
    async def test_delete_category_success(
        self, service, category_repo, customization_repo, mock_category, user_id
    ):
        category_id = uuid4()
        customization_repo.is_irs_customization.return_value = False 
        category_repo.delete.return_value = None

        with patch.object(service, 'get_category', return_value=mock_category) as mock_get:
            await service.delete_category(user_id, category_id)

        mock_get.assert_called_once_with(user_id, category_id)
        category_repo.delete.assert_called_once_with(mock_category)

    @pytest.mark.asyncio
    async def test_delete_category_not_found(self, service, category_repo, user_id):
        category_id = uuid4()
        
        with patch.object(service, 'get_category', side_effect=RateCategoryNotFoundError("Category not found")):
            with pytest.raises(RateCategoryNotFoundError):
                await service.delete_category(user_id, category_id)

    @pytest.mark.asyncio
    async def test_delete_category_irs_blocked(
        self, service, customization_repo, mock_category, user_id
    ):
        category_id = uuid4()
        customization_repo.is_irs_customization.return_value = True  

        with patch.object(service, 'get_category', return_value=mock_category):
            with pytest.raises(InvalidRateCategoryDataError) as exc_info:
                await service.delete_category(user_id, category_id)
        
        assert "Cannot delete IRS standard rate categories" in str(exc_info.value)
