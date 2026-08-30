from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, time, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetFieldNote, AssetInstallation, AssetMovement, AssetRelationship, AssetReplacement, AssetSpecification, AssetTimelineEvent, RepairHistory
from app.models.infrastructure import Location, LocationPosition
from app.models.master import AssetModel, AssetStatus, AssetSubcategory, ManufacturerAssetScope, MovementType, SpecificationDefinition
from app.models.incident import Incident, WorkAction
from app.repositories.asset import (
    AssetInstallationRepository,
    AssetListFilters,
    AssetMovementRepository,
    AssetRepository,
    AssetSpecificationRepository,
)
from app.services.asset_lifecycle_service import AssetLifecycleService


class AssetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AssetRepository(session)

    async def _has_active_installation(self, asset_id: UUID) -> bool:
        query = select(AssetInstallation).where(
            AssetInstallation.asset_id == asset_id,
            AssetInstallation.current_flag.is_(True)
        )
        return (await self.session.execute(query)).scalars().first() is not None

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
        if specification_values:
            await self._validate_specifications(specification_values)
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

    async def _validate_specifications(self, specification_values: list[dict[str, Any]]) -> None:
        if not specification_values:
            return
        
        spec_def_ids = [s["specification_definition_id"] for s in specification_values]
        result = await self.session.execute(select(SpecificationDefinition).where(SpecificationDefinition.id.in_(spec_def_ids)))
        spec_defs = {s.id: s for s in result.scalars()}
        
        import re
        
        for spec_val in specification_values:
            def_id = spec_val["specification_definition_id"]
            spec_def = spec_defs.get(def_id)
            if not spec_def:
                raise ValueError(f"Specification definition {def_id} not found")
            
            # Required flag
            if spec_def.required_flag:
                if not any(spec_val.get(k) is not None for k in ["value_text", "value_number", "value_boolean", "value_date", "value_json"]):
                    raise ValueError(f"Specification {spec_def.name} is required")
            
            # Data type
            if spec_def.data_type == "TEXT" and spec_val.get("value_text") is not None:
                val = spec_val["value_text"]
                if hasattr(spec_def, "validation_regex") and getattr(spec_def, "validation_regex"):
                    if not re.match(getattr(spec_def, "validation_regex"), val):
                        raise ValueError(f"Specification {spec_def.name} does not match required format")
            
            if spec_def.data_type == "NUMBER" and spec_val.get("value_number") is not None:
                val = spec_val["value_number"]
                if hasattr(spec_def, "min_value") and getattr(spec_def, "min_value") is not None and val < getattr(spec_def, "min_value"):
                    raise ValueError(f"Specification {spec_def.name} must be >= {getattr(spec_def, 'min_value')}")
                if hasattr(spec_def, "max_value") and getattr(spec_def, "max_value") is not None and val > getattr(spec_def, "max_value"):
                    raise ValueError(f"Specification {spec_def.name} must be <= {getattr(spec_def, 'max_value')}")

    async def apply_asset_action(self, incident_id: UUID, values: dict[str, Any], user_id: UUID | None) -> Asset:
        if not user_id:
            raise ValueError("user_id is required for asset actions")
        incident = await self.session.get(Incident, incident_id)
        if not incident:
            raise ValueError("Incident not found")
        if incident.incident_status_id is None:
            raise ValueError("Incident has no status")
        asset = await self.session.get(Asset, values["asset_id"])
        if not asset or asset.project_id != incident.project_id:
            raise ValueError("Asset does not belong to the incident project")
        action = values["action"].upper()
        reason = values["reason"].strip()
        if not reason:
            raise ValueError("A reason is required")

        lifecycle = AssetLifecycleService(self.session)
        formatted_reason = f"Work Request {incident.work_request_number}: {reason}"

        if action == "CHANGE_STATUS":
            if values.get("status_id") is None:
                raise ValueError("status_id is required for CHANGE_STATUS")
            await lifecycle.change_status(asset.id, values["status_id"], user_id, incident_id, formatted_reason)
        elif action == "MOVE":
            if values.get("location_id") is None:
                raise ValueError("location_id is required for MOVE")
            await lifecycle.move_asset(asset.id, values["location_id"], user_id, incident_id, formatted_reason)
        elif action == "INSTALL":
            if values.get("location_position_id") is None:
                raise ValueError("location_position_id is required for INSTALL")
            await lifecycle.install_asset(asset.id, values["location_position_id"], user_id, incident_id, formatted_reason)
        elif action in ("UNINSTALL", "UNINSTALLED"):
            if values.get("location_id") is None:
                raise ValueError("location_id (Store) is required for UNINSTALL")
            await lifecycle.uninstall_asset(asset.id, values["location_id"], user_id, incident_id, formatted_reason)
        elif action == "SEND_FOR_REPAIR":
            await lifecycle.dispatch_for_repair(asset.id, values.get("vendor_id"), values.get("courier_number"), date.today(), formatted_reason, user_id, incident_id)
        elif action == "RETURN_FROM_REPAIR":
            if values.get("location_id") is None:
                raise ValueError("location_id (Store) is required to RETURN_FROM_REPAIR")
            await lifecycle.receive_from_repair(asset.id, values["location_id"], date.today(), None, values.get("repair_remarks") or formatted_reason, values.get("status_code"), user_id, incident_id)
        else:
            raise ValueError("Unsupported asset action")

        await self.session.flush()
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
        if faulty.id == spare.id or await self._has_active_installation(spare.id):
            raise ValueError("Select a different asset that is not currently installed")
        if spare.project_id != faulty.project_id:
            raise ValueError("Replacement asset must belong to the same project")

        installation = await self.session.scalar(select(AssetInstallation).where(AssetInstallation.asset_id == asset_id, AssetInstallation.current_flag.is_(True)))
        if not installation:
            raise ValueError("Faulty asset has no current installation to transfer")

        location_position_id = installation.location_position_id
        replacement_date = values["replacement_date"]
        destination = values.get("faulty_destination_location_id")
        if not destination:
            raise ValueError("Faulty asset destination is required for replacement")

        # 1. Uninstall faulty
        await self.uninstall_asset(faulty.id, {
            "to_location_id": destination,
            "removed_on": replacement_date,
            "remarks": f"Uninstalled for replacement by {spare.asset_number}: {values['reason']}"
        })

        # 2. Move spare to the position's location
        pos = await self.session.get(LocationPosition, location_position_id)
        if pos and pos.location_id != spare.current_location_id:
            await self.create_asset_movement(spare.id, {
                "to_location_id": pos.location_id,
                "remarks": f"Moved to replace {faulty.asset_number}"
            })

        # 3. Install spare
        await self.create_asset_installation(spare.id, {
            "location_position_id": location_position_id,
            "installed_on": replacement_date,
            "remarks": f"Installed in place of {faulty.asset_number}: {values['reason']}"
        })

        # 4. Repair (optional)
        if values.get("dispatch_for_repair"):
            await self.dispatch_asset_for_repair(faulty.id, {
                "fault_date": replacement_date,
                "fault_description": values["reason"],
                "removal_date": replacement_date,
                "repair_remarks": values.get("remarks")
            }, user_id)

        replacement = AssetReplacement(
            old_asset_id=faulty.id,
            new_asset_id=spare.id,
            replacement_date=replacement_date,
            engineer_id=user_id,
            reason=values["reason"],
            remarks=values.get("remarks")
        )
        self.session.add(replacement)
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
            await self._validate_specifications(specification_values)
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
        raise ValueError("Direct asset installation is not allowed. All installations must be performed through a Work Request.")

    async def uninstall_asset(self, asset_id: UUID, values: dict[str, Any] | None = None) -> AssetInstallation | None:
        raise ValueError("Direct asset uninstallation is not allowed. All uninstallations must be performed through a Work Request.")

    async def list_asset_movements(self, asset_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[AssetMovement], int]:
        repo = AssetMovementRepository(self.session)
        items = await repo.list_by_asset(asset_id, offset=offset, limit=limit)
        return items, await repo.count_by_asset(asset_id)

    async def create_asset_movement(self, asset_id: UUID, values: dict[str, Any]) -> AssetMovement:
        raise ValueError("Direct asset movement is not allowed. All movements must be performed through a Work Request.")

    async def transfer_asset(self, asset_id: UUID, values: dict[str, Any], user_id: UUID | None = None) -> Asset:
        from app.models.common import Project
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
        if await self._has_active_installation(asset_id):
            raise ValueError(
                "Asset is currently installed at a position. "
                "Uninstall the asset first before transferring it to another project."
            )
        old_project_id = asset.project_id
        new_project_id = values.get("project_id")
        if new_project_id:
            project = await self.session.get(Project, new_project_id)
            if not project:
                raise ValueError("Project not found")
            asset.project_id = new_project_id
        transfer_type = await self.session.scalar(select(MovementType).where(MovementType.code == "TRANSFER"))
        transfer_type_id = transfer_type.id if transfer_type else None
        self.session.add(AssetMovement(
            asset_id=asset_id,
            movement_type_id=transfer_type_id,
            from_location_id=asset.current_location_id,
            to_location_id=asset.current_location_id,
            remarks=values.get("remarks") or f"Transferred project from {old_project_id} to {new_project_id}",
            created_by=user_id,
            moved_at=datetime.now()
        ))
        self.session.add(AssetTimelineEvent(
            asset_id=asset_id,
            event_type="ASSET_TRANSFERRED",
            description=values.get("remarks") or f"Transferred project from {old_project_id} to {new_project_id}",
            metadata_json={
                "old_project_id": str(old_project_id),
                "new_project_id": str(new_project_id) if new_project_id else None
            },
            created_by=user_id
        ))
        await self.session.flush()
        return asset

    async def dispatch_asset_for_repair(self, asset_id: UUID, values: dict[str, Any], user_id: UUID) -> RepairHistory:
        # Directly call lifecycle service since dispatch is not tied to work requests
        lifecycle = AssetLifecycleService(self.session)
        return await lifecycle.dispatch_for_repair(
            asset_id=asset_id,
            vendor_id=values.get("vendor_id"),
            courier_number=values.get("courier_number"),
            fault_date=values.get("fault_date"),
            fault_description=values.get("fault_description"),
            user_id=user_id,
            dispatch_id=values.get("dispatch_id")
        )

    async def receive_asset_from_repair(self, asset_id: UUID, values: dict[str, Any], user_id: UUID) -> RepairHistory:
        lifecycle = AssetLifecycleService(self.session)
        return await lifecycle.receive_from_repair(
            asset_id=asset_id,
            to_location_id=values.get("to_location_id"),
            return_date=values.get("return_date"),
            repair_cost=values.get("repair_cost"),
            repair_remarks=values.get("repair_remarks"),
            status_code=values.get("status_code"),
            user_id=user_id,
            dispatch_id=values.get("dispatch_id")
        )
