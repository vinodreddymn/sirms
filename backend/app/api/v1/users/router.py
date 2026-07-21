from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, pagination_params, PaginationParams
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.security import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

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
    return PaginatedResponse.create([UserRead.from_orm(user) for user in users], total, params)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await UserService(db).get_user(user_id)
    return UserRead.from_orm(user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db)) -> UserRead:
    user = await UserService(db).update_user(user_id, **payload.model_dump(exclude_unset=True))
    return UserRead.from_orm(user)


@router.delete("/{user_id}")
async def deactivate_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await UserService(db).update_user(user_id, is_locked=True)
    return {"status": "deactivated"}
