from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssetBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    asset_number: str
    asset_category_id: int
    asset_subcategory_id: int | None = None
    manufacturer_id: int | None = None
    asset_model_id: int | None = None
    asset_status_id: int
    asset_condition_id: int | None = None
    asset_lifecycle_id: int | None = None
    serial_number: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    purchase_date: date | None = None
    warranty_expiry: date | None = None
    current_location_id: UUID | None = None
    remarks: str | None = None
    asset_role: str = "SPARE"
    health_rating: str | None = None
    network_configuration: dict[str, object] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    specification_values: list["AssetSpecificationValueUpsert"] = Field(default_factory=list)
    location_position_id: UUID | None = None
    installation_date: date | None = None
    relationship_ids: dict[str, list[UUID]] = Field(default_factory=dict)


class AssetUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID | None = None
    asset_number: str | None = None
    asset_category_id: int | None = None
    asset_subcategory_id: int | None = None
    asset_model_id: int | None = None
    manufacturer_id: int | None = None
    current_location_id: UUID | None = None
    asset_status_id: int | None = None
    asset_condition_id: int | None = None
    asset_lifecycle_id: int | None = None
    serial_number: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    purchase_date: date | None = None
    warranty_expiry: date | None = None
    remarks: str | None = None
    specification_values: list["AssetSpecificationValueUpsert"] | None = None
    location_position_id: UUID | None = None
    installation_date: date | None = None
    relationship_ids: dict[str, list[UUID]] | None = None


class AssetLookupRead(BaseModel):
    id: str | int | UUID | None = None
    code: str | None = None
    name: str


class AssetListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    asset_number: str
    category: str
    subcategory: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    barcode: str | None = None
    status: str
    condition: str | None = None
    lifecycle: str | None = None
    current_location: str | None = None
    purchase_date: date | None = None
    warranty_expiry: date | None = None
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AssetSummaryRead(BaseModel):
    total_assets: int = 0
    active_assets: int = 0
    assets_in_repair: int = 0
    retired_assets: int = 0
    warranty_expiring_soon: int = 0


class AssetSpecificationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    specification_definition_id: int
    value_text: str | None = None
    value_number: Decimal | None = None
    value_boolean: bool | None = None
    value_date: date | None = None
    value_json: dict[str, object] | None = None


class AssetSpecificationCreate(AssetSpecificationBase):
    pass


class AssetSpecificationValueUpsert(AssetSpecificationBase):
    pass


class AssetSpecificationRead(AssetSpecificationBase):
    id: UUID
    asset_id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class AssetSpecificationDefinitionRead(BaseModel):
    id: int
    code: str
    name: str
    data_type: str
    unit_of_measure: str | None = None
    required_flag: bool = False
    display_order: int = 0


class AssetSpecificationValueRead(BaseModel):
    id: UUID
    specification_definition_id: int
    specification_name: str
    code: str
    data_type: str
    unit: str | None = None
    value: str | int | float | bool | date | dict[str, object] | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AssetInstallationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_position_id: UUID
    installed_on: date | None = None
    removed_on: date | None = None
    current_flag: bool = True


class AssetInstallationRead(AssetInstallationCreate):
    id: UUID
    asset_id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class AssetInstallationInfoRead(BaseModel):
    location_id: UUID | None = None
    location_name: str | None = None
    position_id: UUID | None = None
    position_name: str | None = None
    installed_on: date | None = None
    removed_on: date | None = None
    current_flag: bool = True


class AssetMovementCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    movement_type_id: int | None = None
    from_location_id: UUID | None = None
    to_location_id: UUID | None = None
    vendor_id: UUID | None = None
    quantity: int | None = None
    remarks: str | None = None


class AssetMovementRead(AssetMovementCreate):
    id: UUID
    asset_id: UUID
    moved_at: datetime
    created_at: datetime
    updated_at: datetime | None = None


class AssetMovementHistoryRead(BaseModel):
    id: UUID
    movement_type: str | None = None
    from_location: str | None = None
    to_location: str | None = None
    vendor: str | None = None
    quantity: int | None = None
    moved_at: datetime
    remarks: str | None = None


class AssetMovementListRead(AssetMovementHistoryRead):
    asset_id: UUID
    asset_number: str


class AssetDocumentRead(BaseModel):
    id: UUID
    attachment_id: UUID
    file_name: str
    file_path: str
    mime_type: str | None = None
    file_size_bytes: int | None = None
    document_type: str | None = None
    created_at: datetime


class AssetPhotoRead(BaseModel):
    id: UUID
    attachment_id: UUID
    file_name: str
    file_path: str
    mime_type: str | None = None
    created_at: datetime


class AssetRelationshipRead(BaseModel):
    id: UUID
    related_asset_id: UUID
    related_asset_number: str
    related_asset_name: str
    relationship_type: str | None = None
    direction: str


class AssetChecklistTaskRead(BaseModel):
    id: UUID
    task_description: str
    sequence_order: int
    is_required: bool


class AssetMaintenanceScheduleRead(BaseModel):
    id: UUID
    checklist_id: UUID
    checklist_name: str
    next_due_date: date | None = None
    frequency_days: int | None = None
    is_active: bool
    last_maintenance: date | None = None
    tasks: list[AssetChecklistTaskRead] = Field(default_factory=list)


class AssetMaintenanceHistoryRead(BaseModel):
    id: UUID
    schedule_id: UUID
    checklist_name: str
    performed_on: date | None = None
    completed: bool
    remarks: str | None = None
    performed_by: UUID | None = None


class AssetDetailsRead(BaseModel):
    id: UUID
    basic_information: AssetListRead
    qr_code: str | None = None
    project: AssetLookupRead
    status: AssetLookupRead
    condition: AssetLookupRead | None = None
    lifecycle: AssetLookupRead | None = None
    category: AssetLookupRead
    subcategory: AssetLookupRead | None = None
    manufacturer: AssetLookupRead | None = None
    model: AssetLookupRead | None = None
    installation: AssetInstallationInfoRead | None = None
    specifications: list[AssetSpecificationValueRead] = Field(default_factory=list)
    power_sources: list[AssetRelationshipRead] = Field(default_factory=list)
    network_connections: list[AssetRelationshipRead] = Field(default_factory=list)
    parent_assets: list[AssetRelationshipRead] = Field(default_factory=list)
    child_assets: list[AssetRelationshipRead] = Field(default_factory=list)
    related_assets: list[AssetRelationshipRead] = Field(default_factory=list)
    movement_history: list[AssetMovementHistoryRead] = Field(default_factory=list)
    documents: list[AssetDocumentRead] = Field(default_factory=list)
    photos: list[AssetPhotoRead] = Field(default_factory=list)
    maintenance_schedules: list[AssetMaintenanceScheduleRead] = Field(default_factory=list)
    maintenance_history: list[AssetMaintenanceHistoryRead] = Field(default_factory=list)


class RepairHistoryCreate(BaseModel):
    fault_date: date
    fault_description: str
    removed_from_location_id: UUID | None = None
    removal_date: date | None = None
    replacement_asset_id: UUID | None = None
    dispatch_date: date | None = None
    courier_number: str | None = None
    vendor_id: UUID | None = None
    repair_cost: Decimal | None = None
    rma_number: str | None = None
    return_date: date | None = None
    repair_remarks: str | None = None
    repair_warranty_expiry: date | None = None
    repair_report_attachment_id: UUID | None = None


class RepairHistoryRead(RepairHistoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    asset_id: UUID
    created_at: datetime


class AssetReplacementRequest(BaseModel):
    spare_asset_id: UUID
    replacement_date: date = Field(default_factory=date.today)
    reason: str
    remarks: str | None = None
    faulty_destination_location_id: UUID | None = None


class ReplacementAssetRead(BaseModel):
    id: UUID
    asset_number: str
    serial_number: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    status: str
    asset_role: str
    current_location: str | None = None


class AssetReplacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    old_asset_id: UUID
    new_asset_id: UUID
    replacement_date: date
    engineer_id: UUID | None = None
    reason: str
    remarks: str | None = None
    created_at: datetime


class AssetTimelineEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_type: str
    event_at: datetime
    description: str
    metadata_json: dict[str, object] = Field(default_factory=dict)
    created_by: UUID | None = None


class AssetFieldNoteCreate(BaseModel):
    note: str
    observed_at: datetime | None = None


class AssetFieldNoteRead(AssetFieldNoteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    asset_id: UUID
    observed_at: datetime
    created_by: UUID | None = None
