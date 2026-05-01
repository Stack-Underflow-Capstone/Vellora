from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class EmailRecipient:
    email: str
    name: Optional[str] = None


@dataclass
class EmailAttachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"
    content_id: Optional[str] = None


@dataclass
class EmailMessage:
    subject: str
    recipients: List[EmailRecipient]
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    attachments: List[EmailAttachment] = None
    reply_to: Optional[str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        
        if not self.html_body and not self.text_body:
            raise ValueError("Either html_body or text_body must be provided")

#Abstract base class for email services
class EmailServiceBase(ABC):
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        pass
    
    @abstractmethod
    async def verify_sender_email(self, email: str) -> bool:
        pass
    
    @abstractmethod
    def get_sender_email(self) -> str:
        pass