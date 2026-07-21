from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str
    email: EmailStr
    mobile_number: str | None = None
    default_project_id: UUID | None = None
    is_locked: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    mobile_number: str | None = None
    default_project_id: UUID | None = None
    is_locked: bool | None = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class RoleRead(BaseModel):
    id: UUID
    role_code: str
    role_name: str
    description: str | None = None
    is_system_role: bool


class PermissionRead(BaseModel):
    id: UUID
    permission_code: str
    permission_name: str
    module_name: str
    description: str | None = None
