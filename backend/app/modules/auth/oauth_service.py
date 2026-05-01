import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.config import settings
from app.modules.users.service import UserService

from .providers.base import OAuthProviderError
from .providers.registry import get_provider
from .repository import OAuthAccountRepository, OAuthStateRepository
from .schemas import AuthResponse, OAuthAuthorizeResponse
from .service import AuthService


class OAuthService:
    """Coordinates external OAuth providers with the local auth system."""

    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service
        self.session = auth_service.session
        self.user_service = UserService(self.session)
        self.state_repository = OAuthStateRepository(self.session)
        self.account_repository = OAuthAccountRepository(self.session)

    async def get_authorization_url(self, provider_name: str, redirect_uri: Optional[str]) -> OAuthAuthorizeResponse:
        provider = get_provider(provider_name)
        state_value = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.OAUTH_STATE_TTL_SECONDS)
        target_redirect = redirect_uri or provider.redirect_uri
        if not target_redirect:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="redirect_uri must be provided either in the request or configuration.",
            )

        await self.state_repository.create(
            provider=provider.name,
            state=state_value,
            redirect_uri=target_redirect,
            code_verifier=None,
            expires_at=expires_at,
        )
        await self.session.commit()

        authorization_url = provider.build_authorization_url(state=state_value, redirect_uri=target_redirect)
        return OAuthAuthorizeResponse(
            provider=provider.name,
            authorization_url=authorization_url,
            state=state_value,
            redirect_uri=target_redirect,
        )

    async def handle_callback(
        self,
        provider_name: str,
        *,
        code: str,
        state: str,
        redirect_uri: Optional[str],
    ) -> AuthResponse:
        provider = get_provider(provider_name)
        state_record = await self.state_repository.consume(provider.name, state)
        if state_record is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired state parameter.")

        target_redirect = redirect_uri or state_record.redirect_uri or provider.redirect_uri
        if not target_redirect:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redirect URI missing for callback exchange.",
            )

        try:
            token = await provider.exchange_code(code=code, redirect_uri=target_redirect)
            user_info = await provider.fetch_user_info(token)
        except OAuthProviderError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not user_info.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provider did not return an email address.",
            )

        account = await self.account_repository.get_by_provider_account(provider.name, user_info.subject)

        if account:
            user = account.user
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OAuth account is not linked to a user.",
                )
            await self.account_repository.update_tokens(
                account,
                email=user_info.email,
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                token_type=token.token_type,
                scope=token.scope,
                expires_at=token.expires_at(),
            )
        else:
            user = await self.user_service.ensure_user_for_oauth(email=user_info.email, full_name=user_info.full_name)
            await self.account_repository.upsert(
                user_id=user.id,
                provider=provider.name,
                provider_account_id=user_info.subject,
                email=user_info.email,
                access_token=token.access_token,
                refresh_token=token.refresh_token,
                token_type=token.token_type,
                scope=token.scope,
                expires_at=token.expires_at(),
            )

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled.")

        return await self.auth_service.finalize_authentication(user, revoke_existing=True)
