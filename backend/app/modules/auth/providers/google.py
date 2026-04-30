from urllib.parse import urlencode

import httpx

from .base import OAuthProviderBase, OAuthProviderError
from .types import OAuthToken, OAuthUserInfo


class GoogleOAuthProvider(OAuthProviderBase):
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    @property
    def name(self) -> str:
        return "google"

    def build_authorization_url(self, *, state: str, redirect_uri: str | None = None) -> str:
        target_redirect = redirect_uri or self.redirect_uri
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": target_redirect,
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(
        self,
        *,
        code: str,
        redirect_uri: str | None = None,
    ) -> OAuthToken:
        target_redirect = redirect_uri or self.redirect_uri
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": target_redirect,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(self.TOKEN_URL, data=data)

        if response.status_code >= 400:
            raise OAuthProviderError(f"Google token exchange failed: {response.text}")

        payload = response.json()
        return OAuthToken(
            access_token=payload["access_token"],
            token_type=payload.get("token_type"),
            refresh_token=payload.get("refresh_token"),
            expires_in=payload.get("expires_in"),
            scope=payload.get("scope"),
            id_token=payload.get("id_token"),
        )

    async def fetch_user_info(self, token: OAuthToken) -> OAuthUserInfo:
        headers = {"Authorization": f"Bearer {token.access_token}"}

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.USERINFO_URL, headers=headers)

        if response.status_code >= 400:
            raise OAuthProviderError(f"Google userinfo request failed: {response.text}")

        payload = response.json()
        return OAuthUserInfo(
            subject=payload["sub"],
            email=payload.get("email"),
            full_name=payload.get("name"),
            email_verified=payload.get("email_verified"),
        )
