from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin


class Incident(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = ({"schema": "incident"},)

    incident_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(ForeignKey("asset.assets.id", ondelete="SET NULL", onupdate="RESTRICT"))
    location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="SET NULL", onupdate="RESTRICT"))
    incident_status_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_status.id", ondelete="SET NULL", onupdate="RESTRICT"))
    incident_priority_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_priority.id", ondelete="SET NULL", onupdate="RESTRICT"))
    incident_category_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_categories.id", ondelete="SET NULL", onupdate="RESTRICT"))
    reported_by: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    reported_at: Mapped[datetime] = mapped_column("reported_date", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    closed_date: Mapped[datetime | None] = mapped_column(DateTime)


class IncidentUpdate(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incident_updates"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    status_after_update_id: Mapped[int | None] = mapped_column(ForeignKey("master.incident_status.id", ondelete="SET NULL", onupdate="RESTRICT"))
    updated_by: Mapped[UUID | None] = mapped_column("update_user_id", ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    update_notes: Mapped[str] = mapped_column("remarks", Text, nullable=False)
    update_at: Mapped[datetime] = mapped_column("update_datetime", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class WorkOrder(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "work_orders"
    __table_args__ = ({"schema": "incident"},)

    work_order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    assigned_to: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))
    status_id: Mapped[int] = mapped_column("work_order_status_id", ForeignKey("master.work_order_status.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    planned_start_date: Mapped[date | None] = mapped_column("planned_start", Date)
    actual_start_date: Mapped[date | None] = mapped_column("actual_start", Date)
    actual_end_date: Mapped[date | None] = mapped_column("actual_finish", Date)
    remarks: Mapped[str | None] = mapped_column("completion_notes", Text)


class WorkOrderTask(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "work_order_tasks"
    __table_args__ = (
        UniqueConstraint("work_order_id", "task_sequence", name="uq_work_order_tasks"),
        {"schema": "incident"},
    )

    work_order_id: Mapped[UUID] = mapped_column(ForeignKey("incident.work_orders.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    description: Mapped[str] = mapped_column("task_description", Text, nullable=False)
    task_sequence: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    assigned_to: Mapped[UUID | None] = mapped_column(ForeignKey("security.users.id", ondelete="SET NULL", onupdate="RESTRICT"))


class IncidentAttachment(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "incident_attachments"
    __table_args__ = ({"schema": "incident"},)

    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incident.incidents.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    attachment_id: Mapped[UUID] = mapped_column(ForeignKey("common.attachments.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    category: Mapped[str | None] = mapped_column("attachment_category", String(20))
