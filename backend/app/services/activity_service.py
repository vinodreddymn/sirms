from __future__ import annotations

from typing import Any, List, Tuple
from uuid import UUID

from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common import ActivityLog


class ActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_activity(
        self,
        *,
        source: str | None,
        module: str,
        action: str | None,
        title: str,
        description: str | None = None,
        entity_name: str | None = None,
        entity_id: UUID | None = None,
        project_id: UUID | None = None,
        location_id: UUID | None = None,
        asset_id: UUID | None = None,
        work_request_id: UUID | None = None,
        dispatch_id: UUID | None = None,
        metadata: dict | None = None,
        performed_by: UUID | None = None,
    ) -> ActivityLog:
        normalized_metadata = metadata or {}
        normalized_module = (module or "UNKNOWN").strip() or "UNKNOWN"
        normalized_action = (action or normalized_metadata.get("action") or "").strip()
        normalized_entity_name = (entity_name or normalized_metadata.get("entity_name") or "").strip()

        entry = ActivityLog(
            activity_at=normalized_metadata.get("activity_time") if normalized_metadata.get("activity_time") else None,
            activity_type=normalized_action,
            module_name=normalized_module,
            entity_name=normalized_entity_name,
            entity_id=entity_id,
            activity_details={
                "source": source,
                "title": title,
                "description": description,
                "metadata": normalized_metadata,
                "project_id": str(project_id) if project_id else None,
                "location_id": str(location_id) if location_id else None,
                "asset_id": str(asset_id) if asset_id else None,
                "work_request_id": str(work_request_id) if work_request_id else None,
                "dispatch_id": str(dispatch_id) if dispatch_id else None,
            },
            project_id=project_id,
            created_by=performed_by,
        )

        try:
            async with self.session.begin_nested():
                self.session.add(entry)
                await self.session.flush()
        except Exception:
            return entry

        return entry

    async def list_activities(self, offset: int = 0, limit: int = 50, filters: dict | None = None) -> Tuple[List[ActivityLog], int]:
        query = select(ActivityLog)
        if filters:
            conds = []
            if filters.get("module"):
                conds.append(ActivityLog.module_name == filters["module"])
            if filters.get("project_id"):
                conds.append(ActivityLog.project_id == filters["project_id"])
            if filters.get("asset_id"):
                conds.append(ActivityLog.activity_details["asset_id"].astext == str(filters["asset_id"]))
            if filters.get("user_id"):
                conds.append(ActivityLog.created_by == filters["user_id"])
            if conds:
                query = query.where(and_(*conds))

        total_q = select(ActivityLog)
        result = await self.session.execute(query.order_by(desc(ActivityLog.activity_at)).offset(offset).limit(limit))
        items = result.scalars().all()
        count_res = await self.session.execute(select(func.count()).select_from(ActivityLog))
        total = int(count_res.scalar_one() or 0)
        return items, total

    # Convenience helpers for common events
    async def work_request_created(self, work_request_id: UUID, work_request_number: str, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Created Work Request"
        description = f"Created Work Request {work_request_number}."
        return await self.log_activity(source="AUTO", module="WORK_REQUEST", action="CREATE", title=title, description=description, work_request_id=work_request_id, project_id=project_id, performed_by=performed_by)

    async def work_request_assigned(self, work_request_id: UUID, work_request_number: str, assignee_name: str, performed_by: UUID | None = None) -> ActivityLog:
        title = "Assigned Work Request"
        description = f"Assigned Work Request {work_request_number} to {assignee_name}."
        return await self.log_activity(source="AUTO", module="WORK_REQUEST", action="ASSIGN", title=title, description=description, work_request_id=work_request_id, performed_by=performed_by)

    async def asset_registered(self, asset_id: UUID, asset_number: str, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Registered Asset"
        description = f"Registered {asset_number}."
        return await self.log_activity(source="AUTO", module="ASSET", action="CREATE", title=title, description=description, asset_id=asset_id, project_id=project_id, performed_by=performed_by)

    async def asset_installed(self, asset_id: UUID, asset_number: str, location_name: str | None = None, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Installed Asset"
        description = f"Installed {asset_number}" + (f" at {location_name}." if location_name else ".")
        return await self.log_activity(source="AUTO", module="ASSET", action="INSTALL", title=title, description=description, asset_id=asset_id, project_id=project_id, performed_by=performed_by)

    async def asset_uninstalled(self, asset_id: UUID, asset_number: str, from_location: str | None = None, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Uninstalled Asset"
        description = f"Removed {asset_number}" + (f" from {from_location}." if from_location else ".")
        return await self.log_activity(source="AUTO", module="ASSET", action="UNINSTALL", title=title, description=description, asset_id=asset_id, project_id=project_id, performed_by=performed_by)

    async def asset_moved(self, asset_id: UUID, asset_number: str, from_location: str | None, to_location: str | None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Moved Asset"
        description = f"Moved {asset_number} from {from_location or 'unknown'} to {to_location or 'unknown'}."
        return await self.log_activity(source="AUTO", module="ASSET", action="MOVE", title=title, description=description, asset_id=asset_id, performed_by=performed_by)

    async def dispatch_created(self, dispatch_id: UUID, dispatch_number: str, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Created Dispatch"
        description = f"Created Dispatch {dispatch_number}."
        return await self.log_activity(source="AUTO", module="DISPATCH", action="CREATE", title=title, description=description, dispatch_id=dispatch_id, project_id=project_id, performed_by=performed_by)

    async def dispatch_sent(self, dispatch_id: UUID, dispatch_number: str, vendor_name: str | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Dispatch Sent"
        description = f"Sent {dispatch_number}" + (f" to {vendor_name}." if vendor_name else ".")
        return await self.log_activity(source="AUTO", module="DISPATCH", action="SEND", title=title, description=description, dispatch_id=dispatch_id, performed_by=performed_by)

    async def invoice_created(self, invoice_id: UUID, invoice_number: str, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "Invoice Created"
        description = f"Created Invoice {invoice_number}."
        return await self.log_activity(source="AUTO", module="FINANCE", action="CREATE", title=title, description=description, project_id=project_id, performed_by=performed_by)

    async def invoice_approved(self, invoice_id: UUID, invoice_number: str, performed_by: UUID | None = None) -> ActivityLog:
        title = "Invoice Approved"
        description = f"Approved Invoice {invoice_number}."
        return await self.log_activity(source="AUTO", module="FINANCE", action="APPROVE", title=title, description=description, performed_by=performed_by)

    async def pm_completed(self, pm_id: UUID, pm_name: str, project_id: UUID | None = None, performed_by: UUID | None = None) -> ActivityLog:
        title = "PM Completed"
        description = f"Preventive maintenance '{pm_name}' completed."
        return await self.log_activity(source="AUTO", module="PM", action="COMPLETE", title=title, description=description, project_id=project_id, performed_by=performed_by)

    async def document_uploaded(self, entity_name: str, entity_id: UUID, filename: str, performed_by: UUID | None = None) -> ActivityLog:
        title = "Document Uploaded"
        description = f"Uploaded document {filename} for {entity_name}."
        return await self.log_activity(source="AUTO", module="DOCUMENT", action="UPLOAD", title=title, description=description, entity_name=entity_name, entity_id=entity_id, performed_by=performed_by)

    async def user_created(self, user_id: UUID, username: str, performed_by: UUID | None = None) -> ActivityLog:
        title = "User Created"
        description = f"Created user {username}."
        return await self.log_activity(source="AUTO", module="USER", action="CREATE", title=title, description=description, entity_name="USER", entity_id=user_id, performed_by=performed_by)
