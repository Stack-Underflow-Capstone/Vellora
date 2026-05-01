from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import OAuthAccount, OAuthState, RefreshToken


def _hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


class RefreshTokenRepository:
    """Persistence layer for refresh tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: UUID, raw_token: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=_hash_token(raw_token),
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_active(self, raw_token: str) -> Optional[RefreshToken]:
        hashed = _hash_token(raw_token)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == hashed,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        token = result.scalar_one_or_none()
        if token and _ensure_timezone(token.expires_at) <= datetime.now(timezone.utc):
            return None
        return token

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        self.session.add(token)

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)


class OAuthStateRepository:
    """Persistence layer for OAuth state tracking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        provider: str,
        state: str,
        redirect_uri: str | None,
        code_verifier: str | None,
        expires_at: datetime,
    ) -> OAuthState:
        oauth_state = OAuthState(
            provider=provider,
            state=state,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            expires_at=expires_at,
        )
        self.session.add(oauth_state)
        await self.session.flush()
        return oauth_state

    async def get_by_provider_state(self, provider: str, state_value: str) -> Optional[OAuthState]:
        stmt = select(OAuthState).where(
            OAuthState.provider == provider,
            OAuthState.state == state_value,
        )
        result = await self.session.execute(stmt)
        oauth_state = result.scalar_one_or_none()
        if oauth_state is None:
            return None
        now = datetime.now(timezone.utc)
        if _ensure_timezone(oauth_state.expires_at) <= now:
            return None
        return oauth_state

    async def consume(self, provider: str, state_value: str) -> Optional[OAuthState]:
        stmt = select(OAuthState).where(
            OAuthState.provider == provider,
            OAuthState.state == state_value,
        )
        result = await self.session.execute(stmt)
        oauth_state = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if (
            oauth_state is None
            or oauth_state.consumed_at is not None
            or _ensure_timezone(oauth_state.expires_at) <= now
        ):
            return None

        oauth_state.consumed_at = now
        self.session.add(oauth_state)
        await self.session.flush()
        return oauth_state


def _ensure_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class OAuthAccountRepository:
    """Persistence layer for linked OAuth accounts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider_account(
        self, provider: str, provider_account_id: str
    ) -> Optional[OAuthAccount]:
        stmt = (
            select(OAuthAccount)
            .where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == provider_account_id,
            )
            .options(selectinload(OAuthAccount.user))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_tokens(
        self,
        account: OAuthAccount,
        *,
        email: str | None,
        access_token: str | None,
        refresh_token: str | None,
        token_type: str | None,
        scope: str | None,
        expires_at: datetime | None,
    ) -> OAuthAccount:
        account.email = email or account.email
        account.access_token = access_token
        account.refresh_token = refresh_token
        account.token_type = token_type
        account.scope = scope
        account.expires_at = expires_at
        self.session.add(account)
        await self.session.flush()
        return account

    async def upsert(
        self,
        *,
        user_id: UUID,
        provider: str,
        provider_account_id: str,
        email: str | None,
        access_token: str | None,
        refresh_token: str | None,
        token_type: str | None,
        scope: str | None,
        expires_at: datetime | None,
    ) -> OAuthAccount:
        existing = await self.get_by_provider_account(provider, provider_account_id)
        if existing:
            return await self.update_tokens(
                existing,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                scope=scope,
                expires_at=expires_at,
            )
        else:
            account = OAuthAccount(
                user_id=user_id,
                provider=provider,
                provider_account_id=provider_account_id,
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
                scope=scope,
                expires_at=expires_at,
            )
            self.session.add(account)

            await self.session.flush()
            return account
