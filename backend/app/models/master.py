from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint, text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime

from app.db.base import AuditMixin, Base, BigIntPrimaryKeyMixin, MasterLookupMixin


class LocationType(MasterLookupMixin, Base):
    __tablename__ = "location_types"
    __table_args__ = {"schema": "master"}


class LocationTemplate(MasterLookupMixin, Base):
    __tablename__ = "location_templates"
    __table_args__ = {"schema": "master"}


class LocationTemplateNode(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "location_template_nodes"
    __table_args__ = (
        UniqueConstraint("location_template_id", "code", name="uq_location_template_nodes"),
        {"schema": "master"},
    )

    location_template_id: Mapped[int] = mapped_column(ForeignKey("master.location_templates.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    parent_node_id: Mapped[int | None] = mapped_column(ForeignKey("master.location_template_nodes.id", ondelete="CASCADE", onupdate="RESTRICT"))
    location_type_id: Mapped[int] = mapped_column(ForeignKey("master.location_types.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    node_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    create_positions_from_template: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    position_template_id: Mapped[int | None] = mapped_column(ForeignKey("master.position_templates.id", ondelete="SET NULL", onupdate="RESTRICT"))
    remarks: Mapped[str | None] = mapped_column(Text)


class PositionType(MasterLookupMixin, Base):
    __tablename__ = "position_types"
    __table_args__ = {"schema": "master"}


class PositionTemplate(MasterLookupMixin, Base):
    __tablename__ = "position_templates"
    __table_args__ = {"schema": "master"}


class PositionTemplateNode(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "position_template_nodes"
    __table_args__ = (
        UniqueConstraint("position_template_id", "position_number", name="uq_position_template_nodes"),
        {"schema": "master"},
    )

    position_template_id: Mapped[int] = mapped_column(ForeignKey("master.position_templates.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    position_type_id: Mapped[int] = mapped_column(ForeignKey("master.position_types.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    position_number: Mapped[str] = mapped_column(String(50), nullable=False)
    maximum_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    node_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    remarks: Mapped[str | None] = mapped_column(Text)


class AssetCategory(MasterLookupMixin, Base):
    __tablename__ = "asset_categories"
    __table_args__ = {"schema": "master"}


class AssetSubcategory(MasterLookupMixin, Base):
    __tablename__ = "asset_subcategories"
    __table_args__ = {"schema": "master"}

    asset_category_id: Mapped[int] = mapped_column(ForeignKey("master.asset_categories.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)


class Manufacturer(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "manufacturers"
    __table_args__ = {"schema": "master"}

    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class ManufacturerAssetScope(BigIntPrimaryKeyMixin, Base):
    __tablename__ = "manufacturer_asset_scopes"
    __table_args__ = (UniqueConstraint("manufacturer_id", "asset_category_id", "asset_subcategory_id", name="uq_manufacturer_asset_scope"), {"schema": "master"})
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("master.manufacturers.id", ondelete="CASCADE"), nullable=False)
    asset_category_id: Mapped[int] = mapped_column(ForeignKey("master.asset_categories.id"), nullable=False)
    asset_subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("master.asset_subcategories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))


class AssetModel(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "asset_models"
    __table_args__ = {"schema": "master"}

    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("master.manufacturers.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    asset_subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("master.asset_subcategories.id", ondelete="SET NULL", onupdate="RESTRICT"))
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class AssetStatus(MasterLookupMixin, Base):
    __tablename__ = "asset_status"
    __table_args__ = {"schema": "master"}


class AssetCondition(MasterLookupMixin, Base):
    __tablename__ = "asset_condition"
    __table_args__ = {"schema": "master"}


class AssetLifecycle(MasterLookupMixin, Base):
    __tablename__ = "asset_lifecycle"
    __table_args__ = {"schema": "master"}


class MaintenanceType(MasterLookupMixin, Base):
    __tablename__ = "maintenance_types"
    __table_args__ = {"schema": "master"}


class FailureCategory(MasterLookupMixin, Base):
    __tablename__ = "failure_categories"
    __table_args__ = {"schema": "master"}


class RootCauseCategory(MasterLookupMixin, Base):
    __tablename__ = "root_cause_categories"
    __table_args__ = {"schema": "master"}


class IncidentStatus(MasterLookupMixin, Base):
    __tablename__ = "incident_status"
    __table_args__ = {"schema": "master"}


class IncidentPriority(MasterLookupMixin, Base):
    __tablename__ = "incident_priority"
    __table_args__ = {"schema": "master"}


class IncidentCategory(MasterLookupMixin, Base):
    __tablename__ = "incident_categories"
    __table_args__ = {"schema": "master"}



class RelationshipType(MasterLookupMixin, Base):
    __tablename__ = "relationship_types"
    __table_args__ = {"schema": "master"}


class DocumentType(MasterLookupMixin, Base):
    __tablename__ = "document_types"
    __table_args__ = {"schema": "master"}


class PhotoType(MasterLookupMixin, Base):
    __tablename__ = "photo_types"
    __table_args__ = {"schema": "master"}


class ProjectType(MasterLookupMixin, Base):
    __tablename__ = "project_types"
    __table_args__ = {"schema": "master"}


class UserRoleTemplate(MasterLookupMixin, Base):
    __tablename__ = "user_role_templates"
    __table_args__ = {"schema": "master"}


class SpecificationDefinition(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "specification_definitions"
    __table_args__ = (
        CheckConstraint("data_type IN ('TEXT', 'NUMBER', 'BOOLEAN', 'DATE', 'JSON')", name="data_type"),
        {"schema": "master"},
    )

    asset_category_id: Mapped[int | None] = mapped_column(ForeignKey("master.asset_categories.id", ondelete="SET NULL", onupdate="RESTRICT"))
    asset_subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("master.asset_subcategories.id", ondelete="SET NULL", onupdate="RESTRICT"))
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_of_measure: Mapped[str | None] = mapped_column(String(30))
    required_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class MovementType(MasterLookupMixin, Base):
    __tablename__ = "movement_types"
    __table_args__ = {"schema": "master"}


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    __table_args__ = {"schema": "master"}

    id: Mapped[UUID] = mapped_column("expense_category_id", PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    code: Mapped[str] = mapped_column("category_code", String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column("category_name", String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)


class PaymentMode(Base):
    __tablename__ = "payment_modes"
    __table_args__ = {"schema": "master"}

    id: Mapped[UUID] = mapped_column("payment_mode_id", PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    code: Mapped[str] = mapped_column("payment_mode_code", String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column("payment_mode_name", String(100), nullable=False, unique=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class PaymentStatus(Base):
    __tablename__ = "payment_statuses"
    __table_args__ = {"schema": "master"}

    id: Mapped[UUID] = mapped_column("payment_status_id", PGUUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    code: Mapped[str] = mapped_column("status_code", String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column("status_name", String(100), nullable=False, unique=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class StockTransactionType(BigIntPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "stock_transaction_types"
    __table_args__ = (
        CheckConstraint("quantity_effect IN (-1, 1)", name="quantity_effect"),
        {"schema": "master"},
    )

    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    quantity_effect: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
