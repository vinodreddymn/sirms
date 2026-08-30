from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin


class Incident(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = ({"schema": "incident"},)

    work_request_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    work_type_id: Mapped[UUID] = mapped_column(ForeignKey("master.work_types.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT"))
    
    status_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_status.id", ondelete="SET NULL", onupdate="RESTRICT"))
    priority_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_priority.id", ondelete="SET NULL", onupdate="RESTRICT"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_categories.id", ondelete="SET NULL", onupdate="RESTRICT"))
    
    assigned_to_id: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    
    target_start_date: Mapped[datetime | None] = mapped_column(DateTime)
    target_completion_date: Mapped[datetime | None] = mapped_column(DateTime)
    actual_start_date: Mapped[datetime | None] = mapped_column(DateTime)
    actual_completion_date: Mapped[datetime | None] = mapped_column(DateTime)
    
    estimated_cost: Mapped[float | None] = mapped_column(Integer)
    actual_cost: Mapped[float | None] = mapped_column(Integer)

    reported_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    reported_at: Mapped[datetime] = mapped_column("reported_date", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    closed_date: Mapped[datetime | None] = mapped_column(DateTime)
    closed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    completion_notes: Mapped[str | None] = mapped_column(Text)


class IncidentUpdate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incident_updates"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    status_after_update_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_status.id", ondelete="SET NULL", onupdate="RESTRICT"))
    updated_by: Mapped[UUID | None] = mapped_column("update_user_id", ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    update_notes: Mapped[str] = mapped_column("remarks", Text, nullable=False)
    time_spent_minutes: Mapped[int | None] = mapped_column(Integer)
    update_at: Mapped[datetime] = mapped_column("update_datetime", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class IncidentAttachment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incident_attachments"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    attachment_id: Mapped[UUID] = mapped_column(ForeignKey("common.attachments.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    category: Mapped[str | None] = mapped_column("attachment_category", String(20))


class WorkAssignment(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "work_assignments"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    assignment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_to: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    assigned_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    assigned_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    accepted_date: Mapped[datetime | None] = mapped_column(DateTime)
    started_date: Mapped[datetime | None] = mapped_column(DateTime)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_date: Mapped[datetime | None] = mapped_column(DateTime)
    assignment_status: Mapped[str] = mapped_column(String(50), nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)


class WorkAction(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "work_actions"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("security.users.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    reference_type: Mapped[str | None] = mapped_column(String(100))
    reference_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))


class WorkRelation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "work_relations"
    __table_args__ = ({"schema": "incident"},)

    source_incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    target_incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)


class PMDetails(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "pm_details"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completion_date: Mapped[date | None] = mapped_column(Date)
    pm_checklist_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    remarks: Mapped[str | None] = mapped_column(Text)


class InspectionDetails(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "inspection_details"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    inspection_date: Mapped[date | None] = mapped_column(Date)
    inspector_id: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    result: Mapped[str | None] = mapped_column(String(50))
    remarks: Mapped[str | None] = mapped_column(Text)


class InstallationDetails(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "installation_details"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    installation_date: Mapped[date | None] = mapped_column(Date)
    installed_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    sign_off_date: Mapped[date | None] = mapped_column(Date)
    remarks: Mapped[str | None] = mapped_column(Text)


class VendorRepairDetails(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "vendor_repair_details"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    vendor_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    dispatch_date: Mapped[date | None] = mapped_column(Date)
    expected_return_date: Mapped[date | None] = mapped_column(Date)
    actual_return_date: Mapped[date | None] = mapped_column(Date)
    repair_cost: Mapped[float | None] = mapped_column(Integer)
    remarks: Mapped[str | None] = mapped_column(Text)


class CalibrationDetails(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "calibration_details"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False, unique=True)
    calibration_date: Mapped[date | None] = mapped_column(Date)
    next_due_date: Mapped[date | None] = mapped_column(Date)
    calibrated_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    certificate_number: Mapped[str | None] = mapped_column(String(100))
    result: Mapped[str | None] = mapped_column(String(50))
    remarks: Mapped[str | None] = mapped_column(Text)
