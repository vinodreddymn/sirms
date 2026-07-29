from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_assets: int = 0
    active_incidents: int = 0
    overdue_maintenance: int = 0


class ChartDataPoint(BaseModel):
    label: str
    value: int


class ChartData(BaseModel):
    title: str
    data: list[ChartDataPoint]


class DashboardPreferenceUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    layout: str | None = None
    theme: str | None = None
    refresh_interval: int | None = None


class DashboardPreferenceRead(DashboardPreferenceUpdate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime | None = None
