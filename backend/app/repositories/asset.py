from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.asset import (
    Asset,
    AssetDocument,
    AssetInstallation,
    AssetMovement,
    AssetPhoto,
    AssetRelationship,
    AssetSpecification,
    ChecklistItem,
    MaintenanceChecklist,
    MaintenanceHistory,
    MaintenanceSchedule,
)
from app.models.common import Attachment, Project, Vendor
from app.models.infrastructure import Location, LocationPosition
from app.models.master import (
    AssetCategory,
    AssetCondition,
    AssetLifecycle,
    AssetModel,
    AssetStatus,
    AssetSubcategory,
    DocumentType,
    Manufacturer,
    MovementType,
    RelationshipType,
    SpecificationDefinition,
)


@dataclass(slots=True)
class AssetListFilters:
    project_id: UUID | None = None
    category_id: int | None = None
    subcategory_id: int | None = None
    manufacturer_id: int | None = None
    model_id: int | None = None
    status_id: int | None = None
    condition_id: int | None = None
    lifecycle_id: int | None = None
    location_id: UUID | None = None
    warranty_status: str | None = None


class AssetRepository:
    SORT_MAP = {
        "asset_number": Asset.asset_number,
        "category": AssetCategory.name,
        "manufacturer": Manufacturer.name,
        "status": AssetStatus.name,
        "purchase_date": Asset.purchase_date,
        "warranty_expiry": Asset.warranty_expiry,
        "created_at": Asset.created_at,
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_list_query(self) -> Any:
        return (
            select(
                Asset.id.label("id"),
                Asset.asset_number.label("asset_number"),
                AssetCategory.name.label("category"),
                AssetSubcategory.name.label("subcategory"),
                Manufacturer.name.label("manufacturer"),
                AssetModel.name.label("model"),
                Asset.serial_number.label("serial_number"),
                Asset.barcode.label("barcode"),
                AssetStatus.name.label("status"),
                AssetCondition.name.label("condition"),
                AssetLifecycle.name.label("lifecycle"),
                Location.name.label("current_location"),
                Asset.purchase_date.label("purchase_date"),
                Asset.warranty_expiry.label("warranty_expiry"),
                Asset.remarks.label("remarks"),
                Asset.created_at.label("created_at"),
                Asset.updated_at.label("updated_at"),
            )
            .select_from(Asset)
            .join(AssetCategory, AssetCategory.id == Asset.asset_category_id)
            .outerjoin(AssetSubcategory, AssetSubcategory.id == Asset.asset_subcategory_id)
            .outerjoin(Manufacturer, Manufacturer.id == Asset.manufacturer_id)
            .outerjoin(AssetModel, AssetModel.id == Asset.asset_model_id)
            .join(AssetStatus, AssetStatus.id == Asset.asset_status_id)
            .outerjoin(AssetCondition, AssetCondition.id == Asset.asset_condition_id)
            .outerjoin(AssetLifecycle, AssetLifecycle.id == Asset.asset_lifecycle_id)
            .outerjoin(Location, Location.id == Asset.current_location_id)
            .where(Asset.is_active.is_(True))
        )

    def _apply_filters(self, query: Any, filters: AssetListFilters, search: str | None) -> Any:
        conditions: list[Any] = []
        if filters.project_id:
            conditions.append(Asset.project_id == filters.project_id)
        if filters.category_id:
            conditions.append(Asset.asset_category_id == filters.category_id)
        if filters.subcategory_id:
            conditions.append(Asset.asset_subcategory_id == filters.subcategory_id)
        if filters.manufacturer_id:
            conditions.append(Asset.manufacturer_id == filters.manufacturer_id)
        if filters.model_id:
            conditions.append(Asset.asset_model_id == filters.model_id)
        if filters.status_id:
            conditions.append(Asset.asset_status_id == filters.status_id)
        if filters.condition_id:
            conditions.append(Asset.asset_condition_id == filters.condition_id)
        if filters.lifecycle_id:
            conditions.append(Asset.asset_lifecycle_id == filters.lifecycle_id)
        if filters.location_id:
            conditions.append(Asset.current_location_id == filters.location_id)
        if filters.warranty_status == "expiring_soon":
            conditions.append(
                and_(
                    Asset.warranty_expiry.is_not(None),
                    Asset.warranty_expiry >= date.today(),
                    Asset.warranty_expiry <= date.today() + timedelta(days=90),
                )
            )
        if filters.warranty_status == "expired":
            conditions.append(
                and_(
                    Asset.warranty_expiry.is_not(None),
                    Asset.warranty_expiry < date.today(),
                )
            )
        if filters.warranty_status == "active":
            conditions.append(
                and_(
                    Asset.warranty_expiry.is_not(None),
                    Asset.warranty_expiry >= date.today(),
                )
            )
        if search:
            term = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Asset.asset_number).like(term),
                    func.lower(func.coalesce(Asset.serial_number, "")).like(term),
                    func.lower(func.coalesce(Asset.barcode, "")).like(term),
                    func.lower(func.coalesce(Manufacturer.name, "")).like(term),
                    func.lower(func.coalesce(AssetModel.name, "")).like(term),
                    func.lower(AssetCategory.name).like(term),
                    func.lower(func.coalesce(Location.name, "")).like(term),
                    func.lower(AssetStatus.name).like(term),
                )
            )
        if conditions:
            query = query.where(and_(*conditions))
        return query

    async def list(
        self,
        *,
        page: int,
        page_size: int,
        sort: str | None,
        order: str,
        search: str | None,
        filters: AssetListFilters,
    ) -> tuple[list[dict[str, Any]], int]:
        query = self._apply_filters(self._base_list_query(), filters, search)
        count_query = select(func.count()).select_from(query.subquery())
        sort_column = self.SORT_MAP.get(sort or "", Asset.created_at)
        query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        rows = (await self.session.execute(query)).mappings().all()
        total = int((await self.session.execute(count_query)).scalar_one())
        return [dict(row) for row in rows], total

    async def export_rows(self, *, search: str | None, filters: AssetListFilters) -> list[dict[str, Any]]:
        query = self._apply_filters(self._base_list_query(), filters, search).order_by(Asset.asset_number.asc())
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def get_summary(self, *, search: str | None, filters: AssetListFilters) -> dict[str, int]:
        query = self._apply_filters(
            select(
                func.count().label("total_assets"),
                func.sum(case((AssetStatus.name == "Active", 1), else_=0)).label("active_assets"),
                func.sum(case((AssetStatus.name == "In Repair", 1), else_=0)).label("assets_in_repair"),
                func.sum(case((AssetStatus.name == "Retired", 1), else_=0)).label("retired_assets"),
                func.sum(
                    case(
                        (
                            and_(
                                Asset.warranty_expiry.is_not(None),
                                Asset.warranty_expiry >= date.today(),
                                Asset.warranty_expiry <= date.today() + timedelta(days=90),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("warranty_expiring_soon"),
            )
            .select_from(Asset)
            .join(AssetCategory, AssetCategory.id == Asset.asset_category_id)
            .outerjoin(AssetSubcategory, AssetSubcategory.id == Asset.asset_subcategory_id)
            .outerjoin(Manufacturer, Manufacturer.id == Asset.manufacturer_id)
            .outerjoin(AssetModel, AssetModel.id == Asset.asset_model_id)
            .join(AssetStatus, AssetStatus.id == Asset.asset_status_id)
            .outerjoin(AssetCondition, AssetCondition.id == Asset.asset_condition_id)
            .outerjoin(AssetLifecycle, AssetLifecycle.id == Asset.asset_lifecycle_id)
            .outerjoin(Location, Location.id == Asset.current_location_id)
            .where(Asset.is_active.is_(True)),
            filters,
            search,
        )
        row = (await self.session.execute(query)).mappings().one()
        return {key: int(value or 0) for key, value in dict(row).items()}

    async def get_by_id(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(select(Asset).where(Asset.id == asset_id, Asset.is_active.is_(True)))
        return result.scalar_one_or_none()

    async def create(self, entity: Asset) -> Asset:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: Asset, values: dict[str, Any]) -> Asset:
        for key, value in values.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def get_details(self, asset_id: UUID) -> dict[str, Any] | None:
        current_installation = (
            select(
                AssetInstallation.asset_id.label("asset_id"),
                AssetInstallation.location_position_id.label("position_id"),
                AssetInstallation.installed_on.label("installed_on"),
                AssetInstallation.removed_on.label("removed_on"),
                AssetInstallation.current_flag.label("current_flag"),
                AssetInstallation.installation_status.label("installation_status"),
                AssetInstallation.remarks.label("installation_remarks"),
            )
            .where(AssetInstallation.asset_id == asset_id, AssetInstallation.current_flag.is_(True))
            .order_by(AssetInstallation.installed_on.desc(), AssetInstallation.created_at.desc())
            .limit(1)
            .subquery()
        )
        details_query = (
            select(
                Asset.id.label("id"),
                Asset.project_id.label("project_id"),
                Project.project_name.label("project_name"),
                Project.project_code.label("project_code"),
                Asset.asset_number.label("asset_number"),
                Asset.asset_category_id.label("asset_category_id"),
                AssetCategory.code.label("category_code"),
                AssetCategory.name.label("category_name"),
                Asset.asset_subcategory_id.label("asset_subcategory_id"),
                AssetSubcategory.code.label("subcategory_code"),
                AssetSubcategory.name.label("subcategory_name"),
                Asset.manufacturer_id.label("manufacturer_id"),
                Manufacturer.code.label("manufacturer_code"),
                Manufacturer.name.label("manufacturer_name"),
                Asset.asset_model_id.label("asset_model_id"),
                AssetModel.code.label("model_code"),
                AssetModel.name.label("model_name"),
                Asset.serial_number.label("serial_number"),
                Asset.barcode.label("barcode"),
                Asset.qr_code.label("qr_code"),
                Asset.asset_status_id.label("asset_status_id"),
                AssetStatus.code.label("status_code"),
                AssetStatus.name.label("status_name"),
                Asset.asset_condition_id.label("asset_condition_id"),
                AssetCondition.code.label("condition_code"),
                AssetCondition.name.label("condition_name"),
                Asset.asset_lifecycle_id.label("asset_lifecycle_id"),
                AssetLifecycle.code.label("lifecycle_code"),
                AssetLifecycle.name.label("lifecycle_name"),
                Asset.current_location_id.label("current_location_id"),
                Location.code.label("current_location_code"),
                Location.name.label("current_location_name"),
                Asset.purchase_date.label("purchase_date"),
                Asset.warranty_expiry.label("warranty_expiry"),
                Asset.remarks.label("remarks"),
                Asset.created_at.label("created_at"),
                Asset.updated_at.label("updated_at"),
                current_installation.c.position_id.label("installation_position_id"),
                current_installation.c.installed_on.label("installation_date"),
                current_installation.c.removed_on.label("installation_removed_on"),
                current_installation.c.current_flag.label("installation_current_flag"),
                current_installation.c.installation_status.label("installation_status"),
                current_installation.c.installation_remarks.label("installation_remarks"),
                LocationPosition.position_number.label("installation_position_name"),
                LocationPosition.power_source.label("position_power_source"),
                LocationPosition.electrical_panel.label("position_electrical_panel"),
                LocationPosition.network_switch.label("position_network_switch"),
                LocationPosition.switch_port.label("position_switch_port"),
                LocationPosition.patch_panel.label("position_patch_panel"),
                LocationPosition.junction_box.label("position_junction_box"),
                LocationPosition.mounting_details.label("position_mounting_details"),
                LocationPosition.infrastructure_details.label("position_infrastructure_details"),
            )
            .select_from(Asset)
            .join(Project, Project.id == Asset.project_id)
            .join(AssetCategory, AssetCategory.id == Asset.asset_category_id)
            .outerjoin(AssetSubcategory, AssetSubcategory.id == Asset.asset_subcategory_id)
            .outerjoin(Manufacturer, Manufacturer.id == Asset.manufacturer_id)
            .outerjoin(AssetModel, AssetModel.id == Asset.asset_model_id)
            .join(AssetStatus, AssetStatus.id == Asset.asset_status_id)
            .outerjoin(AssetCondition, AssetCondition.id == Asset.asset_condition_id)
            .outerjoin(AssetLifecycle, AssetLifecycle.id == Asset.asset_lifecycle_id)
            .outerjoin(Location, Location.id == Asset.current_location_id)
            .outerjoin(current_installation, current_installation.c.asset_id == Asset.id)
            .outerjoin(LocationPosition, LocationPosition.id == current_installation.c.position_id)
            .where(Asset.id == asset_id, Asset.is_active.is_(True))
        )
        details = (await self.session.execute(details_query)).mappings().first()
        if not details:
            return None
        return dict(details)

    async def list_replacement_candidates(self, asset_id: UUID, search: str, limit: int = 25) -> list[dict[str, Any]]:
        faulty = await self.session.scalar(select(Asset).where(Asset.id == asset_id))
        if not faulty:
            return []
        query = (
            select(
                Asset.id.label("id"),
                Asset.asset_number.label("asset_number"),
                Asset.serial_number.label("serial_number"),
                Asset.barcode.label("barcode"),
                Asset.qr_code.label("qr_code"),
                Asset.asset_role.label("asset_role"),
                AssetStatus.name.label("status"),
                Location.name.label("current_location"),
            )
            .select_from(Asset)
            .join(AssetStatus, AssetStatus.id == Asset.asset_status_id)
            .outerjoin(Location, Location.id == Asset.current_location_id)
            .where(
                Asset.project_id == faulty.project_id,
                Asset.id != asset_id,
                Asset.is_active.is_(True),
                Asset.asset_role == "SPARE",
            )
            .order_by(Asset.asset_number.asc())
            .limit(limit)
        )
        term = search.strip().lower()
        if term:
            pattern = f"%{term}%"
            query = query.where(or_(
                func.lower(Asset.asset_number).like(pattern),
                func.lower(func.coalesce(Asset.serial_number, "")).like(pattern),
                func.lower(func.coalesce(Asset.barcode, "")).like(pattern),
                func.lower(func.coalesce(Asset.qr_code, "")).like(pattern),
            ))
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def list_specification_definitions(
        self,
        *,
        category_id: int | None,
        subcategory_id: int | None,
    ) -> list[dict[str, Any]]:
        query = (
            select(
                SpecificationDefinition.id,
                SpecificationDefinition.code,
                SpecificationDefinition.name,
                SpecificationDefinition.data_type,
                SpecificationDefinition.unit_of_measure,
                SpecificationDefinition.required_flag,
                SpecificationDefinition.display_order,
            )
            .where(
                or_(
                    SpecificationDefinition.asset_category_id.is_(None),
                    SpecificationDefinition.asset_category_id == category_id,
                )
            )
            .order_by(SpecificationDefinition.display_order.asc(), SpecificationDefinition.name.asc())
        )
        if subcategory_id:
            query = query.where(
                or_(
                    SpecificationDefinition.asset_subcategory_id.is_(None),
                    SpecificationDefinition.asset_subcategory_id == subcategory_id,
                )
            )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def list_specifications(self, asset_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                AssetSpecification.id.label("id"),
                AssetSpecification.specification_definition_id.label("specification_definition_id"),
                SpecificationDefinition.name.label("specification_name"),
                SpecificationDefinition.code.label("code"),
                SpecificationDefinition.data_type.label("data_type"),
                SpecificationDefinition.unit_of_measure.label("unit"),
                AssetSpecification.value_text.label("value_text"),
                AssetSpecification.value_number.label("value_number"),
                AssetSpecification.value_boolean.label("value_boolean"),
                AssetSpecification.value_date.label("value_date"),
                AssetSpecification.value_json.label("value_json"),
                AssetSpecification.created_at.label("created_at"),
                AssetSpecification.updated_at.label("updated_at"),
            )
            .join(
                SpecificationDefinition,
                SpecificationDefinition.id == AssetSpecification.specification_definition_id,
            )
            .where(AssetSpecification.asset_id == asset_id)
            .order_by(SpecificationDefinition.display_order.asc(), SpecificationDefinition.name.asc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def upsert_specification_values(self, asset_id: UUID, values: list[dict[str, Any]]) -> None:
        existing_query = select(AssetSpecification).where(AssetSpecification.asset_id == asset_id)
        existing_rows = (await self.session.execute(existing_query)).scalars().all()
        by_definition = {row.specification_definition_id: row for row in existing_rows}
        seen_definition_ids: set[int] = set()
        _VALUE_FIELDS = ("value_text", "value_number", "value_boolean", "value_date", "value_json")
        for item in values:
            definition_id = item["specification_definition_id"]
            all_empty = all(item.get(f) is None for f in _VALUE_FIELDS)
            entity = by_definition.get(definition_id)
            if all_empty:
                if entity is not None:
                    await self.session.delete(entity)
                continue
            seen_definition_ids.add(definition_id)
            if entity is None:
                entity = AssetSpecification(asset_id=asset_id, **item)
                self.session.add(entity)
                continue
            entity.value_text = item.get("value_text")
            entity.value_number = item.get("value_number")
            entity.value_boolean = item.get("value_boolean")
            entity.value_date = item.get("value_date")
            entity.value_json = item.get("value_json")
        for definition_id, entity in by_definition.items():
            if definition_id not in seen_definition_ids:
                await self.session.delete(entity)
        await self.session.flush()

    async def upsert_installation(
        self,
        asset_id: UUID,
        *,
        location_position_id: UUID | None,
        installation_date: date | None,
    ) -> None:
        if location_position_id is None:
            return
        current_query = (
            select(AssetInstallation)
            .where(AssetInstallation.asset_id == asset_id, AssetInstallation.current_flag.is_(True))
            .order_by(AssetInstallation.created_at.desc())
        )
        current = (await self.session.execute(current_query)).scalars().first()
        if current and current.location_position_id == location_position_id and current.installed_on == installation_date:
            return
        if current:
            current.current_flag = False
            current.removed_on = installation_date
        self.session.add(
            AssetInstallation(
                asset_id=asset_id,
                location_position_id=location_position_id,
                installed_on=installation_date,
                current_flag=True,
            )
        )
        await self.session.flush()

    async def list_movements(self, asset_id: UUID) -> list[dict[str, Any]]:
        from_location = aliased(Location)
        to_location = aliased(Location)
        query = (
            select(
                AssetMovement.id.label("id"),
                MovementType.name.label("movement_type"),
                from_location.name.label("from_location"),
                to_location.name.label("to_location"),
                Vendor.vendor_name.label("vendor"),
                AssetMovement.moved_at.label("moved_at"),
                AssetMovement.remarks.label("remarks"),
            )
            .select_from(AssetMovement)
            .outerjoin(MovementType, MovementType.id == AssetMovement.movement_type_id)
            .outerjoin(from_location, from_location.id == AssetMovement.from_location_id)
            .outerjoin(to_location, to_location.id == AssetMovement.to_location_id)
            .outerjoin(Vendor, Vendor.id == AssetMovement.vendor_id)
            .where(AssetMovement.asset_id == asset_id)
            .order_by(AssetMovement.moved_at.desc(), AssetMovement.created_at.desc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def list_all_movements(self, search: str = "", offset: int = 0, limit: int = 50) -> tuple[list[dict[str, Any]], int]:
        from_location = aliased(Location)
        to_location = aliased(Location)
        query = select(
            AssetMovement.id.label("id"), AssetMovement.asset_id.label("asset_id"), Asset.asset_number.label("asset_number"),
            MovementType.name.label("movement_type"), from_location.name.label("from_location"), to_location.name.label("to_location"),
            Vendor.vendor_name.label("vendor"), AssetMovement.moved_at.label("moved_at"), AssetMovement.remarks.label("remarks"),
        ).select_from(AssetMovement).join(Asset, Asset.id == AssetMovement.asset_id).outerjoin(MovementType, MovementType.id == AssetMovement.movement_type_id).outerjoin(from_location, from_location.id == AssetMovement.from_location_id).outerjoin(to_location, to_location.id == AssetMovement.to_location_id).outerjoin(Vendor, Vendor.id == AssetMovement.vendor_id)
        term = search.strip().lower()
        if term:
            pattern = f"%{term}%"
            query = query.where(or_(func.lower(Asset.asset_number).like(pattern), func.lower(func.coalesce(MovementType.name, "")).like(pattern), func.lower(func.coalesce(from_location.name, "")).like(pattern), func.lower(func.coalesce(to_location.name, "")).like(pattern), func.lower(func.coalesce(AssetMovement.remarks, "")).like(pattern)))
        count = int((await self.session.execute(select(func.count()).select_from(query.subquery()))).scalar_one())
        rows = (await self.session.execute(query.order_by(AssetMovement.moved_at.desc()).offset(offset).limit(limit))).mappings().all()
        return [dict(row) for row in rows], count

    async def list_documents(self, asset_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                AssetDocument.id.label("id"),
                AssetDocument.attachment_id.label("attachment_id"),
                Attachment.file_name.label("file_name"),
                Attachment.file_path.label("file_path"),
                Attachment.mime_type.label("mime_type"),
                Attachment.file_size_bytes.label("file_size_bytes"),
                DocumentType.name.label("document_type"),
                AssetDocument.created_at.label("created_at"),
            )
            .join(Attachment, Attachment.id == AssetDocument.attachment_id)
            .outerjoin(DocumentType, DocumentType.id == Attachment.document_type_id)
            .where(AssetDocument.asset_id == asset_id)
            .order_by(AssetDocument.created_at.desc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def list_photos(self, asset_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                AssetPhoto.id.label("id"),
                AssetPhoto.attachment_id.label("attachment_id"),
                Attachment.file_name.label("file_name"),
                Attachment.file_path.label("file_path"),
                Attachment.mime_type.label("mime_type"),
                AssetPhoto.created_at.label("created_at"),
            )
            .join(Attachment, Attachment.id == AssetPhoto.attachment_id)
            .where(AssetPhoto.asset_id == asset_id)
            .order_by(AssetPhoto.created_at.desc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def list_relationships(self, asset_id: UUID) -> list[dict[str, Any]]:
        related_asset = aliased(Asset)
        incoming_asset = aliased(Asset)
        outgoing_query = (
            select(
                AssetRelationship.id.label("id"),
                AssetRelationship.related_asset_id.label("related_asset_id"),
                related_asset.asset_number.label("related_asset_number"),
                related_asset.asset_number.label("related_asset_name"),
                RelationshipType.name.label("relationship_type"),
                literal("outgoing").label("direction"),
            )
            .select_from(AssetRelationship)
            .join(related_asset, related_asset.id == AssetRelationship.related_asset_id)
            .outerjoin(RelationshipType, RelationshipType.id == AssetRelationship.relationship_type_id)
            .where(AssetRelationship.asset_id == asset_id)
        )
        incoming_query = (
            select(
                AssetRelationship.id.label("id"),
                AssetRelationship.asset_id.label("related_asset_id"),
                incoming_asset.asset_number.label("related_asset_number"),
                incoming_asset.asset_number.label("related_asset_name"),
                RelationshipType.name.label("relationship_type"),
                literal("incoming").label("direction"),
            )
            .select_from(AssetRelationship)
            .join(incoming_asset, incoming_asset.id == AssetRelationship.asset_id)
            .outerjoin(RelationshipType, RelationshipType.id == AssetRelationship.relationship_type_id)
            .where(AssetRelationship.related_asset_id == asset_id)
        )
        rows = (await self.session.execute(outgoing_query.union_all(incoming_query))).mappings().all()
        return [dict(row) for row in rows]

    async def list_maintenance_schedules(self, asset_id: UUID) -> list[dict[str, Any]]:
        last_maintenance = (
            select(
                MaintenanceHistory.schedule_id.label("schedule_id"),
                func.max(MaintenanceHistory.performed_on).label("last_maintenance"),
            )
            .group_by(MaintenanceHistory.schedule_id)
            .subquery()
        )
        query = (
            select(
                MaintenanceSchedule.id.label("id"),
                MaintenanceSchedule.checklist_id.label("checklist_id"),
                MaintenanceChecklist.checklist_name.label("checklist_name"),
                MaintenanceSchedule.next_due_date.label("next_due_date"),
                MaintenanceSchedule.frequency_days.label("frequency_days"),
                MaintenanceSchedule.is_active.label("is_active"),
                last_maintenance.c.last_maintenance.label("last_maintenance"),
            )
            .select_from(MaintenanceSchedule)
            .join(MaintenanceChecklist, MaintenanceChecklist.id == MaintenanceSchedule.checklist_id)
            .outerjoin(last_maintenance, last_maintenance.c.schedule_id == MaintenanceSchedule.id)
            .where(MaintenanceSchedule.asset_id == asset_id)
            .order_by(MaintenanceSchedule.next_due_date.asc().nullslast())
        )
        rows = (await self.session.execute(query)).mappings().all()
        schedule_rows = [dict(row) for row in rows]
        if not schedule_rows:
            return []
        checklist_ids = [row["checklist_id"] for row in schedule_rows]
        item_rows = (
            await self.session.execute(
                select(
                    ChecklistItem.id.label("id"),
                    ChecklistItem.checklist_id.label("checklist_id"),
                    ChecklistItem.task_description.label("task_description"),
                    ChecklistItem.sequence_order.label("sequence_order"),
                    ChecklistItem.is_required.label("is_required"),
                )
                .where(ChecklistItem.checklist_id.in_(checklist_ids))
                .order_by(ChecklistItem.sequence_order.asc(), ChecklistItem.created_at.asc())
            )
        ).mappings().all()
        items_by_checklist: dict[UUID, list[dict[str, Any]]] = {}
        for row in item_rows:
            row_dict = dict(row)
            items_by_checklist.setdefault(row_dict["checklist_id"], []).append(row_dict)
        for schedule in schedule_rows:
            schedule["tasks"] = items_by_checklist.get(schedule["checklist_id"], [])
        return schedule_rows

    async def list_maintenance_history(self, asset_id: UUID) -> list[dict[str, Any]]:
        query = (
            select(
                MaintenanceHistory.id.label("id"),
                MaintenanceHistory.schedule_id.label("schedule_id"),
                MaintenanceChecklist.checklist_name.label("checklist_name"),
                MaintenanceHistory.performed_on.label("performed_on"),
                literal(True).label("completed"),
                MaintenanceHistory.remarks.label("remarks"),
                MaintenanceHistory.performed_by.label("performed_by"),
            )
            .select_from(MaintenanceHistory)
            .join(MaintenanceSchedule, MaintenanceSchedule.id == MaintenanceHistory.schedule_id)
            .join(MaintenanceChecklist, MaintenanceChecklist.id == MaintenanceSchedule.checklist_id)
            .where(MaintenanceSchedule.asset_id == asset_id)
            .order_by(MaintenanceHistory.performed_on.desc().nullslast(), MaintenanceHistory.created_at.desc())
        )
        rows = (await self.session.execute(query)).mappings().all()
        return [dict(row) for row in rows]

    async def soft_delete(self, asset_id: UUID) -> bool:
        asset = await self.get_by_id(asset_id)
        if not asset:
            return False
        asset.is_active = False
        await self.session.flush()
        return True

    @staticmethod
    def to_csv(rows: list[dict[str, Any]]) -> str:
        import csv

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "Asset Number",
                "Category",
                "Subcategory",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Barcode",
                "Status",
                "Condition",
                "Lifecycle",
                "Current Location",
                "Purchase Date",
                "Warranty Expiry",
                "Remarks",
                "Created Date",
                "Updated Date",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["asset_number"],
                    row["category"],
                    row["subcategory"],
                    row["manufacturer"],
                    row["model"],
                    row["serial_number"],
                    row["barcode"],
                    row["status"],
                    row["condition"],
                    row["lifecycle"],
                    row["current_location"],
                    row["purchase_date"],
                    row["warranty_expiry"],
                    row["remarks"],
                    row["created_at"],
                    row["updated_at"],
                ]
            )
        return output.getvalue()


class AssetSpecificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_asset(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(AssetSpecification).where(AssetSpecification.asset_id == asset_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_asset(self, asset_id: UUID) -> int:
        result = await self.session.execute(select(func.count()).select_from(AssetSpecification).where(AssetSpecification.asset_id == asset_id))
        return int(result.scalar_one())

    async def create(self, entity: AssetSpecification) -> AssetSpecification:
        self.session.add(entity)
        await self.session.flush()
        return entity


class AssetInstallationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_asset(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(AssetInstallation).where(AssetInstallation.asset_id == asset_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_asset(self, asset_id: UUID) -> int:
        result = await self.session.execute(select(func.count()).select_from(AssetInstallation).where(AssetInstallation.asset_id == asset_id))
        return int(result.scalar_one())

    async def create(self, entity: AssetInstallation) -> AssetInstallation:
        self.session.add(entity)
        await self.session.flush()
        return entity


class AssetMovementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_asset(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(AssetMovement).where(AssetMovement.asset_id == asset_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_asset(self, asset_id: UUID) -> int:
        result = await self.session.execute(select(func.count()).select_from(AssetMovement).where(AssetMovement.asset_id == asset_id))
        return int(result.scalar_one())

    async def create(self, entity: AssetMovement) -> AssetMovement:
        self.session.add(entity)
        await self.session.flush()
        return entity
