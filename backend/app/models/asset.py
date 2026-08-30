from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin
from app.models.master import AssetCategory, AssetSubcategory


class Asset(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "assets"
    __table_args__ = ({"schema": "asset"},)

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    asset_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    asset_category_id: Mapped[int] = mapped_column(
        ForeignKey("master.asset_categories.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )
    asset_subcategory_id: Mapped[int | None] = mapped_column(
        ForeignKey("master.asset_subcategories.id", ondelete="SET NULL", onupdate="RESTRICT")
    )
    asset_category: Mapped[AssetCategory] = relationship("AssetCategory", lazy="joined")
    asset_subcategory: Mapped[AssetSubcategory | None] = relationship("AssetSubcategory", lazy="joined")

    manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("master.manufacturers.id", ondelete="SET NULL", onupdate="RESTRICT")
    )

    asset_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("master.asset_models.id", ondelete="SET NULL", onupdate="RESTRICT")
    )

    asset_status_id: Mapped[int] = mapped_column(
        ForeignKey("master.asset_status.id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )

    asset_condition_id: Mapped[int | None] = mapped_column(
        ForeignKey("master.asset_condition.id", ondelete="SET NULL", onupdate="RESTRICT")
    )

    asset_lifecycle_id: Mapped[int | None] = mapped_column(
        ForeignKey("master.asset_lifecycle.id", ondelete="SET NULL", onupdate="RESTRICT")
    )

    serial_number: Mapped[str | None] = mapped_column(String(100))

    barcode: Mapped[str | None] = mapped_column(String(100))

    qr_code: Mapped[str | None] = mapped_column(String(100))

    purchase_date: Mapped[date | None] = mapped_column(Date)

    warranty_expiry: Mapped[date | None] = mapped_column(Date)

    current_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT")
    )

    remarks: Mapped[str | None] = mapped_column(Text)
    asset_role: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'SPARE'"))
    health_rating: Mapped[str | None] = mapped_column(String(20))


class RepairHistory(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "repair_history"
    __table_args__ = ({"schema": "asset"},)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id"), nullable=False)
    fault_date: Mapped[date] = mapped_column(Date, nullable=False)
    fault_description: Mapped[str] = mapped_column(Text, nullable=False)
    removed_from_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id"))
    removal_date: Mapped[date | None] = mapped_column(Date)
    replacement_asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id"))
    dispatch_date: Mapped[date | None] = mapped_column(Date)
    courier_number: Mapped[str | None] = mapped_column(String(100))
    vendor_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.vendors.id"))
    repair_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    rma_number: Mapped[str | None] = mapped_column(String(100))
    return_date: Mapped[date | None] = mapped_column(Date)
    repair_remarks: Mapped[str | None] = mapped_column(Text)
    repair_warranty_expiry: Mapped[date | None] = mapped_column(Date)
    repair_report_attachment_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.attachments.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id"))


class AssetReplacement(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "asset_replacements"
    __table_args__ = ({"schema": "asset"},)
    old_asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id"), nullable=False)
    new_asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id"), nullable=False)
    replacement_date: Mapped[date] = mapped_column(Date, nullable=False)
    engineer_id: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id"))
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class AssetTimelineEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "asset_timeline_events"
    __table_args__ = ({"schema": "asset"},)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    event_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'"))
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id"))


class AssetFieldNote(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "asset_field_notes"
    __table_args__ = ({"schema": "asset"},)
    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    created_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id"))

class AssetSpecification(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_specifications"
    __table_args__ = (
        UniqueConstraint("asset_id", "specification_definition_id", name="uq_asset_specifications"),
        {"schema": "asset"},
    )

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    specification_definition_id: Mapped[int] = mapped_column(ForeignKey("master.specification_definitions.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)

    value_text: Mapped[str | None] = mapped_column(String(500))
    value_number: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    value_boolean: Mapped[bool | None] = mapped_column(Boolean)
    value_date: Mapped[date | None] = mapped_column(Date)
    value_json: Mapped[dict | None] = mapped_column(JSONB)


class AssetInstallation(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_installations"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    location_position_id: Mapped[UUID] = mapped_column(ForeignKey("infrastructure.location_positions.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    installed_on: Mapped[date | None] = mapped_column(Date)
    removed_on: Mapped[date | None] = mapped_column(Date)
    current_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    installation_status: Mapped[str | None] = mapped_column(String(30), server_default=text("'INSTALLED'"))
    installed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    removed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    remarks: Mapped[str | None] = mapped_column(Text)


class AssetMovement(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_movements"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    movement_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.movement_types.id", ondelete="SET NULL", onupdate="RESTRICT"))
    from_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT"))
    to_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT"))
    vendor_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.vendors.id", ondelete="SET NULL", onupdate="RESTRICT"))
    moved_at: Mapped[datetime] = mapped_column(
        "movement_date",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    remarks: Mapped[str | None] = mapped_column(Text)


class StockTransaction(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "stock_transactions"
    __table_args__ = ({"schema": "asset"},)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    transaction_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.stock_transaction_types.id", ondelete="SET NULL", onupdate="RESTRICT"))
    location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT"))
    vendor_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.vendors.id", ondelete="SET NULL", onupdate="RESTRICT"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    remarks: Mapped[str | None] = mapped_column(Text)


class AssetDocument(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_documents"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    attachment_id: Mapped[UUID] = mapped_column(ForeignKey("common.attachments.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)


class AssetPhoto(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_photos"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    attachment_id: Mapped[UUID] = mapped_column(ForeignKey("common.attachments.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)


class AssetRelationship(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_relationships"
    __table_args__ = (
        UniqueConstraint("asset_id", "related_asset_id", name="uq_asset_relationships"),
        {"schema": "asset"},
    )

    asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    related_asset_id: Mapped[UUID] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    relationship_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.relationship_types.id", ondelete="SET NULL", onupdate="RESTRICT"))


class MaintenanceChecklist(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "maintenance_checklists"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    checklist_name: Mapped[str] = mapped_column(String(150), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)


class ChecklistItem(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "checklist_items"
    __table_args__ = ({"schema": "asset"},)

    checklist_id: Mapped[UUID] = mapped_column(ForeignKey("asset.maintenance_checklists.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    task_description: Mapped[str] = mapped_column("item_description", Text, nullable=False)
    sequence_order: Mapped[int] = mapped_column("item_sequence", Integer, nullable=False, server_default=text("0"))
    is_required: Mapped[bool] = mapped_column("is_mandatory", Boolean, nullable=False, server_default=text("TRUE"))


class MaintenanceSchedule(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "maintenance_schedules"
    __table_args__ = ({"schema": "asset"},)

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    checklist_id: Mapped[UUID] = mapped_column(ForeignKey("asset.maintenance_checklists.id", ondelete="SET NULL", onupdate="RESTRICT"), nullable=False)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    frequency_days: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))


class MaintenanceHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "maintenance_history"
    __table_args__ = ({"schema": "asset"},)

    schedule_id: Mapped[UUID] = mapped_column(
        "maintenance_schedule_id",
        ForeignKey("asset.maintenance_schedules.id", ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=False,
    )
    performed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    performed_on: Mapped[date | None] = mapped_column(Date)
    remarks: Mapped[str | None] = mapped_column("completion_notes", Text)
