from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.incident import Incident, IncidentAttachment, IncidentUpdate, WorkOrder, WorkOrderTask
from app.models.asset import Asset, AssetMovement, AssetTimelineEvent, RepairHistory
from app.models.infrastructure import Location
from app.models.master import AssetStatus, IncidentStatus, MovementType, WorkOrderStatus
from app.repositories.incident import (
    IncidentAttachmentRepository,
    IncidentRepository,
    IncidentUpdateRepository,
    WorkOrderRepository,
    WorkOrderTaskRepository,
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

    async def update_incident(self, incident_id: UUID, values: dict[str, Any]) -> Incident | None:
        repo = IncidentRepository(Incident, self.session)
        incident = await repo.get_by_id(incident_id)
        if not incident:
            return None
        status_id = values.get("incident_status_id")
        if status_id:
            status = await self.session.scalar(select(IncidentStatus).where(IncidentStatus.id == status_id))
            if status and status.code == "CLOSED":
                values["closed_date"] = values.get("closed_date") or __import__("datetime").datetime.now()
        return await repo.update(incident, values)

    async def list_incident_updates(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[IncidentUpdate], int]:
        repo = IncidentUpdateRepository(IncidentUpdate, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_incident_update(self, incident_id: UUID, values: dict[str, Any]) -> IncidentUpdate:
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
            if status and status.code == "CLOSED":
                incident.closed_date = __import__("datetime").datetime.now()
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

    async def get_work_order(self, work_order_id: UUID) -> WorkOrder | None:
        repo = WorkOrderRepository(WorkOrder, self.session)
        return await repo.get_by_id(work_order_id)

    async def list_work_orders(self, offset: int = 0, limit: int = 100) -> tuple[list[WorkOrder], int]:
        repo = WorkOrderRepository(WorkOrder, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def list_work_orders_by_incident(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[WorkOrder], int]:
        repo = WorkOrderRepository(WorkOrder, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_work_order(self, values: dict[str, Any]) -> WorkOrder:
        incident_id = values.get("incident_id")
        if not incident_id:
            raise ValueError("Incident is required for a work order")
        incident = await self.get_incident(incident_id)
        if not incident:
            raise ValueError("Incident not found")
        repo = WorkOrderRepository(WorkOrder, self.session)
        existing_work_order = await repo.get_by_incident(incident_id)
        if existing_work_order:
            raise ValueError("A work order already exists for this incident")
        values["work_order_number"] = values.get("work_order_number") or await self.session.scalar(text("SELECT common.generate_business_number('WORK_ORDER')"))
        if values.get("status_id") is None:
            status = await self.session.scalar(select(WorkOrderStatus).where(WorkOrderStatus.code == "PLANNED"))
            values["status_id"] = status.id if status else None
        entity = WorkOrder(**values)
        return await repo.create(entity)

    async def update_work_order(self, work_order_id: UUID, values: dict[str, Any]) -> WorkOrder | None:
        repo = WorkOrderRepository(WorkOrder, self.session)
        work_order = await repo.get_by_id(work_order_id)
        if not work_order:
            return None
        return await repo.update(work_order, values)

    async def list_work_order_tasks(self, work_order_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[WorkOrderTask], int]:
        repo = WorkOrderTaskRepository(WorkOrderTask, self.session)
        items = await repo.list_by_work_order(work_order_id, offset=offset, limit=limit)
        return items, await repo.count_by_work_order(work_order_id)

    async def create_work_order_task(self, work_order_id: UUID, values: dict[str, Any]) -> WorkOrderTask:
        values["work_order_id"] = work_order_id
        entity = WorkOrderTask(**values)
        repo = WorkOrderTaskRepository(WorkOrderTask, self.session)
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
        if action == "CHANGE_STATUS":
            if values.get("status_id") is None:
                raise ValueError("status_id is required for CHANGE_STATUS")
            asset.asset_status_id = values["status_id"]
        elif action == "MOVE":
            destination = await self.session.scalar(select(Location).where(Location.id == values.get("location_id"), Location.project_id == incident.project_id))
            if not destination:
                raise ValueError("A valid destination location is required")
            asset.current_location_id = destination.id
            movement_type = await self.session.scalar(select(MovementType).where(MovementType.code == "TRANSFER"))
            if not movement_type:
                raise ValueError("TRANSFER movement type is not configured")
            self.session.add(AssetMovement(asset_id=asset.id, movement_type_id=movement_type.id, from_location_id=old_location, to_location_id=destination.id, moved_at=datetime.now(), remarks=reason, created_by=user_id))
        elif action == "SEND_FOR_REPAIR":
            repair_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "UNDER_REPAIR"))
            if not repair_status:
                raise ValueError("UNDER_REPAIR status is not configured")
            asset.asset_status_id = repair_status.id
            self.session.add(RepairHistory(asset_id=asset.id, fault_date=date.today(), fault_description=reason, removed_from_location_id=old_location, removal_date=date.today(), created_by=user_id))
        else:
            raise ValueError("Unsupported asset action")
        self.session.add(AssetTimelineEvent(asset_id=asset.id, event_type=f"INCIDENT_{action}", description=reason, metadata_json={"incident_id": str(incident_id), "action": action, "old_location_id": str(old_location) if old_location else None, "old_status_id": old_status, "new_status_id": asset.asset_status_id, "new_location_id": str(asset.current_location_id) if asset.current_location_id else None}, created_by=user_id))
        await self.session.flush()
        return asset

    async def update_work_order_task(self, task_id: UUID, values: dict[str, Any]) -> WorkOrderTask | None:
        repo = WorkOrderTaskRepository(WorkOrderTask, self.session)
        task = await repo.get_by_id(task_id)
        if not task:
            return None
        return await repo.update(task, values)
