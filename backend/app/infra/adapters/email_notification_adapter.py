import logging
from typing import Optional

from app.modules.reports.ports import NotificationPort
from app.modules.users.models import User
from app.modules.reports.models import Report
from app.infra.email.service import EmailService

logger = logging.getLogger(__name__)


class EmailNotificationAdapter(NotificationPort):
    
    def __init__(self, email_service: Optional[EmailService] = None):
        self.email_service = email_service or EmailService()
    
    async def notify_report_completed(self, user: User, report: Report, download_url: str) -> bool:
        try:
            return await self.email_service.send_report_ready_notification(
                user=user,
                report=report,
                download_url=download_url
            )
        except Exception as e:
            logger.warning(f"Failed to send report completion notification to {user.email}: {str(e)}")
            return False
    
    async def notify_report_failed(self, user: User, report: Report) -> bool:
        try:
            return await self.email_service.send_report_failed_notification(
                user=user,
                report=report
            )
        except Exception as e:
            logger.warning(f"Failed to send report failure notification to {user.email}: {str(e)}")
            return False