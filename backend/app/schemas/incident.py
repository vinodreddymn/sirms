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

    description: str | None = None

    resolution_remarks: str | None = None

class IncidentRead(IncidentBase):
    id: UUID
    incident_number: str

    reported_at: datetime
    created_at: datetime
    updated_at: datetime | None = None
    closed_date: datetime | None = None
    closed_by: UUID | None = None
    resolution_remarks: str | None = None

# =============================================================================
# INCIDENT ASSET ACTIONS
# =============================================================================
# Supported actions: CHANGE_STATUS | MOVE | SEND_FOR_REPAIR | RETURN_FROM_REPAIR

class IncidentAssetAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID

    action: str
    reason: str

    status_id: int | None = None
    location_id: UUID | None = None

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
