from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LookupBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str | None = None
    display_order: int | None = Field(default=0, ge=0)
    is_active: bool | None = True


class LookupCreate(LookupBase):
    pass


class LookupUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None = None
    name: str | None = None
    description: str | None = None
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class LookupRead(LookupBase):
    id: int | UUID
    created_at: datetime
    updated_at: datetime | None = None


class SpecificationDefinitionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_category_id: int | None = None
    asset_subcategory_id: int | None = None
    code: str
    name: str
    data_type: str
    unit_of_measure: str | None = None
    required_flag: bool = False
    display_order: int | None = Field(default=0, ge=0)


class SpecificationDefinitionCreate(SpecificationDefinitionBase):
    pass


class SpecificationDefinitionUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_category_id: int | None = None
    asset_subcategory_id: int | None = None
    code: str | None = None
    name: str | None = None
    data_type: str | None = None
    unit_of_measure: str | None = None
    required_flag: bool | None = None
    display_order: int | None = Field(default=None, ge=0)


class SpecificationDefinitionRead(SpecificationDefinitionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    category_name: str | None = None
    subcategory_name: str | None = None


# ─── Position Template Schemas ────────────────────────────────────────────────

class PositionTemplateNodeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position_type_id: int
    position_number: str
    maximum_capacity: int = Field(default=1, ge=1)
    node_order: int = Field(default=0, ge=0)
    remarks: str | None = None


class PositionTemplateNodeCreate(PositionTemplateNodeBase):
    pass


class PositionTemplateNodeUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position_type_id: int | None = None
    position_number: str | None = None
    maximum_capacity: int | None = Field(default=None, ge=1)
    node_order: int | None = Field(default=None, ge=0)
    remarks: str | None = None


class PositionTemplateNodeRead(PositionTemplateNodeBase):
    id: int
    position_template_id: int
    position_type_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class PositionTemplateBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    description: str | None = None
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class PositionTemplateCreate(PositionTemplateBase):
    pass


class PositionTemplateUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None = None
    name: str | None = None
    description: str | None = None
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class PositionTemplateRead(PositionTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    nodes: List[PositionTemplateNodeRead] = []
    node_count: int = 0


# ─── Work Type Schemas ────────────────────────────────────────────────────────

class WorkTypeBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    description: str | None = None
    is_active: bool = True


class WorkTypeCreate(WorkTypeBase):
    pass


class WorkTypeUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None = None
    description: str | None = None
    is_active: bool | None = None


class WorkTypeRead(WorkTypeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
