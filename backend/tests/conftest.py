import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


# Environment setup
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://test/oauth/google/callback")

os.environ.setdefault("OAUTH_GOOGLE_CLIENT_ID", "test-google-client-id")
os.environ.setdefault("OAUTH_GOOGLE_CLIENT_SECRET", "test-google-client-secret")
os.environ.setdefault("OAUTH_GOOGLE_REDIRECT_URI", "http://test/oauth/google/callback")

# AWS environment variables
os.environ.setdefault("USE_LOCALSTACK", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("LOCALSTACK_ENDPOINT", "http://localhost:4566")
os.environ.setdefault("REPORTS_BUCKET", "vellora-s3-bucket")
os.environ.setdefault("REPORTS_QUEUE", "generate-reports-queue")

# Email environment variables
os.environ.setdefault("EMAIL_ENABLED", "false")
os.environ.setdefault("EMAIL_PROVIDER", "resend")
os.environ.setdefault("EMAIL_SENDER", "noreply@test.com")
os.environ.setdefault("RESEND_API_KEY", "re_test_key_12345")
os.environ.setdefault("BACKEND_URL", "http://localhost:8000")

os.environ.setdefault("ENV", "test")
os.environ.setdefault("JWT_SECRET_KEY", "this_is_a_very_long_test_secret_key_32_chars_min")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRES_MIN", "1")
os.environ.setdefault("REFRESH_TOKEN_EXPIRES_MIN", "5")

if "FERNET_KEY" not in os.environ:
    from cryptography.fernet import Fernet
    os.environ["FERNET_KEY"] = Fernet.generate_key().decode()

if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Force SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DB_URL

from app.main import app as fastapi_app
from app.core.base import Base
from app.container import get_db  

try:
    from app.core.settings import get_settings as _get_settings_dep, Settings  
except Exception:
    _get_settings_dep = None
    Settings = None

@pytest.fixture
def mock_db_session():
    """Fixture for mocking AsyncSession"""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def sample_trip_id():
    """Fixture providing a sample trip UUID"""
    return uuid4()


@pytest.fixture
def sample_expense_id():
    """Fixture providing a sample expense UUID"""
    return uuid4()


@pytest.fixture
def sample_notification_id():
    """Fixture providing a sample notification UUID"""
    return uuid4()


@pytest.fixture
def sample_device_token():
    """Fixture providing a sample Expo device token"""
    return "ExponentPushToken[sample-test-token-123]"


@pytest.fixture
def mock_notification():
    """Fixture providing a mock notification object"""
    from app.modules.notifications.models import Notification, NotificationType
    notification = MagicMock(spec=Notification)
    notification.id = uuid4()
    notification.user_id = uuid4()
    notification.title = "Test Notification"
    notification.message = "Test message"
    notification.type = NotificationType.TRIP_STOP_REMINDER
    notification.is_read = False
    return notification


@pytest.fixture
def mock_device_token_obj():
    """Fixture providing a mock device token object"""
    from app.modules.notifications.models import UserDeviceToken
    token = MagicMock(spec=UserDeviceToken)
    token.id = uuid4()
    token.user_id = uuid4()
    token.device_token = "ExponentPushToken[test-token-123]"
    token.device_type = "ios"
    token.is_active = True
    return token


@pytest.fixture
def mock_expo_adapter():
    """Fixture providing a mock Expo notification adapter"""
    from app.infra.adapters.expo_notification_adapter import ExpoNotificationAdapter
    adapter = AsyncMock(spec=ExpoNotificationAdapter)
    adapter.send_notification.return_value = True
    adapter.send_to_user.return_value = True
    return adapter


@pytest.fixture(autouse=True)
def mock_aws_clients():
    """Mock AWS clients for all tests"""
    with patch('app.aws_client.get_s3_client') as mock_s3, \
         patch('app.aws_client.get_sqs_client') as mock_sqs:
        
        # Mock S3 client
        s3_client = MagicMock()
        s3_client.head_object.return_value = {}
        s3_client.generate_presigned_url.return_value = "http://example.com/signed-url"
        s3_client.put_object.return_value = {"ETag": "test-etag"}
        mock_s3.return_value = s3_client
        
        # Mock SQS client
        sqs_client = MagicMock()
        sqs_client.get_queue_url.return_value = {"QueueUrl": "test-queue-url"}
        sqs_client.send_message.return_value = {"MessageId": "test-message-id"}
        mock_sqs.return_value = sqs_client
        
        yield {'s3': s3_client, 'sqs': sqs_client}


# Event Loop
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """One session-scoped loop so the async engine/sessions share it."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Engine and Sessions 
@pytest_asyncio.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        future=True,
        echo=False,
        poolclass=StaticPool,  # keep one in-memory DB alive for the session
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def session_maker(async_engine):
    return async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

@pytest_asyncio.fixture()
async def async_session(session_maker):
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def patch_app_db_layer(async_engine, session_maker):
    """
    If app.infra.db defines module-level engine/sessionmaker, point them to the test engine.
    This prevents any code path from creating a Postgres asyncpg engine.
    """
    try:
        from app import infra as _infra
        from app.infra import db as db_module
    except Exception:
        return  

    # Patch globals commonly used in FastAPI templates
    if hasattr(db_module, "engine"):
        db_module.engine = async_engine  # use our SQLite engine
    if hasattr(db_module, "AsyncSessionLocal"):
        db_module.AsyncSessionLocal = session_maker

    # Some code binds metadata globally; ensure it's not bound to anything stale
    try:
        Base.metadata.bind = None  # use engine passed to run_sync, not a stale bind
    except Exception:
        pass

@pytest.fixture()
def app(async_session):
    async def _override_db():
        # yield an AsyncSession from our sessionmaker
        yield async_session

    fastapi_app.dependency_overrides[get_db] = _override_db

    if _get_settings_dep and Settings:
        def _override_settings():
            # Construct Settings with test DB + dummy oauth
            # Fill any required fields your app expects.
            return Settings(
                DATABASE_URL=TEST_DB_URL,
                JWT_SECRET_KEY=os.environ["JWT_SECRET_KEY"],
                JWT_ALGORITHM=os.environ.get("JWT_ALGORITHM", "HS256"),
                ACCESS_TOKEN_EXPIRES_MIN=int(os.environ.get("ACCESS_TOKEN_EXPIRES_MIN", "1")),
                REFRESH_TOKEN_EXPIRES_MIN=int(os.environ.get("REFRESH_TOKEN_EXPIRES_MIN", "5")),
                GOOGLE_CLIENT_ID=os.environ["GOOGLE_CLIENT_ID"],
                GOOGLE_CLIENT_SECRET=os.environ["GOOGLE_CLIENT_SECRET"],
                GOOGLE_REDIRECT_URI=os.environ["GOOGLE_REDIRECT_URI"],
            )
        fastapi_app.dependency_overrides[_get_settings_dep] = _override_settings

    return fastapi_app

@pytest_asyncio.fixture()
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# -------------------- Optional: clean-slate helper --------------------
@pytest_asyncio.fixture()
async def reset_database(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
