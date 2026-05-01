from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class PushNotificationPort(ABC):
    
    @abstractmethod
    async def send_notification(self, device_tokens: List[str], title: str, message: str, data: Optional[dict] = None) -> bool:
        pass
    
    @abstractmethod
    async def send_to_user(self, user_id: UUID, title: str, message: str, data: Optional[dict] = None) -> bool:
        pass