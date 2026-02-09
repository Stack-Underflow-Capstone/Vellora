import logging
import os
from typing import Optional

from app.config import settings
from app.modules.users.models import User
from app.modules.reports.models import Report
from .base import EmailServiceBase, EmailMessage, EmailRecipient
from .exceptions import EmailServiceError
from .resend import ResendEmailService
from .mock import MockEmailService
from .templates import render_report_ready_email, render_report_ready_text, render_report_failed_email

logger = logging.getLogger(__name__)


class EmailService:    
    def __init__(self, provider: Optional[EmailServiceBase] = None):
        self.provider = provider or self._get_default_provider()
        self.enabled = settings.EMAIL_ENABLED
    
    def _get_default_provider(self) -> EmailServiceBase:
        if settings.EMAIL_PROVIDER == "resend":
            return ResendEmailService(
                sender_email=settings.EMAIL_SENDER,
                api_key=settings.RESEND_API_KEY
            )
        elif settings.EMAIL_PROVIDER == "mock":
            return MockEmailService(sender_email=settings.EMAIL_SENDER)
        else:
            raise ValueError(f"Unknown email provider '{settings.EMAIL_PROVIDER}'. Supported providers: 'resend', 'mock'")
    
    async def send_report_ready_notification(self, user: User, report: Report, download_url: str) -> bool:
        if not self.enabled:
            logger.info("Email service disabled, skipping report ready notification")
            return False
        
        try:
            
            period = f"{report.start_date.strftime('%B %d, %Y')} - {report.end_date.strftime('%B %d, %Y')}"
            
            message = EmailMessage(
                subject="Your Expense Report is Ready - Vellora",
                recipients=[EmailRecipient(email=user.email, name=user.full_name)],
                html_body=render_report_ready_email(
                    user_name=user.full_name or user.email.split('@')[0],
                    report_url=download_url,
                    report_period=period
                ),
                text_body=render_report_ready_text(
                    user_name=user.full_name or user.email.split('@')[0],
                    report_url=download_url,
                    report_period=period
                )
            )
            
            success = await self.provider.send_email(message)
            if success:
                logger.info(f"Report ready notification sent to {user.email} for report {report.id}")
            else:
                logger.error(f"Failed to send report ready notification to {user.email} for report {report.id}")
            
            return success
            
        except EmailServiceError as e:
            logger.error(f"Email service error sending report notification to {user.email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending report notification to {user.email}: {str(e)}")
            return False
    
    async def send_report_failed_notification(self, user: User, report: Report) -> bool:
        if not self.enabled:
            logger.info("Email service disabled, skipping report failed notification")
            return False
        
        try:
            period = f"{report.start_date.strftime('%B %d, %Y')} - {report.end_date.strftime('%B %d, %Y')}"
            
            retry_url = f"{settings.BACKEND_URL}/api/v1/reports/{report.id}/retry"
            
            message = EmailMessage(
                subject="Report Generation Issue - Vellora",
                recipients=[EmailRecipient(email=user.email, name=user.full_name)],
                html_body=render_report_failed_email(
                    user_name=user.full_name or user.email.split('@')[0],
                    report_period=period,
                    retry_url=retry_url
                )
            )
            
            success = await self.provider.send_email(message)
            if success:
                logger.info(f"Report failed notification sent to {user.email} for report {report.id}")
            else:
                logger.error(f"Failed to send report failed notification to {user.email} for report {report.id}")
            
            return success
            
        except EmailServiceError as e:
            logger.error(f"Email service error sending report failure notification to {user.email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending report failure notification to {user.email}: {str(e)}")
            return False
    
    async def verify_sender_email(self) -> bool:
        try:
            return await self.provider.verify_sender_email(self.provider.get_sender_email())
        except Exception as e:
            logger.error(f"Error verifying sender email: {str(e)}")
            return False