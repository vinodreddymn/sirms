from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "security"}

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    mobile_number: Mapped[str | None] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    default_project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))


class Role(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "security"}

    role_template_id: Mapped[int | None] = mapped_column(ForeignKey("master.user_role_templates.id", ondelete="SET NULL", onupdate="RESTRICT"))
    role_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    is_system_role: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))


class Permission(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "security"}

    permission_code: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    permission_name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions"),
        {"schema": "security"},
    )

    role_id: Mapped[UUID] = mapped_column(ForeignKey("security.roles.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("security.permissions.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)


class UserRole(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "project_id", name="uq_security_user_roles"),
        {"schema": "security"},
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("security.roles.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    assigned_from: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE"))
    assigned_to: Mapped[date | None] = mapped_column(Date)


class LoginHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "login_history"
    __table_args__ = {"schema": "security"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    login_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    logout_at: Mapped[datetime | None] = mapped_column(DateTime)
    login_status: Mapped[str] = mapped_column(String(20), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64))
    device_info: Mapped[str | None] = mapped_column(String(255))
    remarks: Mapped[str | None] = mapped_column(Text)


class PasswordResetToken(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"schema": "security"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime)


class RefreshToken(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "security"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    device_info: Mapped[str | None] = mapped_column(String(255))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class ApiToken(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "api_tokens"
    __table_args__ = (
        UniqueConstraint("user_id", "token_name", name="uq_api_token_name"),
        {"schema": "security"},
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    token_name: Mapped[str] = mapped_column(String(100), nullable=False)
    token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    scope_json: Mapped[dict | None] = mapped_column(JSONB)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
