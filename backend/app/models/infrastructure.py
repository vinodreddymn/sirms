from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import AuditMixin, Base, UUIDPrimaryKeyMixin


class Location(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "locations"
    __table_args__ = (
        UniqueConstraint("project_id", "code", name="uq_locations_project_code"),
        {"schema": "infrastructure"},
    )

    project_id: Mapped[UUID] = mapped_column(ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    parent_location_id: Mapped[UUID | None] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="CASCADE", onupdate="RESTRICT"))
    location_template_node_id: Mapped[int | None] = mapped_column(ForeignKey("master.location_template_nodes.id", ondelete="SET NULL", onupdate="RESTRICT"))
    location_type_id: Mapped[int] = mapped_column(ForeignKey("master.location_types.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    elevation_meters: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    geo_json: Mapped[dict | None] = mapped_column(JSONB)
    remarks: Mapped[str | None] = mapped_column(Text)


class LocationPosition(UUIDPrimaryKeyMixin, AuditMixin, Base):
    __tablename__ = "location_positions"
    __table_args__ = (
        UniqueConstraint("location_id", "position_type_id", "position_number", name="uq_location_positions"),
        {"schema": "infrastructure"},
    )

    location_id: Mapped[UUID] = mapped_column(ForeignKey("infrastructure.locations.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False)
    position_template_node_id: Mapped[int | None] = mapped_column(ForeignKey("master.position_template_nodes.id", ondelete="SET NULL", onupdate="RESTRICT"))
    position_type_id: Mapped[int] = mapped_column(ForeignKey("master.position_types.id", ondelete="RESTRICT", onupdate="RESTRICT"), nullable=False)
    position_number: Mapped[str] = mapped_column(String(50), nullable=False)
    maximum_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    remarks: Mapped[str | None] = mapped_column(Text)
