"""
Test helpers for user authentication integration
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock
from httpx import AsyncClient

from app.modules.users.models import User, UserRole


@pytest.fixture
async def test_user():
    """Create a test user object"""
    return User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        role=UserRole.user
    )


@pytest.fixture
def user_id():
    """Generate a test user ID"""
    return uuid4()


async def register(client: AsyncClient, email: str, password: str):
    """Helper function to register a user"""
    return await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "username": email.split('@')[0],
            "password": password
        }
    )


async def login(client: AsyncClient, email: str, password: str):
    """Helper function to login a user"""
    return await client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )


def create_auth_headers(access_token: str):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def authenticated_client(client: AsyncClient):
    """Create an authenticated client"""
    # Register and login user
    await register(client, email="authtest@example.com", password="TestPass123!")
    login_response = await login(client, email="authtest@example.com", password="TestPass123!")
    
    tokens = login_response.json()
    access_token = tokens["access_token"]
    headers = create_auth_headers(access_token)
    
    class AuthenticatedClient:
        def __init__(self, client, headers):
            self.client = client
            self.headers = headers
            
        async def get(self, url, **kwargs):
            return await self.client.get(url, headers=self.headers, **kwargs)
            
        async def post(self, url, **kwargs):
            return await self.client.post(url, headers=self.headers, **kwargs)
            
        async def put(self, url, **kwargs):
            return await self.client.put(url, headers=self.headers, **kwargs)
            
        async def patch(self, url, **kwargs):
            return await self.client.patch(url, headers=self.headers, **kwargs)
            
        async def delete(self, url, **kwargs):
            return await self.client.delete(url, headers=self.headers, **kwargs)
    
    return AuthenticatedClient(client, headers)


class MockRepo:
    """Base mock repository with user filtering support"""
    
    def __init__(self):
        self.get = AsyncMock()
        self.list = AsyncMock() 
        self.save = AsyncMock()
        self.delete = AsyncMock()
        
    def setup_user_filtering(self, user_id: uuid4):
        """Setup mock to return data only for specific user"""
        def filter_by_user(*args, **kwargs):
            # Check if user_id is provided and matches
            if 'user_id' in kwargs:
                if kwargs['user_id'] != user_id:
                    return None
            return AsyncMock()
        
        self.get.side_effect = filter_by_user
        self.list.side_effect = filter_by_user