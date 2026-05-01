import pytest
from pydantic import ValidationError

from app.modules.users.schemas import UserCreate, UserRead, UserUpdate


class TestUserCreate:

    def test_valid_user_create(self):
        dto = UserCreate(email="test@example.com", password="StrongPass1!", full_name="Test User")

        assert dto.email == "test@example.com"
        assert dto.password == "StrongPass1!"
        assert dto.full_name == "Test User"

    def test_user_create_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate(password="StrongPass1!")

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="StrongPass1!")

    def test_user_create_missing_password(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com")

    def test_user_create_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="short")

    def test_user_create_password_too_long(self):
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="a" * 129)


class TestUserUpdate:

    def test_update_all_fields(self):
        dto = UserUpdate(
            full_name="New Name",
            username="new_user",
            current_password="OldPass123!",
            new_password="NewPass123!"
        )

        assert dto.full_name == "New Name"
        assert dto.username == "new_user"
        assert dto.current_password == "OldPass123!"
        assert dto.new_password == "NewPass123!"

    def test_update_partial_fields(self):
        dto = UserUpdate(full_name="New Name")

        assert dto.full_name == "New Name"
        assert dto.username is None
        assert dto.current_password is None
        assert dto.new_password is None

    def test_update_empty(self):
        dto = UserUpdate()

        assert dto.full_name is None
        assert dto.username is None
        assert dto.current_password is None
        assert dto.new_password is None

    def test_update_username_too_short(self):
        with pytest.raises(ValidationError):
            UserUpdate(username="ab")

    def test_update_username_too_long(self):
        with pytest.raises(ValidationError):
            UserUpdate(username="a" * 31)

    def test_update_username_min_length(self):
        dto = UserUpdate(username="abc")
        assert dto.username == "abc"

    def test_update_username_max_length(self):
        dto = UserUpdate(username="a" * 30)
        assert dto.username == "a" * 30

    def test_update_new_password_too_short(self):
        with pytest.raises(ValidationError):
            UserUpdate(new_password="short")

    def test_update_new_password_too_long(self):
        with pytest.raises(ValidationError):
            UserUpdate(new_password="a" * 129)

    def test_update_current_password_too_short(self):
        with pytest.raises(ValidationError):
            UserUpdate(current_password="short")

    # ---- Edge cases: partial field combinations ----

    def test_update_username_only(self):
        dto = UserUpdate(username="just_user")

        assert dto.username == "just_user"
        assert dto.full_name is None
        assert dto.current_password is None
        assert dto.new_password is None

    def test_update_password_fields_only(self):
        dto = UserUpdate(current_password="OldPass123!", new_password="NewPass123!")

        assert dto.current_password == "OldPass123!"
        assert dto.new_password == "NewPass123!"
        assert dto.full_name is None
        assert dto.username is None

    def test_update_current_password_without_new(self):
        """Pydantic should allow this — service handles the logic."""
        dto = UserUpdate(current_password="OldPass123!")

        assert dto.current_password == "OldPass123!"
        assert dto.new_password is None

    def test_update_new_password_without_current(self):
        """Pydantic should allow this — service raises the error."""
        dto = UserUpdate(new_password="NewPass123!")

        assert dto.new_password == "NewPass123!"
        assert dto.current_password is None

    def test_update_password_with_username(self):
        dto = UserUpdate(
            username="new_user",
            current_password="OldPass123!",
            new_password="NewPass123!"
        )

        assert dto.username == "new_user"
        assert dto.current_password == "OldPass123!"
        assert dto.new_password == "NewPass123!"

    def test_update_password_exact_min_length(self):
        dto = UserUpdate(new_password="a" * 8)
        assert dto.new_password == "a" * 8

    def test_update_password_exact_max_length(self):
        dto = UserUpdate(new_password="a" * 128)
        assert dto.new_password == "a" * 128


class TestUserRead:

    def test_user_read_valid(self):
        from uuid import uuid4
        from datetime import datetime, timezone

        user_id = uuid4()
        now = datetime.now(timezone.utc)

        dto = UserRead(
            id=user_id,
            email="test@example.com",
            full_name="Test User",
            username="test_user123",
            is_active=True,
            created_at=now,
            updated_at=now
        )

        assert dto.id == user_id
        assert dto.email == "test@example.com"
        assert dto.username == "test_user123"
        assert dto.is_active is True

    def test_user_read_missing_required_fields(self):
        with pytest.raises(ValidationError):
            UserRead(email="test@example.com")
