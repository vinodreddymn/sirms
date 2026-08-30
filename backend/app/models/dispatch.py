"""SQLAlchemy models for the Dispatch & Delivery Challan module (inventory schema)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin
from app.models.asset import Asset


class Dispatch(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """A single dispatch event that may contain multiple items."""

    __tablename__ = "dispatches"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('Repair', 'Warranty', 'Calibration', 'Transfer', 'Others')",
            name="chk_dispatches_purpose",
        ),
        CheckConstraint(
            "status IN ('Draft', 'Dispatched', 'Partially Returned', 'Closed', 'Cancelled')",
            name="chk_dispatches_status",
        ),
        {"schema": "inventory"},
    )

    dispatch_no: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    delivery_challan_no: Mapped[str | None] = mapped_column(String(30))
    dispatch_date: Mapped[date] = mapped_column(Date, nullable=False)
    vendor_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("common.vendors.id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    courier_name: Mapped[str | None] = mapped_column(String(150))
    tracking_number: Mapped[str | None] = mapped_column(String(100))
    remarks: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default=text("'Draft'")
    )

    items: Mapped[list["DispatchItem"]] = relationship(
        "DispatchItem",
        back_populates="dispatch",
        cascade="all, delete-orphan",
        lazy="select",
    )


class DispatchItem(UUIDPrimaryKeyMixin, AuditMixin, Base):
    """A single asset or component line within a dispatch."""

    __tablename__ = "dispatch_items"
    __table_args__ = (
        CheckConstraint(
            "dispatch_type IN ('Asset', 'Component')",
            name="chk_dispatch_items_dispatch_type",
        ),
        CheckConstraint(
            "condition IN ('Faulty', 'Working', 'Damaged')",
            name="chk_dispatch_items_condition",
        ),
        CheckConstraint(
            "status IN ('Out', 'Returned')",
            name="chk_dispatch_items_status",
        ),
        CheckConstraint(
            "result IS NULL OR result IN ('Repaired', 'Replaced', 'Beyond Repair', 'Returned Without Repair')",
            name="chk_dispatch_items_result",
        ),
        {"schema": "inventory"},
    )

    dispatch_id: Mapped[UUID] = mapped_column(
        ForeignKey("inventory.dispatches.id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("asset.assets.id", ondelete="RESTRICT", onupdate="RESTRICT")
    )
    dispatch_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'Asset'")
    )
    component_name: Mapped[str | None] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'Out'")
    )
    return_date: Mapped[date | None] = mapped_column(Date)
    result: Mapped[str | None] = mapped_column(String(30))
    repair_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    remarks: Mapped[str | None] = mapped_column(Text)

    dispatch: Mapped["Dispatch"] = relationship("Dispatch", back_populates="items")
    asset: Mapped[Asset | None] = relationship("Asset", lazy="joined")
