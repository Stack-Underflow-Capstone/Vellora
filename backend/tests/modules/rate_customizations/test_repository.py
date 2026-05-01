import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.modules.rate_customizations.repository import RateCustomizationRepo
from app.modules.rate_customizations.models import RateCustomization


class TestRateCustomizationRepoSave:

    @pytest.mark.asyncio
    async def test_save_customization(self, mock_db_session):
        repo = RateCustomizationRepo(mock_db_session)
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        customization.name = "Business Rates 2024"
        customization.description = "Standard business mileage rates"
        customization.year = 2024
        mock_db_session.refresh = AsyncMock()

        result = await repo.save(customization)

        mock_db_session.add.assert_called_once_with(customization)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(customization)
        assert result == customization


class TestRateCustomizationRepoGet:

    @pytest.mark.asyncio
    async def test_get_customization_found(self, mock_db_session):
        repo = RateCustomizationRepo(mock_db_session)
        customization_id = uuid4()
        customization = MagicMock(spec=RateCustomization)
        customization.id = customization_id
        customization.name = "Business Rates 2024"
        customization.year = 2024
        mock_db_session.scalar.return_value = customization

        result = await repo.get(customization_id)

        assert result == customization
        mock_db_session.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customization_not_found(self, mock_db_session):
        repo = RateCustomizationRepo(mock_db_session)
        customization_id = uuid4()
        mock_db_session.scalar.return_value = None

        result = await repo.get(customization_id)

        assert result is None
        mock_db_session.scalar.assert_called_once()


class TestRateCustomizationRepoDelete:

    @pytest.mark.asyncio
    async def test_delete_customization_success(self, mock_db_session):
        repo = RateCustomizationRepo(mock_db_session)
        customization = MagicMock(spec=RateCustomization)
        customization.id = uuid4()
        customization.name = "Business Rates 2024"
        customization.year = 2024

        result = await repo.delete(customization)

        mock_db_session.delete.assert_called_once_with(customization)
        mock_db_session.commit.assert_called_once()
        assert result is None
