from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# =============================================================================
# INCIDENTS
# =============================================================================

class IncidentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    asset_id: UUID | None = None
    location_id: UUID | None = None

    incident_status_id: int
    incident_priority_id: int
    incident_category_id: int | None = None

    reported_by: UUID | None = None
    assigned_to: UUID | None = None

    description: str = Field(..., min_length=1)


class IncidentCreate(IncidentBase):
    @model_validator(mode="after")
    def require_affected_asset_or_location(self) -> "IncidentCreate":
        if not self.asset_id and not self.location_id:
            raise ValueError("An affected asset or location position is required")
        return self


class IncidentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID | None = None
    asset_id: UUID | None = None
    location_id: UUID | None = None

    incident_status_id: int | None = None
    incident_priority_id: int | None = None
    incident_category_id: int | None = None

    assigned_to: UUID | None = None
    description: str | None = None


class IncidentRead(IncidentBase):
    id: UUID
    incident_number: str

    reported_at: datetime
    created_at: datetime
    updated_at: datetime | None = None


# =============================================================================
# INCIDENT ASSET ACTIONS
# =============================================================================

class IncidentAssetAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID

    action: str
    reason: str

    status_id: int | None = None
    location_id: UUID | None = None


# =============================================================================
# INCIDENT UPDATES
# =============================================================================

class IncidentUpdateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID

    status_after_update_id: int | None = None
    updated_by: UUID | None = None

    update_notes: str = Field(..., min_length=1)


class IncidentUpdateCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID | None = None  # set from URL path in the service layer
    status_after_update_id: int | None = None
    updated_by: UUID | None = None
    update_notes: str = Field(..., min_length=1)


class IncidentUpdateRead(IncidentUpdateBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None = None


# =============================================================================
# WORK ORDERS
# =============================================================================

class WorkOrderBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID | None = None

    assigned_to: UUID | None = None

    status_id: int | None = None

    planned_start_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None

    remarks: str | None = None


class WorkOrderCreate(WorkOrderBase):
    pass


class WorkOrderUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID | None = None
    assigned_to: UUID | None = None

    status_id: int | None = None

    planned_start_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None

    remarks: str | None = None


class WorkOrderRead(WorkOrderBase):
    id: UUID

    work_order_number: str

    created_at: datetime
    updated_at: datetime | None = None


# =============================================================================
# WORK ORDER TASKS
# =============================================================================

class WorkOrderTaskBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    work_order_id: UUID

    description: str = Field(..., min_length=1)

    task_sequence: int = 0

    assigned_to: UUID | None = None

    due_date: date | None = None

    completed: bool = False


class WorkOrderTaskCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str = Field(..., min_length=1)

    task_sequence: int = 0

    assigned_to: UUID | None = None

    due_date: date | None = None


class WorkOrderTaskUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str | None = None

    task_sequence: int | None = None

    assigned_to: UUID | None = None

    due_date: date | None = None

    completed: bool | None = None


class WorkOrderTaskRead(WorkOrderTaskBase):
    id: UUID

    created_at: datetime
    updated_at: datetime | None = None


# =============================================================================
# INCIDENT ATTACHMENTS
# =============================================================================

class IncidentAttachmentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attachment_id: UUID

    category: str | None = None


class IncidentAttachmentRead(IncidentAttachmentCreate):
    id: UUID

    incident_id: UUID

    created_at: datetime
    updated_at: datetime | None = None
