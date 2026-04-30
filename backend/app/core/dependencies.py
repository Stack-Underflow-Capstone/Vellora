from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import get_db
from app.core.storage import ReceiptStorage
from app.modules.auth.oauth_service import OAuthService
from app.modules.auth.service import AuthService
from app.modules.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", scheme_name="JWT")


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)


async def get_oauth_service(auth_service: AuthService = Depends(get_auth_service)) -> OAuthService:
    return OAuthService(auth_service)


async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.get_user_from_token(token)


def get_receipt_storage() -> ReceiptStorage:
    return ReceiptStorage.from_settings()
