from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, pagination_params, PaginationParams
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.security import RoleCreate, RoleRead, RoleUpdate
from app.services.security_service import SecurityService

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
    dependencies=[Depends(get_current_active_user)],
)

@router.get("", response_model=PaginatedResponse[RoleRead])
async def list_roles(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[RoleRead]:
    service = SecurityService(db)
    roles, total = await service.list_roles(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([RoleRead.model_validate(role) for role in roles], total, params)

@router.post("", response_model=RoleRead)
async def create_role(payload: RoleCreate, db: AsyncSession = Depends(get_db)) -> RoleRead:
    service = SecurityService(db)
    role = await service.create_role(payload.model_dump())
    return RoleRead.model_validate(role)

@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: UUID, db: AsyncSession = Depends(get_db)) -> RoleRead:
    service = SecurityService(db)
    role = await service.get_role(role_id)
    return RoleRead.model_validate(role)

@router.put("/{role_id}", response_model=RoleRead)
async def update_role(role_id: UUID, payload: RoleUpdate, db: AsyncSession = Depends(get_db)) -> RoleRead:
    service = SecurityService(db)
    role = await service.update_role(role_id, payload.model_dump(exclude_unset=True))
    return RoleRead.model_validate(role)
