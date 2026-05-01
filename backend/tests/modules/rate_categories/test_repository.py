import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.rate_categories.repository import RateCategoryRepo
from app.modules.rate_categories.models import RateCategory


class TestRateCategoryRepoSave:

    @pytest.fixture
    def repo(self, mock_db_session):
        return RateCategoryRepo(mock_db_session)

    @pytest.fixture
    def mock_category(self, sample_expense_id):
        category = MagicMock(spec=RateCategory)
        category.id = sample_expense_id
        category.name = "Standard"
        category.cost_per_mile = 0.65
        category.rate_customization_id = uuid4()
        return category

    @pytest.mark.asyncio
    async def test_save_category(self, repo, mock_db_session, mock_category):
        result = await repo.save(mock_category)

        mock_db_session.add.assert_called_once_with(mock_category)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_category)
        assert result == mock_category


class TestRateCategoryRepoGet:

    @pytest.fixture
    def repo(self, mock_db_session):
        return RateCategoryRepo(mock_db_session)

    @pytest.fixture
    def mock_category(self, sample_expense_id):
        category = MagicMock(spec=RateCategory)
        category.id = sample_expense_id
        category.name = "Standard"
        category.cost_per_mile = 0.65
        return category

    @pytest.mark.asyncio
    async def test_get_category_found(self, repo, mock_db_session, mock_category, sample_expense_id):
        mock_db_session.scalar.return_value = mock_category

        result = await repo.get(sample_expense_id)

        assert result == mock_category
        mock_db_session.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, repo, mock_db_session, sample_expense_id):
        mock_db_session.scalar.return_value = None

        result = await repo.get(sample_expense_id)

        assert result is None
        mock_db_session.scalar.assert_called_once()


class TestRateCategoryRepoGetByCustomizationId:

    @pytest.fixture
    def repo(self, mock_db_session):
        return RateCategoryRepo(mock_db_session)

    @pytest.fixture
    def mock_categories(self):
        categories = []
        for i in range(3):
            category = MagicMock(spec=RateCategory)
            category.id = uuid4()
            category.name = f"Category{i}"
            category.cost_per_mile = 0.5 + (i * 0.1)
            categories.append(category)
        return categories

    @pytest.mark.asyncio
    async def test_get_by_customization_id_found(self, repo, mock_db_session, mock_categories):
        customization_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_categories
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_customization_id(customization_id)

        assert result == mock_categories
        assert len(result) == 3
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_customization_id_empty(self, repo, mock_db_session):
        customization_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_customization_id(customization_id)

        assert result == []
        mock_db_session.execute.assert_called_once()


class TestRateCategoryRepoGetByCustomizationAndName:

    @pytest.fixture
    def repo(self, mock_db_session):
        return RateCategoryRepo(mock_db_session)

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        category.cost_per_mile = 0.65
        return category

    @pytest.mark.asyncio
    async def test_get_by_customization_and_name_found(self, repo, mock_db_session, mock_category):
        customization_id = uuid4()
        name = "Standard"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_customization_and_name(customization_id, name)

        assert result == mock_category
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_customization_and_name_not_found(self, repo, mock_db_session):
        customization_id = uuid4()
        name = "NonExistent"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_customization_and_name(customization_id, name)

        assert result is None
        mock_db_session.execute.assert_called_once()


class TestRateCategoryRepoDelete:

    @pytest.fixture
    def repo(self, mock_db_session):
        return RateCategoryRepo(mock_db_session)

    @pytest.fixture
    def mock_category(self):
        category = MagicMock(spec=RateCategory)
        category.id = uuid4()
        category.name = "Standard"
        return category

    @pytest.mark.asyncio
    async def test_delete_category_success(self, repo, mock_db_session, mock_category):
        await repo.delete(mock_category)

        mock_db_session.delete.assert_called_once_with(mock_category)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_category_returns_none(self, repo, mock_db_session, mock_category):
        result = await repo.delete(mock_category)

        assert result is None
