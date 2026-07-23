from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.security import PermissionRead
from app.services.security_service import SecurityService

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    dependencies=[Depends(get_current_active_user)],
)

@router.get("", response_model=list[PermissionRead])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
) -> list[PermissionRead]:
    service = SecurityService(db)
    permissions = await service.list_permissions()
    return [PermissionRead.model_validate(p) for p in permissions]
