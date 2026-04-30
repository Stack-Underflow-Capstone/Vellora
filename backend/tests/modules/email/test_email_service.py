import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import date

from app.infra.email.service import EmailService
from app.modules.users.models import User
from app.modules.reports.models import Report, ReportStatus


class TestEmailService:
    """Test email service with all dependencies mocked for CI/CD."""

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.email = "test@example.com"
        user.full_name = "Test User"
        return user
    
    @pytest.fixture
    def mock_report(self):
        report = MagicMock(spec=Report)
        report.id = uuid4()
        report.start_date = date(2024, 1, 1)
        report.end_date = date(2024, 1, 31)
        report.status = ReportStatus.completed
        return report

    @patch('app.infra.email.service.settings')
    async def test_send_report_ready_notification(self, mock_settings, mock_user, mock_report):
        """Test sending report ready notification with mocked provider."""
        # Mock settings
        mock_settings.EMAIL_ENABLED = True
        mock_settings.BACKEND_URL = "https://api.test.com"
        
        # Mock email provider
        mock_provider = AsyncMock()
        mock_provider.send_email.return_value = True
        
        email_service = EmailService(provider=mock_provider)
        
        result = await email_service.send_report_ready_notification(
            user=mock_user,
            report=mock_report,
            download_url="https://s3.example.com/report.pdf"
        )
        
        assert result is True
        mock_provider.send_email.assert_called_once()

    @patch('app.infra.email.service.settings')
    async def test_send_report_failed_notification(self, mock_settings, mock_user, mock_report):
        """Test sending report failed notification with mocked provider."""
        # Mock settings
        mock_settings.EMAIL_ENABLED = True
        mock_settings.BACKEND_URL = "https://api.test.com"
        
        # Mock email provider
        mock_provider = AsyncMock()
        mock_provider.send_email.return_value = True
        
        email_service = EmailService(provider=mock_provider)
        
        result = await email_service.send_report_failed_notification(
            user=mock_user,
            report=mock_report
        )
        
        assert result is True
        mock_provider.send_email.assert_called_once()

    @patch('app.infra.email.service.settings')
    async def test_email_service_disabled(self, mock_settings, mock_user, mock_report):
        """Test that emails are not sent when service is disabled."""
        mock_settings.EMAIL_ENABLED = False
        
        mock_provider = AsyncMock()
        email_service = EmailService(provider=mock_provider)
        
        result = await email_service.send_report_ready_notification(
            user=mock_user,
            report=mock_report,
            download_url="https://example.com/report.pdf"
        )
        
        assert result is False
        mock_provider.send_email.assert_not_called()