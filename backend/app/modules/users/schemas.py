from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict

from .models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.EMPLOYEE)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    id: UUID
    username: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    current_password: Optional[str] = Field(default=None, min_length=8, max_length=128)
    new_password: Optional[str] = Field(default=None, min_length=8, max_length=128)
