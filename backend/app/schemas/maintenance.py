from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceChecklistBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID | None = None
    checklist_name: str
    remarks: str | None = None


class MaintenanceChecklistCreate(MaintenanceChecklistBase):
    pass


class MaintenanceChecklistUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID | None = None
    checklist_name: str | None = None
    remarks: str | None = None


class MaintenanceChecklistRead(MaintenanceChecklistBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class ChecklistItemBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    checklist_id: UUID
    task_description: str
    sequence_order: int = 0
    is_required: bool = True


class ChecklistItemCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_description: str
    sequence_order: int = 0
    is_required: bool = True


class ChecklistItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_description: str | None = None
    sequence_order: int | None = None
    is_required: bool | None = None


class ChecklistItemRead(ChecklistItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class MaintenanceScheduleBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID | None = None
    checklist_id: UUID
    next_due_date: date | None = None
    frequency_days: int | None = None
    is_active: bool = True


class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    pass


class MaintenanceScheduleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asset_id: UUID | None = None
    checklist_id: UUID | None = None
    next_due_date: date | None = None
    frequency_days: int | None = None
    is_active: bool | None = None


class MaintenanceScheduleRead(MaintenanceScheduleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class MaintenanceHistoryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: UUID
    performed_by: UUID | None = None
    performed_on: date | None = None
    remarks: str | None = None
    completed: bool = False


class MaintenanceHistoryCreate(MaintenanceHistoryBase):
    pass


class MaintenanceHistoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    performed_by: UUID | None = None
    performed_on: date | None = None
    remarks: str | None = None
    completed: bool | None = None


class MaintenanceHistoryRead(MaintenanceHistoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None


class StockTransactionBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    asset_id: UUID | None = None
    transaction_type_id: int | None = None
    location_id: UUID | None = None
    vendor_id: UUID | None = None
    quantity: int
    remarks: str | None = None


class StockTransactionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    asset_id: UUID | None = None
    transaction_type_id: int | None = None
    location_id: UUID | None = None
    vendor_id: UUID | None = None
    quantity: int
    remarks: str | None = None


class StockTransactionRead(StockTransactionBase):
    id: UUID
    transaction_at: datetime
    created_at: datetime
    updated_at: datetime | None = None
