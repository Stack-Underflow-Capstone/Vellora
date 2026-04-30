import pytest
from uuid import uuid4
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.modules.reports.repository import ReportRepository
from app.modules.reports.models import Report, ReportStatus


class TestReportRepository:

    @pytest.fixture
    def repo(self):
        return ReportRepository()

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def sample_report(self):
        return Report(
            user_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            status=ReportStatus.pending
        )

    async def test_create_report(self, repo, mock_session, sample_report):
        result = await repo.create(mock_session, sample_report)
        
        mock_session.add.assert_called_once_with(sample_report)
        mock_session.flush.assert_called_once()
        assert result == sample_report

    async def test_get_by_id_existing(self, repo, mock_session):
        report_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "mock_report"
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_by_id(mock_session, report_id)
        
        mock_session.execute.assert_called_once()
        assert result == "mock_report"

    async def test_get_by_id_not_found(self, repo, mock_session):
        report_id = uuid4()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_by_id(mock_session, report_id)
        
        assert result is None

    async def test_list_for_user(self, repo, mock_session):
        user_id = uuid4()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = ["report1", "report2"]
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result
        
        result = await repo.list_for_user(mock_session, user_id)
        
        mock_session.execute.assert_called_once()
        assert result == ["report1", "report2"]

    async def test_update_report(self, repo, mock_session, sample_report):
        result = await repo.update(mock_session, sample_report)
        
        mock_session.flush.assert_called_once()
        assert result == sample_report