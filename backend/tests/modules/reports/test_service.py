import pytest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.reports.service import ReportsService
from app.modules.reports.repository import ReportRepository
from app.modules.reports.schemas import GenerateReportDTO, AnalyticsResponse
from app.modules.reports.models import Report, ReportStatus
from app.modules.reports.exceptions import (
    ReportNotFoundError, ReportPermissionError, ReportRateLimitError,
    ReportSystemLimitError, ReportMaxRetriesError, ReportInvalidStateError,
    ReportExpiredError, ReportPersistenceError, InvalidMonthAnalyticsError,
    InvalidDataAnalyticsError
)
from app.modules.users.models import User


class TestReportsService:

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock(spec=ReportRepository)

    @pytest.fixture
    def mock_data_builder(self):
        return AsyncMock()

    @pytest.fixture
    def mock_renderer(self):
        renderer = MagicMock()
        renderer.render.return_value = b"pdf_content"
        return renderer

    @pytest.fixture
    def mock_storage(self):
        # Mock the storage methods directly instead of using real S3ReportStorage
        storage = MagicMock()
        storage.exists.return_value = True
        storage.get_signed_url.return_value = "http://example.com/report.pdf"
        storage.save.return_value = "report_file.pdf"
        return storage

    @pytest.fixture
    def mock_queue(self):
        # Mock the queue methods directly instead of using real ReportQueue
        queue = MagicMock()
        queue.send.return_value = None
        return queue

    @pytest.fixture
    def service(self, mock_session, mock_repo, mock_data_builder, 
                mock_renderer, mock_storage, mock_queue):
        return ReportsService(
            mock_session, mock_repo, mock_data_builder,
            mock_renderer, mock_storage, mock_queue
        )

    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def report_id(self):
        return uuid4()

    @pytest.fixture
    def generate_dto(self):
        return GenerateReportDTO(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )

    @pytest.fixture
    def sample_report(self, user_id, report_id):
        report = MagicMock(spec=Report)
        report.id = report_id
        report.user_id = user_id
        report.status = ReportStatus.pending
        report.retry_attempts = 0
        report.expires_at = None
        report.file_name = "test-report.pdf"
        # Set these as attributes that can be modified during tests
        report.completed_at = None
        report.file_url = None
        return report


class TestGenerateReport(TestReportsService):

    async def test_generate_report_success(
        self, service, user_id, generate_dto, mock_repo, mock_session, mock_queue
    ):
        mock_report = MagicMock(spec=Report)
        mock_repo.create.return_value = mock_report
        
        # Mock rate limit validation
        mock_session.scalar.return_value = 0

        result = await service.generate_report(user_id, generate_dto)

        mock_repo.create.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_queue.send.assert_called_once()
        assert result == mock_report

    async def test_generate_report_system_limit_exceeded(
        self, service, user_id, generate_dto, mock_session
    ):
        mock_session.scalar.return_value = 51  # Over SYSTEM_MAX

        with pytest.raises(ReportSystemLimitError):
            await service.generate_report(user_id, generate_dto)

    async def test_generate_report_user_rate_limit_recent(
        self, service, user_id, generate_dto, mock_session
    ):
        # Mock system limit check (pass) and user rate limit (fail)
        mock_session.scalar.side_effect = [0, 1, 0]  # system, recent, daily

        with pytest.raises(ReportRateLimitError) as exc_info:
            await service.generate_report(user_id, generate_dto)
        
        assert "Too many requests" in str(exc_info.value)

    async def test_generate_report_user_daily_limit(
        self, service, user_id, generate_dto, mock_session
    ):
        # Mock system limit check (pass), recent (pass), daily (fail)
        mock_session.scalar.side_effect = [0, 0, 5]

        with pytest.raises(ReportRateLimitError) as exc_info:
            await service.generate_report(user_id, generate_dto)
        
        assert "Daily report limit reached" in str(exc_info.value)

    async def test_generate_report_persistence_error(
        self, service, user_id, generate_dto, mock_repo, mock_session
    ):
        mock_session.scalar.return_value = 0  # Pass rate limits
        mock_repo.create.side_effect = Exception("DB Error")

        with pytest.raises(ReportPersistenceError):
            await service.generate_report(user_id, generate_dto)
        
        mock_session.rollback.assert_called_once()


class TestRetryReport(TestReportsService):

    async def test_retry_report_success(
        self, service, user_id, report_id, sample_report, mock_repo, mock_session, mock_queue
    ):
        sample_report.status = ReportStatus.failed
        mock_repo.get_by_id.return_value = sample_report
        mock_session.scalar.return_value = 0  # Pass rate limit

        result = await service.retry_report(report_id, user_id)

        assert sample_report.status == ReportStatus.pending
        assert sample_report.retry_attempts == 1
        mock_repo.update.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_queue.send.assert_called_once_with(str(report_id))
        assert result == sample_report

    async def test_retry_report_not_found(
        self, service, user_id, report_id, mock_repo, mock_session
    ):
        mock_repo.get_by_id.return_value = None
        mock_session.scalar.return_value = 0

        with pytest.raises(ReportNotFoundError):
            await service.retry_report(report_id, user_id)

    async def test_retry_report_permission_denied(
        self, service, user_id, report_id, sample_report, mock_repo, mock_session
    ):
        sample_report.user_id = uuid4()  # Different user
        sample_report.status = ReportStatus.failed
        mock_repo.get_by_id.return_value = sample_report
        mock_session.scalar.return_value = 0

        with pytest.raises(ReportPermissionError):
            await service.retry_report(report_id, user_id)

    async def test_retry_report_invalid_status(
        self, service, user_id, report_id, sample_report, mock_repo, mock_session
    ):
        sample_report.status = ReportStatus.pending  # Can't retry pending
        mock_repo.get_by_id.return_value = sample_report
        mock_session.scalar.return_value = 0

        with pytest.raises(ReportInvalidStateError):
            await service.retry_report(report_id, user_id)

    async def test_retry_report_max_attempts_reached(
        self, service, user_id, report_id, sample_report, mock_repo, mock_session
    ):
        sample_report.status = ReportStatus.failed
        sample_report.retry_attempts = 3  # At max
        mock_repo.get_by_id.return_value = sample_report
        mock_session.scalar.return_value = 0

        with pytest.raises(ReportMaxRetriesError):
            await service.retry_report(report_id, user_id)


class TestGetDownloadUrl(TestReportsService):

    async def test_get_download_url_success(
        self, service, user_id, report_id, sample_report, mock_repo, mock_storage
    ):
        sample_report.status = ReportStatus.completed
        sample_report.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        mock_repo.get_by_id.return_value = sample_report

        result = await service.get_download_url(report_id, user_id)

        assert result == "http://example.com/report.pdf"
        mock_storage.exists.assert_called_once_with(sample_report.file_name)
        mock_storage.get_signed_url.assert_called_once_with(sample_report.file_name)

    async def test_get_download_url_not_found(
        self, service, user_id, report_id, mock_repo
    ):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ReportNotFoundError):
            await service.get_download_url(report_id, user_id)

    async def test_get_download_url_permission_denied(
        self, service, user_id, report_id, sample_report, mock_repo
    ):
        sample_report.user_id = uuid4()  # Different user
        mock_repo.get_by_id.return_value = sample_report

        with pytest.raises(ReportPermissionError):
            await service.get_download_url(report_id, user_id)

    async def test_get_download_url_expired(
        self, service, user_id, report_id, sample_report, mock_repo, mock_session
    ):
        sample_report.status = ReportStatus.completed
        sample_report.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        mock_repo.get_by_id.return_value = sample_report

        with pytest.raises(ReportExpiredError):
            await service.get_download_url(report_id, user_id)
        
        assert sample_report.status == ReportStatus.expired
        mock_session.commit.assert_called_once()

    async def test_get_download_url_not_completed(
        self, service, user_id, report_id, sample_report, mock_repo
    ):
        sample_report.status = ReportStatus.pending
        sample_report.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        mock_repo.get_by_id.return_value = sample_report

        with pytest.raises(ReportInvalidStateError):
            await service.get_download_url(report_id, user_id)

    async def test_get_download_url_file_missing(
        self, service, user_id, report_id, sample_report, mock_repo, mock_storage, mock_session
    ):
        sample_report.status = ReportStatus.completed
        sample_report.expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        mock_repo.get_by_id.return_value = sample_report
        mock_storage.exists = MagicMock(return_value=False)

        with pytest.raises(ReportExpiredError):
            await service.get_download_url(report_id, user_id)
        
        assert sample_report.status == ReportStatus.expired
        mock_session.commit.assert_called_once()


class TestListUserReports(TestReportsService):

    async def test_list_user_reports_success(
        self, service, user_id, mock_repo, mock_session
    ):
        reports = [
            MagicMock(
                status=ReportStatus.completed, 
                expires_at=datetime.now(timezone.utc) + timedelta(days=30),
                requested_at=datetime.now(timezone.utc)
            ),
            MagicMock(
                status=ReportStatus.pending, 
                expires_at=None,
                requested_at=datetime.now(timezone.utc) - timedelta(hours=1)
            )
        ]
        mock_repo.list_for_user.return_value = reports

        result = await service.list_user_reports(user_id)

        # Should be sorted by requested_at, newest first
        assert len(result) == 2
        assert result[0].requested_at > result[1].requested_at
        mock_repo.list_for_user.assert_called_once_with(mock_session, user_id)

    async def test_list_user_reports_with_expired(
        self, service, user_id, mock_repo, mock_session
    ):
        expired_report = MagicMock(
            status=ReportStatus.completed, 
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            requested_at=datetime.now(timezone.utc)
        )
        valid_report = MagicMock(
            status=ReportStatus.completed, 
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            requested_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        
        reports = [expired_report, valid_report]
        mock_repo.list_for_user.return_value = reports

        result = await service.list_user_reports(user_id)

        # Expired report should be marked as expired
        assert expired_report.status == ReportStatus.expired
        assert valid_report.status == ReportStatus.completed
        mock_session.commit.assert_called_once()


class TestGenerateNow(TestReportsService):

    async def test_generate_now_success(
        self, service, report_id, sample_report, mock_repo, mock_data_builder,
        mock_renderer, mock_storage, mock_session
    ):
        mock_repo.get_by_id.return_value = sample_report
        mock_data_builder.build.return_value = {"test": "data"}
        mock_renderer.render.return_value = b"pdf_content"
        mock_storage.save.return_value = "report_file.pdf"

        result = await service.generate_now(report_id)

        assert result == sample_report
        assert sample_report.status == ReportStatus.completed
        assert sample_report.file_name == "report_file.pdf"
        assert sample_report.file_url == "report_file.pdf"
        assert sample_report.completed_at is not None
        assert sample_report.expires_at is not None
        
        mock_data_builder.build.assert_called_once_with(sample_report)
        mock_renderer.render.assert_called_once_with({"test": "data"})
        mock_storage.save.assert_called_once_with(report_id, b"pdf_content")
        mock_session.commit.assert_called_once()

    async def test_generate_now_not_found(
        self, service, report_id, mock_repo
    ):
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ReportNotFoundError):
            await service.generate_now(report_id)


class TestGetAnalytics(TestReportsService):

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        return user

    @pytest.fixture
    def mock_trip_data(self):
        """Mock trip data with category information"""
        data = MagicMock()
        trip1 = MagicMock()
        trip1.category_name = "Business"
        trip2 = MagicMock()
        trip2.category_name = "Business"
        trip3 = MagicMock()
        trip3.category_name = "Personal"
        data.trips = [trip1, trip2, trip3]
        data.total_miles = 150.5
        data.grand_total = 95.25
        return data

    @pytest.mark.asyncio
    async def test_get_analytics_success(
        self, service, mock_user, mock_data_builder, mock_trip_data
    ):
        mock_data_builder.build.return_value = mock_trip_data

        with patch('app.modules.reports.service.Report'):
            result = await service.get_analytics(mock_user, "January")

        mock_data_builder.build.assert_called_once()
        assert result.total_miles == 150.5
        assert result.grand_total == 95.25
        assert result.category_counts == {"Business": 2, "Personal": 1}

    @pytest.mark.asyncio
    async def test_get_analytics_invalid_month(self, service, mock_user):
        with pytest.raises(InvalidMonthAnalyticsError) as exc_info:
            await service.get_analytics(mock_user, "InvalidMonth")
        
        assert "Invalid Month" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_analytics_data_builder_failure(
        self, service, mock_user, mock_data_builder
    ):
        mock_data_builder.build.side_effect = Exception("Database error")

        with patch('app.modules.reports.service.Report'):
            with pytest.raises(InvalidDataAnalyticsError) as exc_info:
                await service.get_analytics(mock_user, "January")
        
        assert "Failed to gather data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_analytics_empty_trips(
        self, service, mock_user, mock_data_builder
    ):
        empty_data = MagicMock()
        empty_data.trips = []
        empty_data.total_miles = 0.0
        empty_data.grand_total = 0.0
        mock_data_builder.build.return_value = empty_data

        with patch('app.modules.reports.service.Report'):
            result = await service.get_analytics(mock_user, "February")

        assert result.total_miles == 0.0
        assert result.grand_total == 0.0
        assert result.category_counts == {}