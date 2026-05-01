from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password

from .exceptions import DuplicateUsernameError, InvalidPasswordError
from .models import User, UserRole
from .repository import UserRepository
from .schemas import UserCreate, UserUpdate

class UserService:
    """Business logic for user management."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

    async def create_user(self, user_create: UserCreate) -> User:
        password_hash = hash_password(user_create.password)
        username = await self.generate_username(full_name=user_create.full_name)
        return await self.repository.create(user_create, password_hash, username)

    async def generate_username(self, full_name: str | None = None, max_retries: int = 5) -> str:
        """Generate a unique username based on full name and random 6 characters."""
        if full_name and full_name.strip():
            base = full_name.strip().lower().replace(" ", "_")
        else:
            base = "user_"

        for _ in range(max_retries):
            username = base + uuid4().hex[:6]
            existing = await self.repository.get_by_username(username)
            if existing is None:
                return username
        raise DuplicateUsernameError("Failed to generate a unique username")

    async def update_user(self, user: User, user_update: UserUpdate) -> User:
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.username is not None:
            existing_username = await self.repository.get_by_username(user_update.username)
            if existing_username and existing_username.id != user.id:
                raise DuplicateUsernameError("Username already exists")
            user.username = user_update.username
        if user_update.new_password is not None:
            if user_update.current_password is None:
                raise InvalidPasswordError("Current password is required")
            if user.password_hash is None:
                raise InvalidPasswordError("Password authentication is not required for OAuth")
            if not verify_password(user_update.current_password, user.password_hash):
                raise InvalidPasswordError("Current password is incorrect")
            user.password_hash = hash_password(user_update.new_password)
        return await self.repository.update(user)

    async def ensure_user_for_oauth(
        self,
        email: str,
        full_name: str | None,
        role: UserRole = UserRole.EMPLOYEE,
    ) -> User:
        existing = await self.repository.get_by_email(email)
        if existing:
            return existing
        username = await self.generate_username(full_name=full_name)
        return await self.repository.create_oauth_user(email=email, full_name=full_name, username=username, role=role)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.repository.get_by_id(user_id)
