import logging
from .base import EmailServiceBase, EmailMessage

logger = logging.getLogger(__name__)


class MockEmailService(EmailServiceBase):
    def __init__(self, sender_email: str = "mock@vellora.local"):
        self.sender_email = sender_email
    
    async def send_email(self, message: EmailMessage) -> bool:
        logger.info(f"[MOCK EMAIL] Would send email:")
        logger.info(f"  From: {self.sender_email}")
        logger.info(f"  To: {[r.email for r in message.recipients]}")
        logger.info(f"  Subject: {message.subject}")
        logger.info(f"  Body length: {len(message.html_body or message.text_body or '')} chars")
        return True
    
    async def verify_sender_email(self, email: str) -> bool:
        logger.info(f"[MOCK EMAIL] Would verify sender email: {email}")
        return True
    
    def get_sender_email(self) -> str:
        return self.sender_email

