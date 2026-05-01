from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    verify_password,
)
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.service import UserService

from .repository import RefreshTokenRepository
from .schemas import AuthResponse, RegisterRequest, RefreshResponse, TokenPair


class AuthService:
    """Coordinates authentication flows including OAuth token issuance."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.refresh_repo = RefreshTokenRepository(session)

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        existing = await self.user_service.get_by_email(payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with that email already exists.",
            )

        user = await self.user_service.create_user(
            UserCreate(
                email=payload.email,
                password=payload.password,
                full_name=payload.full_name,
                role=payload.role,
            )
        )
        return await self.finalize_authentication(user, revoke_existing=False)

    async def login(self, email: str, password: str) -> AuthResponse:
        user = await self.user_service.get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password authentication is not available for this account.",
            )
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

        return await self.finalize_authentication(user, revoke_existing=True)

    async def refresh(self, refresh_token: str) -> RefreshResponse:
        stored_token = await self.refresh_repo.get_active(refresh_token)
        if not stored_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        await self.refresh_repo.revoke(stored_token)
        token_pair = await self._issue_tokens(stored_token.user_id)
        await self.session.commit()

        return RefreshResponse(tokens=token_pair)

    async def logout(self, refresh_token: str) -> None:
        stored_token = await self.refresh_repo.get_active(refresh_token)
        if stored_token:
            await self.refresh_repo.revoke(stored_token)
            await self.session.commit()

    async def get_user_from_token(self, token: str) -> User:
        try:
            payload = decode_access_token(token)
        except TokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            ) from exc

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject",
            )

        user = await self.user_service.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        return user

    async def finalize_authentication(self, user: User, *, revoke_existing: bool = True) -> AuthResponse:
        if revoke_existing:
            await self.refresh_repo.revoke_all_for_user(user.id)
        token_pair = await self._issue_tokens(user.id)
        await self.session.commit()
        await self.session.refresh(user)

        return AuthResponse(
            user=UserRead.model_validate(user, from_attributes=True),
            tokens=token_pair,
        )

    async def _issue_tokens(self, user_id: UUID) -> TokenPair:
        access_token = create_access_token(
            subject=str(user_id),
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        refresh_token_value = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_repo.create(user_id=user_id, raw_token=refresh_token_value, expires_at=expires_at)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token_value,
            access_token_expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            refresh_token_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
