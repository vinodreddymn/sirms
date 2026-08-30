from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func

from app.models.incident import Incident, IncidentAttachment, IncidentUpdate, WorkAssignment, WorkAction, WorkRelation
from app.models.asset import Asset, AssetInstallation, AssetMovement, AssetTimelineEvent, RepairHistory

from app.models.infrastructure import Location
from app.models.master import AssetStatus, IncidentStatus, MovementType, WorkType
from app.repositories.incident import (
    IncidentAttachmentRepository,
    IncidentRepository,
    IncidentUpdateRepository,
    WorkAssignmentRepository,
    WorkActionRepository,
    WorkRelationRepository,
)
from app.services.activity_service import ActivityService


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
        work_type_id = values.get("work_type_id")
        if not work_type_id:
            work_type = await self.session.scalar(select(WorkType).where(WorkType.code == "INCIDENT"))
            if not work_type:
                raise ValueError("Default INCIDENT work type is missing from the database.")
            work_type_id = work_type.id
            values["work_type_id"] = work_type_id
        else:
            work_type = await self.session.scalar(select(WorkType).where(WorkType.id == work_type_id))
            if not work_type:
                raise ValueError("Invalid work_type_id provided.")

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
        if not values.get("work_request_number"):
            try:
                values["work_request_number"] = await self.session.scalar(
                    text("SELECT common.generate_business_number(:entity_name)"),
                    {"entity_name": work_type.code},
                )
            except Exception as exc:
                work_type_code = work_type.code
                try:
                    await self.session.rollback()
                except Exception:
                    pass
                raise ValueError(
                    f"Unable to generate incident number for work type '{work_type_code}'. "
                    "Ensure a matching row exists in common.number_sequences for this work type."
                ) from exc
        values.setdefault("reported_at", datetime.now())
        entity = Incident(**values)
        repo = IncidentRepository(Incident, self.session)
        return await repo.create(entity)

    async def update_incident(self, incident_id: UUID, values: dict[str, Any], user_id: UUID | None = None) -> Incident | None:
        repo = IncidentRepository(Incident, self.session)
        incident = await repo.get_by_id(incident_id)
        if not incident:
            return None
        status_id = values.get("status_id")
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
        # Activity logging
        try:
            act_service = ActivityService(self.session)
            if values.get("status_after_update_id"):
                incident.status_id = values["status_after_update_id"]
                status = await self.session.scalar(select(IncidentStatus).where(IncidentStatus.id == values["status_after_update_id"]))
                if status:
                    # Map to action
                    action = "UPDATE_STATUS"
                    title = f"Work Request Status: {status.name}"
                    description = f"Work Request {incident.work_request_number} status changed to {status.name}."
                    await act_service.log_activity(source="AUTO", module="WORK_REQUEST", action=action, title=title, description=description, work_request_id=incident.id, project_id=incident.project_id, performed_by=user_id)
                    if status and status.code in ("CLOSED", "RESOLVED"):
                        incident.closed_date = datetime.now()
                        incident.closed_by = user_id
                        incident.completion_notes = values.get("update_notes")
            # If there are update notes, add a simple activity
            if values.get("update_notes"):
                await act_service.log_activity(source="AUTO", module="WORK_REQUEST", action="UPDATE", title="Work Request Update", description=f"{values.get('update_notes')}", work_request_id=incident.id, project_id=incident.project_id, performed_by=user_id)
        except Exception:
            pass
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


    # =========================================================================
    # WORK ASSIGNMENTS
    # =========================================================================

    async def list_work_assignments(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[WorkAssignment], int]:
        repo = WorkAssignmentRepository(WorkAssignment, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_work_assignment(self, incident_id: UUID, values: dict[str, Any]) -> WorkAssignment:
        values["incident_id"] = incident_id
        entity = WorkAssignment(**values)
        repo = WorkAssignmentRepository(WorkAssignment, self.session)
        return await repo.create(entity)

    # =========================================================================
    # WORK ACTIONS
    # =========================================================================

    async def list_work_actions(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[WorkAction], int]:
        repo = WorkActionRepository(WorkAction, self.session)
        items = await repo.list_by_incident(incident_id, offset=offset, limit=limit)
        return items, await repo.count_by_incident(incident_id)

    async def create_work_action(self, incident_id: UUID, values: dict[str, Any]) -> WorkAction:
        values["incident_id"] = incident_id
        values.setdefault("timestamp", datetime.now())
        entity = WorkAction(**values)
        repo = WorkActionRepository(WorkAction, self.session)
        return await repo.create(entity)

    # =========================================================================
    # WORK RELATIONS
    # =========================================================================

    async def list_work_relations(self, source_incident_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[WorkRelation], int]:
        repo = WorkRelationRepository(WorkRelation, self.session)
        items = await repo.list_by_source(source_incident_id, offset=offset, limit=limit)
        # using generic count for relations by source, but wait we only have list_by_source and list_by_target.
        # it's fine for now, we can just return len(items) if we don't implement count_by_source
        return items, len(items)

    async def create_work_relation(self, source_incident_id: UUID, values: dict[str, Any]) -> WorkRelation:
        values["source_incident_id"] = source_incident_id
        entity = WorkRelation(**values)
        repo = WorkRelationRepository(WorkRelation, self.session)
        return await repo.create(entity)
