from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.security import (
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_with_roles_and_permissions(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_role_codes(self, user_id: UUID) -> list[str]:
        result = await self.session.execute(
            select(Role.role_code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def get_role_ids(self, user_id: UUID) -> list[UUID]:
        result = await self.session.execute(
            select(Role.id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def get_effective_permissions(self, user_id: UUID) -> list[str]:
        result = await self.session.execute(
            select(Permission.permission_code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def has_permission(self, user_id: UUID, permission_code: str) -> bool:
        result = await self.session.execute(
            select(Permission.id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Permission.permission_code == permission_code)
        )
        return result.scalars().first() is not None

    async def list(self, offset: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.execute(select(User).offset(offset).limit(limit))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def update_password_hash(self, user: User, password_hash: str) -> None:
        user.password_hash = password_hash
        await self.session.flush()

    async def update_last_login(self, user: User) -> None:
        user.last_login_at = __import__("datetime").datetime.utcnow()
        await self.session.flush()


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_active_by_user_and_token(self, user_id: UUID, refresh_token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        )
        for token in result.scalars().all():
            if verify_password(refresh_token, token.token_hash):
                return token
        return None

    async def revoke(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.utcnow()
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        )
        for token in result.scalars().all():
            token.revoked_at = datetime.utcnow()
        await self.session.flush()

class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, role_id: UUID) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def get_by_code(self, role_code: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.role_code == role_code))
        return result.scalars().first()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Role]:
        result = await self.session.execute(select(Role).order_by(Role.role_name).offset(offset).limit(limit))
        return result.scalars().all()
        
    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Role))
        return result.scalar_one()

    async def create(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        return role

class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def list(self) -> list[Permission]:
        result = await self.session.execute(select(Permission).order_by(Permission.module_name, Permission.permission_name))
        return result.scalars().all()

class LoginHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, history) -> None:
        self.session.add(history)
        await self.session.flush()
    async def list_with_users(self, offset: int = 0, limit: int = 100):
        from app.models.security import LoginHistory, User
        stmt = (
            select(LoginHistory, User.username)
            .outerjoin(User, User.id == LoginHistory.user_id)
            .order_by(LoginHistory.login_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def count(self) -> int:
        from app.models.security import LoginHistory
        result = await self.session.execute(select(func.count()).select_from(LoginHistory))
        return result.scalar_one()
