from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin


class Customer(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "customers"
    __table_args__ = {"schema": "common"}

    customer_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    contact_person: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(150))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    remarks: Mapped[str | None] = mapped_column(Text)


class Project(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "common"}

    customer_id: Mapped[UUID] = mapped_column(ForeignKey("common.customers.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    project_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.project_types.id", ondelete="SET NULL", onupdate="RESTRICT"))
    project_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    project_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    remarks: Mapped[str | None] = mapped_column(Text)


class Vendor(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "vendors"
    __table_args__ = {"schema": "common"}

    vendor_code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    vendor_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    vendor_type: Mapped[str] = mapped_column(String(30), nullable=False)
    contact_person: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(150))
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    address_line: Mapped[str | None] = mapped_column(String(255))
    remarks: Mapped[str | None] = mapped_column(Text)


class VendorAssetScope(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "vendor_asset_scopes"
    __table_args__ = (UniqueConstraint("vendor_id", "asset_category_id", "asset_subcategory_id", "manufacturer_id", name="uq_vendor_asset_scope"), {"schema": "common"})
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("common.vendors.id", ondelete="CASCADE"), nullable=False)
    asset_category_id: Mapped[int] = mapped_column(ForeignKey("master.asset_categories.id"), nullable=False)
    asset_subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("master.asset_subcategories.id"))
    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("master.manufacturers.id"))
    service_type: Mapped[str | None] = mapped_column(String(30))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))


class Attachment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "attachments"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    document_type_id: Mapped[int | None] = mapped_column(ForeignKey("master.document_types.id", ondelete="SET NULL", onupdate="RESTRICT"))
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    checksum: Mapped[str | None] = mapped_column(String(128))
    remarks: Mapped[str | None] = mapped_column(Text)


class AuditLog(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    schema_name: Mapped[str] = mapped_column(String(50), nullable=False)
    table_name: Mapped[str] = mapped_column(String(150), nullable=False)
    record_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    action_name: Mapped[str] = mapped_column(String(30), nullable=False)
    old_data: Mapped[dict | None] = mapped_column(JSONB)
    new_data: Mapped[dict | None] = mapped_column(JSONB)
    action_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    ip_address: Mapped[str | None] = mapped_column(String(64))


class ActivityLog(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "activity_logs"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    activity_details: Mapped[dict | None] = mapped_column(JSONB)
    activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Notification(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = {"schema": "common"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    entity_name: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    notification_title: Mapped[str] = mapped_column(String(150), nullable=False)
    notification_body: Mapped[str] = mapped_column(Text, nullable=False)
    channel_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)


class SystemSetting(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "system_settings"
    __table_args__ = {"schema": "common"}

    setting_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
    setting_group: Mapped[str] = mapped_column(String(50), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)


class DashboardPreference(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "dashboard_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", "preference_name", name="uq_dashboard_preferences"),
        {"schema": "common"},
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    preference_name: Mapped[str] = mapped_column(String(100), nullable=False)
    preference_json: Mapped[dict] = mapped_column(JSONB, nullable=False)


class SavedSearch(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "saved_searches"
    __table_args__ = {"schema": "common"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    search_name: Mapped[str] = mapped_column(String(100), nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    search_criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)


class SavedFilter(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "saved_filters"
    __table_args__ = {"schema": "common"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    filter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    filter_criteria: Mapped[dict] = mapped_column(JSONB, nullable=False)


class ReportDefinition(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "report_definitions"
    __table_args__ = {"schema": "common"}

    report_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    report_name: Mapped[str] = mapped_column(String(150), nullable=False)
    module_name: Mapped[str] = mapped_column(String(50), nullable=False)
    definition_json: Mapped[dict] = mapped_column(JSONB, nullable=False)


class SavedReport(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "saved_reports"
    __table_args__ = {"schema": "common"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    report_definition_id: Mapped[UUID] = mapped_column(ForeignKey("common.report_definitions.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    report_name: Mapped[str] = mapped_column(String(150), nullable=False)
    parameters_json: Mapped[dict | None] = mapped_column(JSONB)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime)


class QrGenerationHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "qr_generation_history"
    __table_args__ = {"schema": "common"}

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    generated_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    qr_value: Mapped[str] = mapped_column(String(150), nullable=False)


class QrPrintHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "qr_print_history"
    __table_args__ = {"schema": "common"}

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    printed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    printed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    copies_printed: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class BarcodeHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "barcode_history"
    __table_args__ = {"schema": "common"}

    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    barcode_value: Mapped[str] = mapped_column(String(150), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    generated_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))


class ImportJob(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "import_jobs"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    import_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)


class ImportError(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "import_errors"
    __table_args__ = {"schema": "common"}

    import_job_id: Mapped[UUID] = mapped_column(ForeignKey("common.import_jobs.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    row_number: Mapped[int | None] = mapped_column(Integer)
    field_name: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(Text, nullable=False)


class ExportHistory(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "export_history"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255))
    exported_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class Comment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "comments"
    __table_args__ = {"schema": "common"}

    project_id: Mapped[UUID | None] = mapped_column(ForeignKey("common.projects.id", ondelete="SET NULL", onupdate="RESTRICT"))
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    commented_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)


class Tag(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "common"}

    tag_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    tag_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tag_color: Mapped[str | None] = mapped_column(String(20))
    remarks: Mapped[str | None] = mapped_column(Text)


class EntityTag(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "entity_tags"
    __table_args__ = (
        UniqueConstraint("tag_id", "entity_name", "entity_id", name="uq_entity_tags"),
        {"schema": "common"},
    )

    tag_id: Mapped[UUID] = mapped_column(ForeignKey("common.tags.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)


class FavoriteAsset(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "favorite_assets"
    __table_args__ = (
        UniqueConstraint("user_id", "asset_id", name="uq_favorite_assets"),
        {"schema": "common"},
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="CASCADE", onupdate="RESTRICT"))


class WatchList(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "watch_list"
    __table_args__ = (
        UniqueConstraint("user_id", "incident_id", name="uq_watch_list"),
        {"schema": "common"},
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    incident_id: Mapped[UUID | None] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"))


class NotificationPreference(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "notification_preferences"
    __table_args__ = {"schema": "common"}

    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    sms_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    push_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    quiet_hours_from: Mapped[time | None] = mapped_column(Time)
    quiet_hours_to: Mapped[time | None] = mapped_column(Time)


class NumberSequence(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "number_sequences"
    __table_args__ = {"schema": "common"}

    entity_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    prefix: Mapped[str] = mapped_column(String(20), nullable=False)
    current_value: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    number_length: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("6"))
    reset_policy: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'NEVER'"))
    last_reset_on: Mapped[date | None] = mapped_column(Date)
