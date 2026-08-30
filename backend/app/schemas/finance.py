from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    project_id: UUID
    expense_date: date
    expense_category_id: UUID
    description: str | None = None
    bill_reference: str | None = None
    amount: Decimal = Field(..., ge=0)
    payment_mode_id: UUID
    payment_status_id: UUID
    remarks: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID | None = None
    expense_date: date | None = None
    expense_category_id: UUID | None = None
    description: str | None = None
    bill_reference: str | None = None
    amount: Decimal | None = Field(None, ge=0)
    payment_mode_id: UUID | None = None
    payment_status_id: UUID | None = None
    remarks: str | None = None


class ExpenseResponse(ExpenseBase):
    id: UUID
    expense_number: str = Field(..., alias="expense_no")
    created_at: datetime
    updated_at: datetime | None = None


class ExpenseFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID | None = None
    category_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    payment_mode_id: int | None = None
    payment_status_id: int | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    search: str | None = None
    sort_by: str | None = None
    sort_dir: str | None = None


class ExpenseAttachmentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attachment_id: UUID
    category: str | None = None


class ExpenseAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    expense_id: UUID
    attachment_id: UUID
    filename: str | None = None
    file_name: str | None = None
    url: str | None = None
    category: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
