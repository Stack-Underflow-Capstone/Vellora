from typing import Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.schemas import UserRead
from app.modules.users.models import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None
    role: UserRole = Field(default=UserRole.EMPLOYEE)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    access_token_expires_in: int
    refresh_token_expires_in: int


class AuthResponse(BaseModel):
    user: UserRead
    tokens: TokenPair

    model_config = ConfigDict(from_attributes=True)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class RefreshResponse(BaseModel):
    tokens: TokenPair


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class OAuthAuthorizeResponse(BaseModel):
    provider: str
    authorization_url: AnyUrl
    state: str
    redirect_uri: AnyUrl


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
