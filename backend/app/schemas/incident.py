from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# =============================================================================
# INCIDENTS
# =============================================================================

class IncidentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    work_type_id: UUID | None = None
    asset_id: UUID | None = None
    location_id: UUID | None = None

    status_id: int
    priority_id: int
    category_id: int | None = None

    reported_by: UUID | None = None
    assigned_to_id: UUID | None = None

    target_start_date: datetime | None = None
    target_completion_date: datetime | None = None
    actual_start_date: datetime | None = None
    actual_completion_date: datetime | None = None

    estimated_cost: float | None = None
    actual_cost: float | None = None

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
    work_type_id: UUID | None = None
    asset_id: UUID | None = None
    location_id: UUID | None = None

    status_id: int | None = None
    priority_id: int | None = None
    category_id: int | None = None

    assigned_to_id: UUID | None = None
    target_start_date: datetime | None = None
    target_completion_date: datetime | None = None
    actual_start_date: datetime | None = None
    actual_completion_date: datetime | None = None
    estimated_cost: float | None = None
    actual_cost: float | None = None

    description: str | None = None

    completion_notes: str | None = None

class IncidentRead(IncidentBase):
    id: UUID
    work_request_number: str

    reported_at: datetime
    created_at: datetime
    updated_at: datetime | None = None
    closed_date: datetime | None = None
    closed_by: UUID | None = None
    completion_notes: str | None = None

# =============================================================================
# INCIDENT ASSET ACTIONS
# =============================================================================
# Supported actions: CHANGE_STATUS | MOVE | INSTALL | UNINSTALL | SEND_FOR_REPAIR | RETURN_FROM_REPAIR

class IncidentAssetAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID

    action: str
    reason: str

    status_id: int | None = None
    location_id: UUID | None = None
    location_position_id: UUID | None = None  # Required for INSTALL action

    # Fields used by RETURN_FROM_REPAIR
    courier_number: str | None = None
    repair_remarks: str | None = None


# =============================================================================
# INCIDENT UPDATES
# =============================================================================

class IncidentUpdateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID

    status_after_update_id: int | None = None
    updated_by: UUID | None = None

    update_notes: str = Field(..., min_length=1)
    time_spent_minutes: int | None = Field(None, ge=0)


class IncidentUpdateCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID | None = None  # set from URL path in the service layer
    status_after_update_id: int | None = None
    updated_by: UUID | None = None
    update_notes: str = Field(..., min_length=1)
    time_spent_minutes: int | None = Field(None, ge=0)


class IncidentUpdateRead(IncidentUpdateBase):
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


# =============================================================================
# WORK ASSIGNMENTS
# =============================================================================

class WorkAssignmentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID
    assignment_type: str
    assigned_to: UUID
    assigned_by: UUID | None = None
    assigned_date: datetime | None = None
    accepted_date: datetime | None = None
    started_date: datetime | None = None
    completed_date: datetime | None = None
    cancelled_date: datetime | None = None
    assignment_status: str
    remarks: str | None = None


class WorkAssignmentCreate(WorkAssignmentBase):
    pass


class WorkAssignmentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assignment_type: str | None = None
    assigned_to: UUID | None = None
    assigned_by: UUID | None = None
    accepted_date: datetime | None = None
    started_date: datetime | None = None
    completed_date: datetime | None = None
    cancelled_date: datetime | None = None
    assignment_status: str | None = None
    remarks: str | None = None


class WorkAssignmentRead(WorkAssignmentBase):
    id: UUID


# =============================================================================
# WORK ACTIONS
# =============================================================================

class WorkActionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID
    asset_id: UUID | None = None
    action_type: str
    user_id: UUID
    timestamp: datetime | None = None
    reference_type: str | None = None
    reference_id: UUID | None = None


class WorkActionCreate(WorkActionBase):
    pass


class WorkActionRead(WorkActionBase):
    id: UUID


# =============================================================================
# WORK RELATIONS
# =============================================================================

class WorkRelationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_incident_id: UUID
    target_incident_id: UUID
    relation_type: str


class WorkRelationCreate(WorkRelationBase):
    pass


class WorkRelationRead(WorkRelationBase):
    id: UUID
