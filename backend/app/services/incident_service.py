from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func

from app.models.incident import Incident, IncidentAttachment, IncidentUpdate
from app.models.asset import Asset, AssetInstallation, AssetMovement, AssetTimelineEvent, RepairHistory

from app.models.infrastructure import Location
from app.models.master import AssetStatus, IncidentStatus, MovementType
from app.repositories.incident import (
    IncidentAttachmentRepository,
    IncidentRepository,
    IncidentUpdateRepository,
)


class IncidentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_incident(self, incident_id: UUID) -> Incident | None:
        repo = IncidentRepository(Incident, self.session)
        return await repo.get_by_id(incident_id)

    async def list_incidents(self, offset: int = 0, limit: int = 100, search: str | None = None) -> tuple[list[Incident], int]:
        repo = IncidentRepository(Incident, self.session)
        items = await repo.list(offset=offset, limit=limit, search=search)
        return items, await repo.count(search=search)

    async def create_incident(self, values: dict[str, Any]) -> Incident:
        asset_id = values.get("asset_id")
        location_id = values.get("location_id")
        project_id = values["project_id"]
        if asset_id:
            asset = await self.session.get(Asset, asset_id)
            if not asset or asset.project_id != project_id:
                raise ValueError("Affected asset does not belong to the selected project")
        if location_id:
            location = await self.session.get(Location, location_id)
            if not location or location.project_id != project_id:
                raise ValueError("Affected location does not belong to the selected project")
        values["incident_number"] = values.get("incident_number") or await self.session.scalar(text("SELECT common.generate_business_number('INCIDENT')"))
        values.setdefault("reported_at", datetime.now())
        entity = Incident(**values)
        repo = IncidentRepository(Incident, self.session)
        return await repo.create(entity)

    async def update_incident(self, incident_id: UUID, values: dict[str, Any], user_id: UUID | None = None) -> Incident | None:
        repo = IncidentRepository(Incident, self.session)
        incident = await repo.get_by_id(incident_id)
        if not incident:
            return None
        status_id = values.get("incident_status_id")
        if status_id:
            status = await self.session.scalar(select(IncidentStatus).where(IncidentStatus.id == status_id))
            if status and status.code in ("CLOSED", "RESOLVED"):
                values["closed_date"] = values.get("closed_date") or datetime.now()
                values["closed_by"] = values.get("closed_by") or user_id
        return await repo.update(incident, values)

    async def list_incident_updates(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[IncidentUpdate], int]:
        repo = IncidentUpdateRepository(IncidentUpdate, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_incident_update(self, incident_id: UUID, values: dict[str, Any], user_id: UUID | None = None) -> IncidentUpdate:
        incident = await self.get_incident(incident_id)
        if not incident:
            raise ValueError("Incident not found")
        values["incident_id"] = incident_id
        values["update_at"] = values.get("update_at") or datetime.now()
        entity = IncidentUpdate(**values)
        repo = IncidentUpdateRepository(IncidentUpdate, self.session)
        update = await repo.create(entity)
        if values.get("status_after_update_id"):
            incident.incident_status_id = values["status_after_update_id"]
            status = await self.session.scalar(select(IncidentStatus).where(IncidentStatus.id == values["status_after_update_id"]))
            if status and status.code in ("CLOSED", "RESOLVED"):
                incident.closed_date = datetime.now()
                incident.closed_by = user_id
                incident.resolution_remarks = values.get("update_notes")
        return update

    async def list_incident_attachments(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[IncidentAttachment], int]:
        repo = IncidentAttachmentRepository(IncidentAttachment, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_incident_attachment(self, incident_id: UUID, values: dict[str, Any]) -> IncidentAttachment:
        values["incident_id"] = incident_id
        entity = IncidentAttachment(**values)
        repo = IncidentAttachmentRepository(IncidentAttachment, self.session)
        return await repo.create(entity)

    async def apply_asset_action(self, incident_id: UUID, values: dict[str, Any], user_id: UUID | None) -> Asset:
        incident = await self.get_incident(incident_id)
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
        old_location = asset.current_location_id
        old_status = asset.asset_status_id
        formatted_reason = f"Incident {incident.incident_number}: {reason}"
        if action == "CHANGE_STATUS":
            if values.get("status_id") is None:
                raise ValueError("status_id is required for CHANGE_STATUS")
            asset.asset_status_id = values["status_id"]
        elif action == "MOVE":
            if asset.asset_role == "INSTALLED":
                raise ValueError(
                    "Asset is currently installed at a position. "
                    "Use the UNINSTALL action first before moving it."
                )
            destination = await self.session.scalar(select(Location).where(Location.id == values.get("location_id"), Location.project_id == incident.project_id))
            if not destination:
                raise ValueError("A valid destination location is required")
            # Close current installation record
            current_install = await self.session.scalar(
                select(AssetInstallation)
                .where(AssetInstallation.asset_id == asset.id, AssetInstallation.current_flag.is_(True))
                .order_by(AssetInstallation.created_at.desc())
            )
            if current_install:
                current_install.current_flag = False
                current_install.removed_on = date.today()
                current_install.installation_status = "REMOVED"
                current_install.removed_by = user_id
            asset.current_location_id = destination.id
            movement_type = await self.session.scalar(select(MovementType).where(MovementType.code == "TRANSFER"))
            if not movement_type:
                raise ValueError("TRANSFER movement type is not configured")
            self.session.add(AssetMovement(asset_id=asset.id, movement_type_id=movement_type.id, from_location_id=old_location, to_location_id=destination.id, moved_at=datetime.now(), remarks=formatted_reason, created_by=user_id))
        elif action in ("UNINSTALL", "UNINSTALLED"):
            current_install = await self.session.scalar(
                select(AssetInstallation)
                .where(AssetInstallation.asset_id == asset.id, AssetInstallation.current_flag.is_(True))
                .order_by(AssetInstallation.created_at.desc())
            )
            if not current_install:
                raise ValueError("Asset has no active installation to uninstall")
            current_install.current_flag = False
            current_install.removed_on = date.today()
            current_install.installation_status = "UNINSTALLED"
            current_install.remarks = formatted_reason
            current_install.removed_by = user_id
            asset.current_location_id = None
            asset.asset_role = "SPARE"
        elif action == "SEND_FOR_REPAIR":
            if asset.asset_role == "INSTALLED":
                raise ValueError(
                    "Asset is currently installed at a position. "
                    "Uninstall the asset first before sending it for repair."
                )
            repair_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "UNDER_REPAIR"))
            if not repair_status:
                raise ValueError("UNDER_REPAIR status is not configured")
            # Close current installation — asset is leaving the site
            current_install = await self.session.scalar(
                select(AssetInstallation)
                .where(AssetInstallation.asset_id == asset.id, AssetInstallation.current_flag.is_(True))
                .order_by(AssetInstallation.created_at.desc())
            )
            if current_install:
                current_install.current_flag = False
                current_install.removed_on = date.today()
                current_install.installation_status = "UNDER_REPAIR"
                current_install.removed_by = user_id
            asset.asset_status_id = repair_status.id
            asset.current_location_id = None  # no longer at a tracked location
            self.session.add(RepairHistory(asset_id=asset.id, fault_date=date.today(), fault_description=formatted_reason, removed_from_location_id=old_location, removal_date=date.today(), created_by=user_id))
        elif action == "RETURN_FROM_REPAIR":
            # Fetch the latest open RepairHistory for this asset (no return_date yet)
            repair = await self.session.scalar(
                select(RepairHistory)
                .where(RepairHistory.asset_id == asset.id, RepairHistory.return_date.is_(None))
                .order_by(RepairHistory.fault_date.desc())
            )
            if repair:
                repair.return_date = date.today()
                repair.repair_remarks = values.get("repair_remarks") or formatted_reason
            # Restore asset to ACTIVE status (fall back to SPARE if not found)
            active_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "ACTIVE"))
            if not active_status:
                active_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "SPARE"))
            if not active_status:
                raise ValueError("Neither ACTIVE nor SPARE asset status is configured")
            asset.asset_status_id = active_status.id
            # Return the asset to the location it was removed from (if recorded)
            if repair and repair.removed_from_location_id:
                asset.current_location_id = repair.removed_from_location_id
        else:
            raise ValueError("Unsupported asset action")
        self.session.add(AssetTimelineEvent(asset_id=asset.id, event_type=f"INCIDENT_{action}", description=formatted_reason, metadata_json={"incident_id": str(incident_id), "action": action, "old_location_id": str(old_location) if old_location else None, "old_status_id": old_status, "new_status_id": asset.asset_status_id, "new_location_id": str(asset.current_location_id) if asset.current_location_id else None}, created_by=user_id))
        await self.session.flush()
        return asset
