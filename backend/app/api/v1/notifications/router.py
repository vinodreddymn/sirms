from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.common import Notification, NotificationPreference
from app.models.security import User
from app.schemas.notifications import NotificationPreferenceRead, NotificationPreferenceUpdate, NotificationRead

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PaginatedResponse[NotificationRead])
async def list_notifications(
    params: PaginationParams = Depends(pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[NotificationRead]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset(params.offset)
        .limit(params.page_size)
    )
    total = await db.scalar(
        select(func.count()).select_from(Notification).where(Notification.user_id == current_user.id)
    )
    items = [_notification_to_schema(item) for item in result.scalars().all()]
    return PaginatedResponse.create(items, total or 0, params)


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    unread_count = await db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id, Notification.read_at.is_(None))
    )
    return {"unread_count": unread_count or 0}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationRead:
    notification = await db.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        from app.core.exceptions import NotFoundException

        raise NotFoundException("Notification not found")
    notification.read_at = func.now()
    await db.flush()
    await db.refresh(notification)
    return _notification_to_schema(notification)


@router.get("/preferences", response_model=NotificationPreferenceRead)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceRead:
    preference = await _get_or_create_notification_preference(db, current_user.id)
    return NotificationPreferenceRead.model_validate(preference)


@router.put("/preferences", response_model=NotificationPreferenceRead)
async def update_preferences(
    payload: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationPreferenceRead:
    preference = await _get_or_create_notification_preference(db, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(preference, field):
            setattr(preference, field, value)
    await db.flush()
    return NotificationPreferenceRead.model_validate(preference)


async def _get_or_create_notification_preference(
    db: AsyncSession,
    user_id: UUID,
) -> NotificationPreference:
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    preference = result.scalars().first()
    if preference:
        return preference
    preference = NotificationPreference(user_id=user_id)
    db.add(preference)
    await db.flush()
    return preference


def _notification_to_schema(notification: Notification) -> NotificationRead:
    return NotificationRead(
        id=notification.id,
        user_id=notification.user_id,
        title=notification.notification_title,
        message=notification.notification_body,
        notification_type=notification.channel_type,
        related_entity_id=notification.entity_id,
        is_read=notification.read_at is not None,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )
