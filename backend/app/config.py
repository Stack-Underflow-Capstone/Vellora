from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthProviderConfig(BaseModel):
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    scopes: list[str] = Field(default_factory=list)


class OAuthProviders(BaseModel):
    google: OAuthProviderConfig = OAuthProviderConfig(scopes=["openid", "email", "profile"])
    microsoft: OAuthProviderConfig = OAuthProviderConfig(scopes=["openid", "email", "profile"])


class Settings(BaseSettings):
    DATABASE_URL: str
    FERNET_KEY: str | None = None

    USE_LOCALSTACK: bool = True
    AWS_ACCESS_KEY_ID: str = "test"
    AWS_SECRET_ACCESS_KEY: str = "test"
    AWS_REGION: str = "us-east-1"
    LOCALSTACK_ENDPOINT: str = "http://localhost:4566"
    REPORTS_QUEUE: str = "generate-reports-queue"
    REPORTS_BUCKET: str = "vellora-s3-bucket"
    
    #will change later(maybe)
    EMAIL_SENDER: str = "noreply@resend.dev"
    EMAIL_ENABLED: bool = True
    EMAIL_PROVIDER: str = "mock"
    RESEND_API_KEY: str = ""
    BACKEND_URL: str = "http://localhost:8000"

    JWT_SECRET_KEY: str = Field(
        default="__change_me_in_prod_please_1234567890abcd",
        min_length=32,
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AI_AGENT_ENABLED: bool = False
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    AI_TIMEOUT_SECONDS: int = 30
    AI_RATE_LIMIT_PER_MINUTE: int = 12
    AI_MAX_METADATA_KEYS: int = 20
    AI_MAX_METADATA_VALUE_LENGTH: int = 500
    AI_MAX_MISSING_DETAILS: int = 8
    WEATHER_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_TIMEOUT_SECONDS: int = 10
    OAUTH_STATE_TTL_SECONDS: int = 600
    OAUTH_PROVIDERS: OAuthProviders = OAuthProviders()
    AWS_S3_BUCKET: str | None = None
    AWS_REGION: str | None = None
    AWS_S3_ENDPOINT_URL: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    RECEIPT_URL_EXPIRES_SECONDS: int = 900

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_nested_delimiter="__",
    )

settings = Settings()


def get_settings() -> Settings:
    return settings
