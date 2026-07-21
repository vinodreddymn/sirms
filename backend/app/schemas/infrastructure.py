from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LocationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    parent_location_id: UUID | None = None
    location_template_node_id: int | None = None
    location_type_id: int
    code: str
    name: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    elevation_meters: Decimal | None = None
    geo_json: dict[str, Any] | None = None
    remarks: str | None = None


class LocationCreate(LocationBase):
    # Optional: auto-create positions from this template after location creation
    position_template_id: int | None = None


class LocationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID | None = None
    parent_location_id: UUID | None = None
    location_template_node_id: int | None = None
    location_type_id: int | None = None
    code: str | None = None
    name: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    elevation_meters: Decimal | None = None
    geo_json: dict[str, Any] | None = None
    remarks: str | None = None


class LocationRead(LocationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class LocationSearchRead(BaseModel):
    id: UUID
    code: str
    name: str
    location_type_name: str
    hierarchy_path: str


class LocationPositionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: UUID
    position_template_node_id: int | None = None
    position_type_id: int
    position_number: str
    maximum_capacity: int = Field(default=1, ge=0)
    remarks: str | None = None


class LocationPositionCreate(LocationPositionBase):
    pass


class LocationPositionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: UUID | None = None
    position_template_node_id: int | None = None
    position_type_id: int | None = None
    position_number: str | None = None
    maximum_capacity: int | None = Field(default=None, ge=0)
    remarks: str | None = None


class LocationPositionRead(LocationPositionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class LocationTreeNode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    location_type_id: int
    location_type_name: str
    parent_location_id: UUID | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    remarks: str | None = None
    children: list["LocationTreeNode"] = []

LocationTreeNode.model_rebuild()


class PositionPreviewItem(BaseModel):
    """Lightweight preview of a position that would be created from a template."""
    position_type_id: int
    position_type_name: str
    position_number: str
    maximum_capacity: int
    node_order: int
    remarks: str | None = None
