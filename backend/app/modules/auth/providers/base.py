from abc import ABC, abstractmethod
from typing import Sequence

from .types import OAuthToken, OAuthUserInfo


class OAuthProviderError(RuntimeError):
    """Raised when a provider call fails."""


class OAuthProviderBase(ABC):
    """Abstract provider describing required OAuth behaviour."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Sequence[str],
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = list(scopes)

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def build_authorization_url(self, *, state: str, redirect_uri: str | None = None) -> str:
        ...

    @abstractmethod
    async def exchange_code(
        self,
        *,
        code: str,
        redirect_uri: str | None = None,
    ) -> OAuthToken:
        ...

    @abstractmethod
    async def fetch_user_info(self, token: OAuthToken) -> OAuthUserInfo:
        ...
