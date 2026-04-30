import json
from typing import List, Optional
from uuid import UUID
import httpx
from app.config import settings
from app.config import settings
from app.modules.notifications.exceptions import NotificationDeliveryError
from app.modules.notifications.ports import PushNotificationPort
from app.modules.notifications.repository import DeviceTokenRepository


class ExpoNotificationAdapter(PushNotificationPort):
    
    def __init__(self, device_token_storage: DeviceTokenRepository = None):
        self.device_token_storage = device_token_storage
        self.expo_api_url = "https://exp.host/--/api/v2/push/send"
    
    async def send_notification(self, device_tokens: List[str], title: str, message: str, data: Optional[dict] = None) -> bool:
        if not device_tokens:
            return False
        
        valid_tokens = self._filter_valid_expo_tokens(device_tokens)
        if not valid_tokens:
            return False
        
        messages = []
        for token in valid_tokens:
            payload = {
                "to": token,
                "title": title,
                "body": message,
                "sound": "default",
            }
            
            if data:
                payload["data"] = data
            
            messages.append(payload)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.expo_api_url,
                    json=messages,
                    headers={
                        "Accept": "application/json",
                        "Accept-encoding": "gzip, deflate",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise NotificationDeliveryError(f"Expo API returned status {response.status_code}: {response.text}")
                
                result = response.json()
                
                if "data" in result:
                    errors = [item for item in result["data"] if item.get("status") == "error"]
                    if errors:
                        error_messages = [error.get("message", "Unknown error") for error in errors]
                        raise NotificationDeliveryError(f"Expo push errors: {error_messages}")
                
                return True
                
        except httpx.TimeoutException:
            raise NotificationDeliveryError("Expo push notification request timed out")
        except httpx.RequestError as e:
            raise NotificationDeliveryError(f"Expo push notification request failed: {e}")
        except Exception as e:
            raise NotificationDeliveryError(f"Failed to send push notification via Expo: {e}")
    
    async def send_to_user(self, user_id: UUID, title: str, message: str, data: Optional[dict] = None) -> bool:
        if not self.device_token_storage:
            return False
        
        device_tokens_objs = await self.device_token_storage.get_user_device_tokens(user_id, active_only=True)
        device_tokens = [token.device_token for token in device_tokens_objs]
        
        if not device_tokens:
            return False
        
        return await self.send_notification(device_tokens, title, message, data)
    
    def _filter_valid_expo_tokens(self, tokens: List[str]) -> List[str]:
        valid_tokens = []
        for token in tokens:
            if self._is_valid_expo_token(token):
                valid_tokens.append(token)
        return valid_tokens
    
    def _is_valid_expo_token(self, token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        return (
            (token.startswith("ExponentPushToken[") or token.startswith("ExpoPushToken[")) and
            token.endswith("]")
        )