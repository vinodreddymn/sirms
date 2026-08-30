"""Pydantic schemas for the Dispatch & Delivery Challan module."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Dispatch Item schemas ─────────────────────────────────────────────────────

class DispatchItemCreate(BaseModel):
    asset_id: UUID | None = None
    dispatch_type: str = "Asset"  # Asset | Component
    component_name: str | None = None
    quantity: int = Field(default=1, ge=1)
    condition: str  # Faulty | Working | Damaged
    remarks: str | None = None


class DispatchItemUpdate(BaseModel):
    component_name: str | None = None
    quantity: int | None = Field(default=None, ge=1)
    condition: str | None = None
    remarks: str | None = None


class ReceiveItemRequest(BaseModel):
    return_date: date
    result: str  # Repaired | Replaced | Beyond Repair | Returned Without Repair
    store_location_id: UUID | None = None
    to_location_id: UUID | None = None
    repair_cost: Decimal | None = None
    remarks: str | None = None


class DispatchItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dispatch_id: UUID
    asset_id: UUID | None = None
    asset_number: str | None = None
    asset_category: str | None = None
    asset_subcategory: str | None = None
    asset_serial_number: str | None = None
    dispatch_type: str
    component_name: str | None = None
    quantity: int
    condition: str
    status: str
    return_date: date | None = None
    result: str | None = None
    repair_cost: Decimal | None = None
    remarks: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


# ── Dispatch schemas ──────────────────────────────────────────────────────────

class DispatchCreate(BaseModel):
    dispatch_date: date
    vendor_id: UUID | None = None
    purpose: str  # Repair | Warranty | Calibration | Transfer | Others
    courier_name: str | None = None
    tracking_number: str | None = None
    remarks: str | None = None
    items: list[DispatchItemCreate] = Field(default_factory=list)


class DispatchUpdate(BaseModel):
    dispatch_date: date | None = None
    vendor_id: UUID | None = None
    purpose: str | None = None
    courier_name: str | None = None
    tracking_number: str | None = None
    remarks: str | None = None


class DispatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dispatch_no: str
    delivery_challan_no: str | None = None
    dispatch_date: date
    vendor_id: UUID | None = None
    vendor_name: str | None = None
    purpose: str
    courier_name: str | None = None
    tracking_number: str | None = None
    remarks: str | None = None
    status: str
    item_count: int = 0
    returned_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None


class DispatchDetailsRead(DispatchRead):
    items: list[DispatchItemRead] = Field(default_factory=list)
