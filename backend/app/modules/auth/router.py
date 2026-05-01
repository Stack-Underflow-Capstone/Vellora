from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_auth_service, get_current_user, get_oauth_service
from app.core.error_handler import error_handler
from app.modules.users.models import User
from app.modules.users.schemas import UserRead, UserUpdate


from .schemas import (
    AuthResponse,
    LogoutRequest,
    OAuthAuthorizeResponse,
    OAuthTokenResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
)
from .oauth_service import OAuthService
from .service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> AuthResponse:
    return await auth_service.register(payload)


@router.post("/token", response_model=OAuthTokenResponse)
async def issue_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> OAuthTokenResponse:
    auth_response = await auth_service.login(email=form_data.username, password=form_data.password)
    return OAuthTokenResponse(
        access_token=auth_response.tokens.access_token,
        token_type=auth_response.tokens.token_type,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    return await auth_service.login(email=form_data.username, password=form_data.password)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_tokens(
    payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)
) -> RefreshResponse:
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)) -> None:
    await auth_service.logout(payload.refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user, from_attributes=True)

@router.patch("/me", response_model=UserRead)
@error_handler
async def update_me(
    body: UserUpdate, 
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserRead:
    updated_user = await auth_service.user_service.update_user(current_user, body)
    return UserRead.model_validate(updated_user, from_attributes=True)

@router.get("/providers/{provider}/authorize", response_model=OAuthAuthorizeResponse)
async def authorize_provider(
    provider: str,
    redirect_uri: str | None = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
) -> OAuthAuthorizeResponse:
    return await oauth_service.get_authorization_url(provider, redirect_uri)


@router.get("/providers/{provider}/callback")
async def oauth_callback(
    request: Request,
    provider: str,
    code: str = Query(..., description="Authorization code returned by the provider."),
    state: str = Query(..., description="Opaque state value generated during authorization."),
    redirect_uri: str | None = None,
    oauth_service: OAuthService = Depends(get_oauth_service),
):
    accept_header = request.headers.get("accept", "")
    
    if "application/json" not in accept_header:
        from urllib.parse import quote
        from app.modules.auth.repository import OAuthStateRepository
        
        state_repo = OAuthStateRepository(oauth_service.session)
        state_record = await state_repo.get_by_provider_state(provider, state)
        
        if state_record is None:
            return HTMLResponse(
                content="""
                <html>
                    <body>
                        <h1>Authentication Error</h1>
                        <p>Invalid or expired state parameter.</p>
                    </body>
                </html>
                """,
                status_code=400
            )
        
        auth_response = await oauth_service.handle_callback(
            provider_name=provider,
            code=code,
            state=state,
            redirect_uri=redirect_uri,
        )
        
        access_token = quote(auth_response.tokens.access_token)
        app_deep_link = f"vellora://oauth/{provider}/callback?access_token={access_token}"
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="0;url={app_deep_link}">
                    <script>window.location.href = "{app_deep_link}";</script>
                </head>
                <body>
                    <p>Redirecting to app...</p>
                    <p>If you are not redirected, <a href="{app_deep_link}">click here</a>.</p>
                </body>
            </html>
            """
        )
    
    return await oauth_service.handle_callback(
        provider_name=provider,
        code=code,
        state=state,
        redirect_uri=redirect_uri,
    )
