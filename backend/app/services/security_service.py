from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.models.security import Role
from app.repositories.security import RoleRepository, PermissionRepository, LoginHistoryRepository

class SecurityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.role_repo = RoleRepository(session)
        self.permission_repo = PermissionRepository(session)
        self.login_history_repo = LoginHistoryRepository(session)

    # --- Roles ---
    async def list_roles(self, offset: int = 0, limit: int = 100) -> tuple[list[Role], int]:
        roles = await self.role_repo.list(offset=offset, limit=limit)
        total = await self.role_repo.count()
        return roles, total

    async def get_role(self, role_id: UUID) -> Role:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Role not found")
        return role

    async def create_role(self, data: dict) -> Role:
        if await self.role_repo.get_by_code(data["role_code"]):
            raise ConflictException("Role code already exists")
        role = Role(**data)
        return await self.role_repo.create(role)

    async def update_role(self, role_id: UUID, data: dict) -> Role:
        role = await self.get_role(role_id)
        for field, value in data.items():
            if value is not None and hasattr(role, field):
                setattr(role, field, value)
        await self.session.flush()
        return role

    # --- Permissions ---
    async def list_permissions(self):
        return await self.permission_repo.list()

    # --- Login History ---
    async def list_login_history(self, offset: int = 0, limit: int = 100):
        items = await self.login_history_repo.list_with_users(offset=offset, limit=limit)
        total = await self.login_history_repo.count()
        return items, total
