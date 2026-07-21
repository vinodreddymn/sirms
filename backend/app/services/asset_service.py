from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, time, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetFieldNote, AssetInstallation, AssetMovement, AssetRelationship, AssetReplacement, AssetSpecification, AssetTimelineEvent, RepairHistory
from app.models.infrastructure import Location, LocationPosition
from app.models.master import AssetModel, AssetStatus, AssetSubcategory, ManufacturerAssetScope, MovementType
from app.repositories.asset import (
    AssetInstallationRepository,
    AssetListFilters,
    AssetMovementRepository,
    AssetRepository,
    AssetSpecificationRepository,
)


class AssetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AssetRepository(session)

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        return await self.repo.get_by_id(asset_id)

    async def get_asset_details(self, asset_id: UUID) -> dict[str, Any] | None:
        details = await self.repo.get_details(asset_id)
        if not details:
            return None
        details["specifications"] = await self.repo.list_specifications(asset_id)
        details["movement_history"] = await self.repo.list_movements(asset_id)
        details["documents"] = await self.repo.list_documents(asset_id)
        details["photos"] = await self.repo.list_photos(asset_id)
        details["relationships"] = await self.repo.list_relationships(asset_id)
        details["maintenance_schedules"] = await self.repo.list_maintenance_schedules(asset_id)
        details["maintenance_history"] = await self.repo.list_maintenance_history(asset_id)
        return details

    async def list_replacement_candidates(self, asset_id: UUID, search: str) -> list[dict[str, Any]]:
        return await self.repo.list_replacement_candidates(asset_id, search)

    async def list_all_movements(self, search: str, offset: int, limit: int) -> tuple[list[dict[str, Any]], int]:
        return await self.repo.list_all_movements(search, offset, limit)

    async def list_assets(
        self,
        *,
        page: int,
        page_size: int,
        sort: str | None,
        order: str,
        search: str | None,
        filters: AssetListFilters,
    ) -> tuple[list[dict[str, Any]], int]:
        return await self.repo.list(
            page=page,
            page_size=page_size,
            sort=sort,
            order=order,
            search=search,
            filters=filters,
        )

    async def get_asset_summary(self, *, search: str | None, filters: AssetListFilters) -> dict[str, int]:
        normalized_filters = AssetListFilters(**asdict(filters))
        if normalized_filters.warranty_status == "expiring_soon":
            normalized_filters.warranty_status = "active"
        summary = await self.repo.get_summary(search=search, filters=normalized_filters)
        if filters.warranty_status in {None, "expiring_soon"}:
            export_rows = await self.repo.export_rows(search=search, filters=normalized_filters)
            threshold = date.today() + timedelta(days=90)
            summary["warranty_expiring_soon"] = sum(
                1
                for row in export_rows
                if row["warranty_expiry"] is not None and date.today() <= row["warranty_expiry"] <= threshold
            )
        return summary

    async def export_assets(self, *, search: str | None, filters: AssetListFilters) -> str:
        rows = await self.repo.export_rows(search=search, filters=filters)
        return self.repo.to_csv(rows)

    async def create_asset(self, values: dict[str, Any]) -> Asset:
        specification_values = values.pop("specification_values", [])
        relationship_ids = values.pop("relationship_ids", {})
        location_position_id = values.pop("location_position_id", None)
        installation_date = values.pop("installation_date", None)
        await self._validate_asset_lookup_relationships(values)
        if location_position_id:
            await self._validate_position_capacity(location_position_id)
        entity = Asset(**values)
        asset = await self.repo.create(entity)
        self.session.add(AssetTimelineEvent(asset_id=asset.id, event_type="ASSET_CREATED", description="Asset registered", created_by=None))
        if specification_values:
            await self.repo.upsert_specification_values(asset.id, specification_values)
        if location_position_id:
            await self.repo.upsert_installation(
                asset.id,
                location_position_id=location_position_id,
                installation_date=installation_date,
            )
        await self._save_relationships(asset.id, relationship_ids)
        return asset

    async def add_repair_history(self, asset_id: UUID, values: dict[str, Any], user_id: UUID) -> RepairHistory:
        if not await self.repo.get_by_id(asset_id):
            raise ValueError("Asset not found")
        repair = RepairHistory(asset_id=asset_id, created_by=user_id, **values)
        self.session.add(repair)
        self.session.add(AssetTimelineEvent(asset_id=asset_id, event_type="REPAIR_RECORDED", description=repair.fault_description, created_by=user_id))
        await self.session.flush()
        return repair

    async def add_field_note(self, asset_id: UUID, note: str, observed_at: Any, user_id: UUID) -> AssetFieldNote:
        if not await self.repo.get_by_id(asset_id):
            raise ValueError("Asset not found")
        field_note = AssetFieldNote(asset_id=asset_id, note=note, observed_at=observed_at, created_by=user_id) if observed_at else AssetFieldNote(asset_id=asset_id, note=note, created_by=user_id)
        self.session.add(field_note)
        self.session.add(AssetTimelineEvent(asset_id=asset_id, event_type="FIELD_NOTE", description=note, created_by=user_id))
        await self.session.flush()
        return field_note

    async def replace_asset(self, asset_id: UUID, values: dict[str, Any], user_id: UUID) -> AssetReplacement:
        faulty = await self.repo.get_by_id(asset_id)
        spare = await self.repo.get_by_id(values["spare_asset_id"])
        if not faulty or not spare:
            raise ValueError("Faulty or spare asset not found")
        if faulty.id == spare.id or spare.asset_role != "SPARE":
            raise ValueError("Select a different asset currently marked as SPARE")
        if spare.project_id != faulty.project_id:
            raise ValueError("Replacement asset must belong to the same project")
        installation = await self.session.scalar(select(AssetInstallation).where(AssetInstallation.asset_id == asset_id, AssetInstallation.current_flag.is_(True)))
        if not installation:
            raise ValueError("Faulty asset has no current installation to transfer")
        installed_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "INSTALLED"))
        repair_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "UNDER_REPAIR"))
        if not installed_status or not repair_status:
            raise ValueError("Operational status master data is missing INSTALLED or UNDER_REPAIR")
        replacement_date = values["replacement_date"]
        installation.current_flag = False
        installation.removed_on = replacement_date
        destination = values.get("faulty_destination_location_id")
        if destination:
            destination_location = await self.session.scalar(select(Location).where(Location.id == destination, Location.project_id == faulty.project_id))
            if not destination_location:
                raise ValueError("Faulty asset destination must belong to the same project")
        faulty_from_location = faulty.current_location_id
        spare_from_location = spare.current_location_id
        faulty.asset_role, faulty.asset_status_id, faulty.current_location_id = "SPARE", repair_status.id, destination
        spare.asset_role, spare.asset_status_id, spare.current_location_id = "INSTALLED", installed_status.id, faulty_from_location
        self.session.add(AssetInstallation(asset_id=spare.id, location_position_id=installation.location_position_id, installed_on=replacement_date, current_flag=True))
        self.session.add(RepairHistory(
            asset_id=faulty.id,
            fault_date=replacement_date,
            fault_description=values["reason"],
            removed_from_location_id=faulty_from_location,
            removal_date=replacement_date,
            replacement_asset_id=spare.id,
            repair_remarks=values.get("remarks"),
            created_by=user_id,
        ))
        movements = await self.session.execute(select(MovementType).where(MovementType.code.in_(["REPAIR", "TRANSFER"])))
        movement_types = {item.code: item.id for item in movements.scalars()}
        if not movement_types.get("REPAIR") or not movement_types.get("TRANSFER"):
            raise ValueError("Movement types REPAIR and TRANSFER are required for replacement")
        movement_at = datetime.combine(replacement_date, time.min)
        self.session.add_all([
            AssetMovement(asset_id=faulty.id, movement_type_id=movement_types["REPAIR"], from_location_id=faulty_from_location, to_location_id=destination, moved_at=movement_at, remarks=values["reason"]),
            AssetMovement(asset_id=spare.id, movement_type_id=movement_types["TRANSFER"], from_location_id=spare_from_location, to_location_id=faulty_from_location, moved_at=movement_at, remarks=values["reason"]),
        ])
        replacement = AssetReplacement(old_asset_id=faulty.id, new_asset_id=spare.id, replacement_date=replacement_date, engineer_id=user_id, reason=values["reason"], remarks=values.get("remarks"))
        self.session.add(replacement)
        self.session.add_all([
            AssetTimelineEvent(asset_id=faulty.id, event_type="REPLACED", description=f"Replaced by {spare.asset_number}: {values['reason']}", metadata_json={"replacement_asset_id": str(spare.id), "previous_location_id": str(faulty_from_location) if faulty_from_location else None}, created_by=user_id),
            AssetTimelineEvent(asset_id=spare.id, event_type="INSTALLED_AS_REPLACEMENT", description=f"Installed in place of {faulty.asset_number}: {values['reason']}", metadata_json={"replaced_asset_id": str(faulty.id), "location_id": str(faulty_from_location) if faulty_from_location else None}, created_by=user_id),
        ])
        await self.session.flush()
        return replacement

    async def list_timeline(self, asset_id: UUID) -> list[AssetTimelineEvent]:
        result = await self.session.execute(select(AssetTimelineEvent).where(AssetTimelineEvent.asset_id == asset_id).order_by(AssetTimelineEvent.event_at.desc()))
        return list(result.scalars())

    async def update_asset(self, asset_id: UUID, values: dict[str, Any]) -> Asset | None:
        specification_values = values.pop("specification_values", None)
        relationship_ids = values.pop("relationship_ids", None)
        location_position_id = values.pop("location_position_id", None)
        installation_date = values.pop("installation_date", None)
        asset = await self.repo.get_by_id(asset_id)
        if not asset:
            return None
        await self._validate_asset_lookup_relationships(
            {
                "asset_category_id": values.get("asset_category_id", asset.asset_category_id),
                "asset_subcategory_id": values.get("asset_subcategory_id", asset.asset_subcategory_id),
                "manufacturer_id": values.get("manufacturer_id", asset.manufacturer_id),
                "asset_model_id": values.get("asset_model_id", asset.asset_model_id),
            },
        )
        asset = await self.repo.update(asset, values)
        if specification_values is not None:
            await self.repo.upsert_specification_values(asset_id, specification_values)
        if location_position_id is not None:
            await self._validate_position_capacity(location_position_id, asset_id=asset.id)
            await self.repo.upsert_installation(
                asset.id,
                location_position_id=location_position_id,
                installation_date=installation_date,
            )
        if relationship_ids is not None:
            await self._replace_relationships(asset.id, relationship_ids)
        return asset

    async def _save_relationships(self, asset_id: UUID, relationship_ids: dict[str, list[UUID]]) -> None:
        relationship_types = await self._relationship_types()
        for relationship_code, related_ids in relationship_ids.items():
            relationship_type_id = relationship_types.get("PARENT_OF" if relationship_code == "CHILD_OF" else relationship_code)
            if relationship_type_id is None:
                raise ValueError(f"Unknown asset relationship type: {relationship_code}")
            for related_id in set(related_ids):
                if related_id == asset_id:
                    raise ValueError("An asset cannot be related to itself")
                if relationship_code == "PARENT_OF":
                    self.session.add(AssetRelationship(asset_id=related_id, related_asset_id=asset_id, relationship_type_id=relationship_type_id))
                else:
                    self.session.add(AssetRelationship(asset_id=asset_id, related_asset_id=related_id, relationship_type_id=relationship_type_id))
        await self.session.flush()

    async def _replace_relationships(self, asset_id: UUID, relationship_ids: dict[str, list[UUID]]) -> None:
        existing = (await self.session.execute(select(AssetRelationship).where(AssetRelationship.asset_id == asset_id))).scalars().all()
        for relationship in existing:
            await self.session.delete(relationship)
        await self.session.flush()
        await self._save_relationships(asset_id, relationship_ids)

    async def _relationship_types(self) -> dict[str, int]:
        from app.models.master import RelationshipType
        rows = (await self.session.execute(select(RelationshipType))).scalars().all()
        return {row.code: row.id for row in rows}

    async def _validate_asset_lookup_relationships(self, values: dict[str, Any]) -> None:
        subcategory_id = values.get("asset_subcategory_id")
        category_id = values.get("asset_category_id")
        if subcategory_id is not None:
            subcategory = await self.session.scalar(
                select(AssetSubcategory).where(AssetSubcategory.id == subcategory_id),
            )
            if not subcategory or subcategory.asset_category_id != category_id:
                raise ValueError("Selected subcategory does not belong to the selected category.")

        model_id = values.get("asset_model_id")
        manufacturer_id = values.get("manufacturer_id")
        if model_id is not None:
            model = await self.session.scalar(select(AssetModel).where(AssetModel.id == model_id))
            if not model or model.manufacturer_id != manufacturer_id:
                raise ValueError("Selected model does not belong to the selected manufacturer.")
            if model.asset_subcategory_id is not None and model.asset_subcategory_id != subcategory_id:
                raise ValueError("Selected model does not belong to the selected subcategory.")
        if manufacturer_id is not None and category_id is not None:
            scopes = (await self.session.execute(select(ManufacturerAssetScope).where(
                ManufacturerAssetScope.manufacturer_id == manufacturer_id,
                ManufacturerAssetScope.is_active.is_(True),
            ))).scalars().all()
            if scopes and not any(
                scope.asset_category_id == category_id and (scope.asset_subcategory_id is None or scope.asset_subcategory_id == subcategory_id)
                for scope in scopes
            ):
                raise ValueError("Selected manufacturer is not configured for the selected category or subcategory.")

    async def _validate_position_capacity(self, location_position_id: UUID, asset_id: UUID | None = None) -> None:
        position = await self.session.scalar(select(LocationPosition).where(LocationPosition.id == location_position_id))
        if not position:
            raise ValueError("Selected installation position was not found.")

        used_query = select(func.count()).select_from(AssetInstallation).where(
            AssetInstallation.location_position_id == location_position_id,
            AssetInstallation.current_flag.is_(True),
        )
        if asset_id is not None:
            used_query = used_query.where(AssetInstallation.asset_id != asset_id)

        used_count = await self.session.scalar(used_query)
        if (used_count or 0) >= position.maximum_capacity:
            raise ValueError("Selected installation position has reached its maximum asset capacity.")

    async def delete_asset(self, asset_id: UUID) -> bool:
        return await self.repo.soft_delete(asset_id)

    async def list_specification_definitions(
        self,
        *,
        category_id: int | None,
        subcategory_id: int | None,
    ) -> list[dict[str, Any]]:
        return await self.repo.list_specification_definitions(
            category_id=category_id,
            subcategory_id=subcategory_id,
        )

    async def list_asset_specifications(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[AssetSpecification], int]:
        repo = AssetSpecificationRepository(self.session)
        items = await repo.list_by_asset(asset_id, offset=offset, limit=limit)
        return items, await repo.count_by_asset(asset_id)

    async def create_asset_specification(self, asset_id: UUID, values: dict[str, Any]) -> AssetSpecification:
        values["asset_id"] = asset_id
        entity = AssetSpecification(**values)
        repo = AssetSpecificationRepository(self.session)
        return await repo.create(entity)

    async def list_asset_installations(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[AssetInstallation], int]:
        repo = AssetInstallationRepository(self.session)
        items = await repo.list_by_asset(asset_id, offset=offset, limit=limit)
        return items, await repo.count_by_asset(asset_id)

    async def create_asset_installation(self, asset_id: UUID, values: dict[str, Any]) -> AssetInstallation:
        values["asset_id"] = asset_id
        entity = AssetInstallation(**values)
        repo = AssetInstallationRepository(self.session)
        return await repo.create(entity)

    async def list_asset_movements(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[AssetMovement], int]:
        repo = AssetMovementRepository(self.session)
        items = await repo.list_by_asset(asset_id, offset=offset, limit=limit)
        return items, await repo.count_by_asset(asset_id)

    async def create_asset_movement(self, asset_id: UUID, values: dict[str, Any]) -> AssetMovement:
        values["asset_id"] = asset_id
        entity = AssetMovement(**values)
        repo = AssetMovementRepository(self.session)
        return await repo.create(entity)
