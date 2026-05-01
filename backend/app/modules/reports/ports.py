from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.modules.users.models import User
from app.modules.reports.models import Report


class NotificationPort(ABC):
    
    @abstractmethod
    async def notify_report_completed(self, user: User, report: Report, download_url: str) -> bool:
        pass
    
    @abstractmethod
    async def notify_report_failed(self, user: User, report: Report, retry_url: str) -> bool:
        pass


class StoragePort(ABC):
    
    @abstractmethod
    def save(self, report_id: UUID, file_bytes: bytes) -> str:
        pass
    
    @abstractmethod
    def get_signed_url(self, key: str, expires_in: int = 300) -> str:
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass


class QueuePort(ABC):
    
    @abstractmethod
    def send(self, report_id: str) -> None:
        pass