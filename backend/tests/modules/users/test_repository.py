import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.modules.users.repository import UserRepository
from app.modules.users.models import User


class TestUserRepoGetByEmail:

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, repo, mock_db_session):
        mock_user = MagicMock(spec=User)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_email("test@example.com")

        assert result == mock_user
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_email("nobody@example.com")

        assert result is None


class TestUserRepoGetById:

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo, mock_db_session):
        mock_user = MagicMock(spec=User)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_id(uuid4())

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_id(uuid4())

        assert result is None


class TestUserRepoGetByUsername:

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_get_by_username_found(self, repo, mock_db_session):
        mock_user = MagicMock(spec=User)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_username("test_user")

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repo.get_by_username("nonexistent")

        assert result is None


class TestUserRepoUpdate:

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_update_user(self, repo, mock_db_session):
        mock_user = MagicMock(spec=User)

        result = await repo.update(mock_user)

        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_user)
        assert result == mock_user


class TestUserRepoCreate:

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    @pytest.mark.asyncio
    async def test_create_user(self, repo, mock_db_session):
        from app.modules.users.schemas import UserCreate

        dto = UserCreate(email="test@example.com", password="StrongPass1!", full_name="Test")

        result = await repo.create(dto, password_hash="hashed", username="test_abc123")

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_oauth_user(self, repo, mock_db_session):
        result = await repo.create_oauth_user(
            email="oauth@example.com",
            full_name="OAuth User",
            username="oauth_user123"
        )

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
