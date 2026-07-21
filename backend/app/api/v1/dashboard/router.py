from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.asset import Asset, MaintenanceSchedule
from app.models.common import DashboardPreference
from app.models.incident import Incident, WorkOrder
from app.models.security import User
from app.schemas.dashboard import DashboardPreferenceRead, DashboardPreferenceUpdate, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)) -> DashboardSummary:
    total_assets = await db.scalar(select(func.count()).select_from(Asset))
    active_incidents = await db.scalar(
        select(func.count()).select_from(Incident).where(Incident.is_active.is_(True))
    )
    overdue_maintenance = await db.scalar(
        select(func.count()).select_from(MaintenanceSchedule).where(
            MaintenanceSchedule.is_active.is_(True),
            MaintenanceSchedule.next_due_date < func.current_date(),
        )
    )
    pending_work_orders = await db.scalar(
        select(func.count()).select_from(WorkOrder).where(WorkOrder.actual_end_date.is_(None))
    )
    return DashboardSummary(
        total_assets=total_assets or 0,
        active_incidents=active_incidents or 0,
        overdue_maintenance=overdue_maintenance or 0,
        pending_work_orders=pending_work_orders or 0,
    )


@router.get("/preferences", response_model=DashboardPreferenceRead)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardPreferenceRead:
    preference = await _get_or_create_dashboard_preference(db, current_user.id)
    return _preference_to_schema(preference)


@router.put("/preferences", response_model=DashboardPreferenceRead)
async def update_preferences(
    payload: DashboardPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardPreferenceRead:
    preference = await _get_or_create_dashboard_preference(db, current_user.id)
    preference.preference_json = {
        **(preference.preference_json or {}),
        **payload.model_dump(exclude_unset=True),
    }
    await db.flush()
    return _preference_to_schema(preference)


async def _get_or_create_dashboard_preference(
    db: AsyncSession,
    user_id,
) -> DashboardPreference:
    result = await db.execute(
        select(DashboardPreference).where(
            DashboardPreference.user_id == user_id,
            DashboardPreference.preference_name == "default",
        )
    )
    preference = result.scalars().first()
    if preference:
        return preference
    preference = DashboardPreference(
        user_id=user_id,
        preference_name="default",
        preference_json={},
    )
    db.add(preference)
    await db.flush()
    return preference


def _preference_to_schema(preference: DashboardPreference) -> DashboardPreferenceRead:
    values = preference.preference_json or {}
    return DashboardPreferenceRead(
        id=preference.id,
        user_id=preference.user_id,
        layout=values.get("layout"),
        theme=values.get("theme"),
        refresh_interval=values.get("refresh_interval"),
        created_at=preference.created_at,
        updated_at=preference.updated_at,
    )
