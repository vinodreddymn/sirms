from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, pagination_params, PaginationParams
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.security import LoginHistoryRead
from app.services.security_service import SecurityService

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"],
    dependencies=[Depends(get_current_active_user)],
)

@router.get("/login-history", response_model=PaginatedResponse[LoginHistoryRead])
async def list_login_history(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LoginHistoryRead]:
    service = SecurityService(db)
    rows, total = await service.list_login_history(offset=params.offset, limit=params.page_size)
    
    items = []
    for row in rows:
        history, username = row
        data = {
            "id": history.id,
            "user_id": history.user_id,
            "username": username,
            "login_at": history.login_at,
            "logout_at": history.logout_at,
            "login_status": history.login_status,
            "ip_address": history.ip_address,
            "device_info": history.device_info,
            "remarks": history.remarks,
        }
        items.append(LoginHistoryRead.model_validate(data))

    return PaginatedResponse.create(items, total, params)
