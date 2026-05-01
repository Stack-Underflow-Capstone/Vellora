from functools import lru_cache
from typing import Callable, Dict

from app.config import settings

from .base import OAuthProviderBase, OAuthProviderError
from .google import GoogleOAuthProvider


class OAuthProviderNotConfigured(OAuthProviderError):
    """Raised when a requested provider is not configured."""


class OAuthProviderUnsupported(OAuthProviderError):
    """Raised when a requested provider is not supported."""


ProviderFactory = Callable[..., OAuthProviderBase]


@lru_cache(maxsize=8)
def _provider_factories() -> Dict[str, ProviderFactory]:
    return {
        "google": GoogleOAuthProvider,
    }


def get_provider(name: str) -> OAuthProviderBase:
    normalized = name.lower()
    factories = _provider_factories()
    factory = factories.get(normalized)
    if factory is None:
        raise OAuthProviderUnsupported(f"Provider '{name}' is not supported")

    provider_config = getattr(settings.OAUTH_PROVIDERS, normalized, None)
    if provider_config is None:
        raise OAuthProviderUnsupported(f"Provider '{name}' is not supported")

    if not provider_config.client_id or not provider_config.client_secret or not provider_config.redirect_uri:
        raise OAuthProviderNotConfigured(
            f"Provider '{name}' is missing client configuration (client_id, client_secret, redirect_uri)"
        )

    return factory(
        client_id=provider_config.client_id,
        client_secret=provider_config.client_secret,
        redirect_uri=provider_config.redirect_uri,
        scopes=provider_config.scopes,
    )
