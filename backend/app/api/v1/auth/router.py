from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.security import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    service = AuthService(db)
    user = await service.authenticate(payload.username, payload.password, request)
    return await service.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    service = AuthService(db)
    return await service.refresh_tokens(payload.refresh_token)


@router.post("/logout")
async def logout(payload: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    service = AuthService(db)
    await service.logout(payload.refresh_token)
    return {"status": "logged_out"}


@router.post("/logout/all")
async def logout_all(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    service = AuthService(db)
    await service.logout_all(current_user)
    return {"status": "logged_out_all"}


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    service = AuthService(db)
    await service.change_password(current_user, payload.old_password, payload.new_password)
    return {"status": "password_changed"}


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.from_orm(current_user)
