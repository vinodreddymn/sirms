from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.security import User
from app.repositories.security import UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise UnauthorizedException("Missing or invalid authorization header")
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    if not user:
        raise UnauthorizedException("User not found")
    setattr(user, "is_admin", bool(payload.get("is_admin")))
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.is_locked or not getattr(current_user, "is_active", True):
        raise ForbiddenException("User account is not active")
    return current_user


def require_permission(permission_code: str) -> Callable:
    async def permission_dependency(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        user_repo = UserRepository(db)
        if not await user_repo.has_permission(current_user.id, permission_code):
            raise ForbiddenException("Permission denied")
        return current_user

    return permission_dependency


def require_any_permission(*permission_codes: str) -> Callable:
    async def permission_dependency(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        user_repo = UserRepository(db)
        for code in permission_codes:
            if await user_repo.has_permission(current_user.id, code):
                return current_user
        raise ForbiddenException("Permission denied")

    return permission_dependency


def require_all_permissions(*permission_codes: str) -> Callable:
    async def permission_dependency(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        user_repo = UserRepository(db)
        for code in permission_codes:
            if not await user_repo.has_permission(current_user.id, code):
                raise ForbiddenException("Permission denied")
        return current_user

    return permission_dependency


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not credentials:
        return None
    return await get_current_user(credentials, db)
