from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StockTransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    asset_id: UUID | None = None
    transaction_type_id: int | None = None
    location_id: UUID | None = None
    vendor_id: UUID | None = None
    quantity: int
    transaction_at: datetime
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class StockTransactionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    asset_id: UUID | None = None
    transaction_type_id: int | None = None
    location_id: UUID | None = None
    vendor_id: UUID | None = None
    quantity: int
    remarks: str | None = None
