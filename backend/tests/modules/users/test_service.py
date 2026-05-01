import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.modules.users.service import UserService
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserUpdate
from app.modules.users.models import User
from app.modules.users.exceptions import DuplicateUsernameError, InvalidPasswordError


class TestUserServiceCreateUser:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def service(self, repo):
        svc = UserService.__new__(UserService)
        svc.repository = repo
        return svc

    @pytest.mark.asyncio
    async def test_create_user_success(self, service, repo):
        from app.modules.users.schemas import UserCreate

        dto = UserCreate(email="test@example.com", password="StrongPass1!", full_name="Test User")
        repo.get_by_username.return_value = None
        mock_user = MagicMock(spec=User)
        repo.create.return_value = mock_user

        with patch("app.modules.users.service.hash_password", return_value="hashed_pw"):
            result = await service.create_user(dto)

        assert result == mock_user
        repo.create.assert_called_once()


class TestUserServiceGenerateUsername:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def service(self, repo):
        svc = UserService.__new__(UserService)
        svc.repository = repo
        return svc

    @pytest.mark.asyncio
    async def test_generate_username_with_full_name(self, service, repo):
        repo.get_by_username.return_value = None

        result = await service.generate_username(full_name="John Doe")

        assert result.startswith("john_doe")
        assert len(result) == len("john_doe") + 6

    @pytest.mark.asyncio
    async def test_generate_username_without_full_name(self, service, repo):
        repo.get_by_username.return_value = None

        result = await service.generate_username(full_name=None)

        assert result.startswith("user_")
        assert len(result) == len("user_") + 6

    @pytest.mark.asyncio
    async def test_generate_username_with_empty_name(self, service, repo):
        repo.get_by_username.return_value = None

        result = await service.generate_username(full_name="   ")

        assert result.startswith("user_")

    @pytest.mark.asyncio
    async def test_generate_username_retries_on_collision(self, service, repo):
        existing_user = MagicMock(spec=User)
        # First call collides, second succeeds
        repo.get_by_username.side_effect = [existing_user, None]

        result = await service.generate_username(full_name="Test User")

        assert result.startswith("test_user")
        assert repo.get_by_username.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_username_all_retries_exhausted(self, service, repo):
        existing_user = MagicMock(spec=User)
        # All retries collide
        repo.get_by_username.return_value = existing_user

        with pytest.raises(DuplicateUsernameError, match="Failed to generate a unique username"):
            await service.generate_username(full_name="Test User", max_retries=3)

        assert repo.get_by_username.call_count == 3


class TestUserServiceUpdateUser:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def service(self, repo):
        svc = UserService.__new__(UserService)
        svc.repository = repo
        return svc

    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.username = "old_username"
        user.full_name = "Old Name"
        user.password_hash = "hashed_old_password"
        return user

    @pytest.mark.asyncio
    async def test_update_full_name(self, service, repo, mock_user):
        dto = UserUpdate(full_name="New Name")
        repo.update.return_value = mock_user

        result = await service.update_user(mock_user, dto)

        assert mock_user.full_name == "New Name"
        repo.update.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_update_username_success(self, service, repo, mock_user):
        dto = UserUpdate(username="new_username")
        repo.get_by_username.return_value = None
        repo.update.return_value = mock_user

        result = await service.update_user(mock_user, dto)

        assert mock_user.username == "new_username"
        repo.update.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_update_username_to_own_username(self, service, repo, mock_user):
        """User updates to the same username they already have — should succeed."""
        dto = UserUpdate(username="old_username")
        existing = MagicMock(spec=User)
        existing.id = mock_user.id  # Same user
        repo.get_by_username.return_value = existing
        repo.update.return_value = mock_user

        result = await service.update_user(mock_user, dto)

        assert mock_user.username == "old_username"
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_username_duplicate(self, service, repo, mock_user):
        dto = UserUpdate(username="taken_username")
        other_user = MagicMock(spec=User)
        other_user.id = uuid4()  # Different user
        repo.get_by_username.return_value = other_user

        with pytest.raises(DuplicateUsernameError, match="Username already exists"):
            await service.update_user(mock_user, dto)

    @pytest.mark.asyncio
    async def test_change_password_success(self, service, repo, mock_user):
        dto = UserUpdate(current_password="OldPass123!", new_password="NewPass123!")
        repo.update.return_value = mock_user

        with patch("app.modules.users.service.verify_password", return_value=True), \
             patch("app.modules.users.service.hash_password", return_value="hashed_new"):
            result = await service.update_user(mock_user, dto)

        assert mock_user.password_hash == "hashed_new"
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, service, repo, mock_user):
        dto = UserUpdate(current_password="WrongPass1!", new_password="NewPass123!")

        with patch("app.modules.users.service.verify_password", return_value=False):
            with pytest.raises(InvalidPasswordError, match="Current password is incorrect"):
                await service.update_user(mock_user, dto)

    @pytest.mark.asyncio
    async def test_change_password_missing_current(self, service, repo, mock_user):
        dto = UserUpdate(new_password="NewPass123!")

        with pytest.raises(InvalidPasswordError, match="Current password is required"):
            await service.update_user(mock_user, dto)

    @pytest.mark.asyncio
    async def test_change_password_oauth_user_no_hash(self, service, repo, mock_user):
        """OAuth user has no password_hash — cannot change password."""
        mock_user.password_hash = None
        dto = UserUpdate(current_password="SomePass1!", new_password="NewPass123!")

        with pytest.raises(InvalidPasswordError):
            await service.update_user(mock_user, dto)

    @pytest.mark.asyncio
    async def test_update_no_fields(self, service, repo, mock_user):
        """Empty update should still call repo.update and succeed."""
        dto = UserUpdate()
        repo.update.return_value = mock_user

        result = await service.update_user(mock_user, dto)

        assert result == mock_user
        repo.update.assert_called_once()

    # ---- Edge cases: partial field combinations ----

    @pytest.mark.asyncio
    async def test_update_only_username_leaves_other_fields_unchanged(self, service, repo, mock_user):
        """Sending only username should not touch full_name or password_hash."""
        original_name = mock_user.full_name
        original_hash = mock_user.password_hash
        dto = UserUpdate(username="new_user")
        repo.get_by_username.return_value = None
        repo.update.return_value = mock_user

        await service.update_user(mock_user, dto)

        assert mock_user.username == "new_user"
        assert mock_user.full_name == original_name
        assert mock_user.password_hash == original_hash

    @pytest.mark.asyncio
    async def test_update_only_password_leaves_other_fields_unchanged(self, service, repo, mock_user):
        """Sending only password fields should not touch full_name or username."""
        original_name = mock_user.full_name
        original_username = mock_user.username
        dto = UserUpdate(current_password="OldPass123!", new_password="NewPass123!")
        repo.update.return_value = mock_user

        with patch("app.modules.users.service.verify_password", return_value=True), \
             patch("app.modules.users.service.hash_password", return_value="hashed_new"):
            await service.update_user(mock_user, dto)

        assert mock_user.full_name == original_name
        assert mock_user.username == original_username
        assert mock_user.password_hash == "hashed_new"

    @pytest.mark.asyncio
    async def test_update_full_name_and_username_together(self, service, repo, mock_user):
        """Update both full_name and username in one request."""
        dto = UserUpdate(full_name="New Name", username="new_user")
        repo.get_by_username.return_value = None
        repo.update.return_value = mock_user

        await service.update_user(mock_user, dto)

        assert mock_user.full_name == "New Name"
        assert mock_user.username == "new_user"
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_full_name_and_password_together(self, service, repo, mock_user):
        """Update full_name and change password in one request."""
        dto = UserUpdate(full_name="New Name", current_password="OldPass123!", new_password="NewPass123!")
        repo.update.return_value = mock_user

        with patch("app.modules.users.service.verify_password", return_value=True), \
             patch("app.modules.users.service.hash_password", return_value="hashed_new"):
            await service.update_user(mock_user, dto)

        assert mock_user.full_name == "New Name"
        assert mock_user.password_hash == "hashed_new"

    @pytest.mark.asyncio
    async def test_update_all_fields_at_once(self, service, repo, mock_user):
        """Update full_name, username, and password all in one request."""
        dto = UserUpdate(
            full_name="New Name",
            username="new_user",
            current_password="OldPass123!",
            new_password="NewPass123!"
        )
        repo.get_by_username.return_value = None
        repo.update.return_value = mock_user

        with patch("app.modules.users.service.verify_password", return_value=True), \
             patch("app.modules.users.service.hash_password", return_value="hashed_new"):
            await service.update_user(mock_user, dto)

        assert mock_user.full_name == "New Name"
        assert mock_user.username == "new_user"
        assert mock_user.password_hash == "hashed_new"
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_current_password_without_new_password_is_ignored(self, service, repo, mock_user):
        """Sending current_password alone does nothing — password block skipped."""
        original_hash = mock_user.password_hash
        dto = UserUpdate(current_password="OldPass123!")
        repo.update.return_value = mock_user

        await service.update_user(mock_user, dto)

        assert mock_user.password_hash == original_hash
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_username_does_not_update_anything(self, service, repo, mock_user):
        """If username is duplicate, full_name should NOT be updated either (error raised before commit)."""
        dto = UserUpdate(full_name="New Name", username="taken_username")
        other_user = MagicMock(spec=User)
        other_user.id = uuid4()
        repo.get_by_username.return_value = other_user

        with pytest.raises(DuplicateUsernameError):
            await service.update_user(mock_user, dto)

        # full_name was set before the username check, but repo.update was never called
        repo.update.assert_not_called()


class TestUserServiceEnsureOAuth:

    @pytest.fixture
    def repo(self):
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def service(self, repo):
        svc = UserService.__new__(UserService)
        svc.repository = repo
        return svc

    @pytest.mark.asyncio
    async def test_ensure_oauth_existing_user(self, service, repo):
        existing = MagicMock(spec=User)
        repo.get_by_email.return_value = existing

        result = await service.ensure_user_for_oauth(email="test@example.com", full_name="Test")

        assert result == existing
        repo.create_oauth_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_oauth_new_user(self, service, repo):
        repo.get_by_email.return_value = None
        repo.get_by_username.return_value = None  # For generate_username
        new_user = MagicMock(spec=User)
        repo.create_oauth_user.return_value = new_user

        result = await service.ensure_user_for_oauth(email="new@example.com", full_name="New User")

        assert result == new_user
        repo.create_oauth_user.assert_called_once()
