from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass(slots=True)
class OAuthToken:
    access_token: str
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    id_token: Optional[str] = None

    def expires_at(self) -> Optional[datetime]:
        if self.expires_in is None:
            return None
        return datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)


@dataclass(slots=True)
class OAuthUserInfo:
    subject: str
    email: Optional[str]
    full_name: Optional[str]
    email_verified: Optional[bool] = None
