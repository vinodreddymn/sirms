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


class RoleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_code: str
    role_name: str
    description: str | None = None
    is_system_role: bool = False
    role_template_id: int | None = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    role_name: str | None = None
    description: str | None = None

class RoleRead(RoleBase):
    id: UUID


class PermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    permission_code: str
    permission_name: str
    module_name: str
    description: str | None = None

class LoginHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    username: str | None = None
    login_at: datetime
    logout_at: datetime | None = None
    login_status: str
    ip_address: str | None = None
    device_info: str | None = None
    remarks: str | None = None
