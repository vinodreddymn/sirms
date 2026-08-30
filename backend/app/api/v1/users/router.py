from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, pagination_params, PaginationParams
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.security import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from fastapi import Body, HTTPException
from uuid import UUID as UUIDType

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("", response_model=UserRead)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    service = UserService(db)
    user = await service.create_user(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        password=payload.password,
    )
    return UserRead.from_orm(user)


@router.get("", response_model=PaginatedResponse[UserRead])
async def list_users(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[UserRead]:
    service = UserService(db)
    users, total = await service.list_users(offset=params.offset, limit=params.page_size)
    result_items = []
    for user in users:
        u = UserRead.from_orm(user)
        # attach role ids and codes
        u.role_codes = await service.user_repo.get_role_codes(user.id)
        u.role_ids = await service.user_repo.get_role_ids(user.id)
        result_items.append(u)
    return PaginatedResponse.create(result_items, total, params)


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    service = UserService(db)
    u = UserRead.from_orm(current_user)
    u.role_codes = await service.user_repo.get_role_codes(current_user.id)
    u.role_ids = await service.user_repo.get_role_ids(current_user.id)
    return u


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserRead:
    service = UserService(db)
    user = await service.get_user(user_id)
    u = UserRead.from_orm(user)
    u.role_codes = await service.user_repo.get_role_codes(user.id)
    u.role_ids = await service.user_repo.get_role_ids(user.id)
    return u


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> UserRead:
    service = UserService(db)
    user = await service.update_user(user_id, **payload.model_dump(exclude_unset=True))
    u = UserRead.from_orm(user)
    u.role_codes = await service.user_repo.get_role_codes(user.id)
    u.role_ids = await service.user_repo.get_role_ids(user.id)
    return u


@router.post("/{user_id}/roles")
async def assign_role_to_user(user_id: UUID, payload: dict = Body(...), db: AsyncSession = Depends(get_db), current_user=Depends(get_current_active_user)) -> dict:
    # only admins may assign roles
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Permission denied")
    role_id = payload.get("role_id")
    if not role_id:
        raise HTTPException(status_code=400, detail="role_id is required")
    service = UserService(db)
    await service.assign_role(user_id, UUIDType(role_id))
    return {"status": "ok"}


@router.delete("/{user_id}/roles/{role_id}")
async def remove_role_from_user(user_id: UUID, role_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_active_user)) -> dict:
    # only admins may remove roles
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Permission denied")
    service = UserService(db)
    await service.remove_role(user_id, role_id)
    return {"status": "ok"}


@router.delete("/{user_id}")
async def deactivate_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await UserService(db).update_user(user_id, is_locked=True)
    return {"status": "deactivated"}
