from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.asset import Asset, AssetInstallation, AssetMovement, AssetTimelineEvent, RepairHistory
from app.models.dispatch import Dispatch
from app.models.incident import Incident, WorkAction
from app.models.master import AssetStatus, MovementType, LocationType
from app.models.infrastructure import Location, LocationPosition
from app.repositories.asset import AssetInstallationRepository, AssetMovementRepository
from app.services.activity_service import ActivityService


class AssetLifecycleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _has_active_installation(self, asset_id: UUID) -> bool:
        query = select(AssetInstallation).where(
            AssetInstallation.asset_id == asset_id,
            AssetInstallation.current_flag.is_(True)
        )
        current = (await self.session.execute(query)).scalars().first()
        return current is not None

    async def _validate_position_capacity(self, location_position_id: UUID, asset_id: UUID | None = None) -> None:
        pos = await self.session.get(LocationPosition, location_position_id)
        if not pos:
            raise ValueError("Position not found")
        query = select(AssetInstallation).where(
            AssetInstallation.location_position_id == location_position_id,
            AssetInstallation.current_flag.is_(True)
        )
        if asset_id:
            query = query.where(AssetInstallation.asset_id != asset_id)
        active_installations = (await self.session.execute(query)).scalars().all()
        if len(active_installations) >= pos.maximum_capacity:
            raise ValueError(f"Position has reached its maximum capacity of {pos.maximum_capacity}")

    async def _is_store(self, location_id: UUID) -> bool:
        location_type = await self.session.scalar(
            select(LocationType).join(Location, Location.location_type_id == LocationType.id)
            .where(Location.id == location_id)
        )
        return location_type is not None and location_type.code == "STORE"

    async def _close_current_installation(self, asset_id: UUID, removed_by: UUID | None, removed_on: date | None = None, status: str = "REMOVED", remarks: str | None = None) -> AssetInstallation | None:
        current_query = select(AssetInstallation).where(
            AssetInstallation.asset_id == asset_id,
            AssetInstallation.current_flag.is_(True)
        )
        current = (await self.session.execute(current_query)).scalars().first()
        if current:
            current.current_flag = False
            current.installation_status = status
            current.removed_on = removed_on or date.today()
            if removed_by:
                current.removed_by = removed_by
            if remarks:
                current.remarks = remarks
        return current

    async def _record_movement(self, asset_id: UUID, from_location: UUID | None, to_location: UUID | None, movement_type_code: str, remarks: str, user_id: UUID | None = None, vendor_id: UUID | None = None) -> None:
        movement_type = await self.session.scalar(select(MovementType).where(MovementType.code == movement_type_code))
        self.session.add(AssetMovement(
            asset_id=asset_id,
            movement_type_id=movement_type.id if movement_type else None,
            from_location_id=from_location,
            to_location_id=to_location,
            vendor_id=vendor_id,
            remarks=remarks,
            moved_at=datetime.now(),
            created_by=user_id
        ))

    async def _record_timeline(self, asset_id: UUID, event_type: str, description: str, metadata: dict | None = None, user_id: UUID | None = None) -> None:
        self.session.add(AssetTimelineEvent(
            asset_id=asset_id,
            event_type=event_type,
            description=description,
            metadata_json=metadata,
            created_by=user_id
        ))

    async def _record_work_action(self, incident_id: UUID | None, asset_id: UUID, action_type: str, user_id: UUID | None) -> None:
        if incident_id and user_id:
            self.session.add(WorkAction(
                incident_id=incident_id,
                asset_id=asset_id,
                action_type=action_type,
                user_id=user_id,
                timestamp=datetime.now(),
                reference_type="AssetAction",
                reference_id=asset_id
            ))

    async def _format_work_request_prefix(self, work_request_id: UUID | None) -> str:
        if not work_request_id:
            return ""
        incident = await self.session.get(Incident, work_request_id)
        if incident:
            return f"WR {incident.work_request_number}: "
        return f"WR {work_request_id}: "

    async def _format_dispatch_prefix(self, dispatch_id: UUID | None) -> str:
        if not dispatch_id:
            return ""
        dispatch = await self.session.get(Dispatch, dispatch_id)
        if dispatch:
            return f"Dispatch {dispatch.dispatch_no}: "
        return f"Dispatch {dispatch_id}: "

    async def _format_location_label(self, location_id: UUID | None) -> str:
        if not location_id:
            return "Unknown location"
        location = await self.session.get(Location, location_id)
        if location and getattr(location, "name", None):
            return location.name
        return str(location_id)

    async def install_asset(self, asset_id: UUID, location_position_id: UUID, user_id: UUID | None, work_request_id: UUID | None = None, remarks: str | None = None, installed_on: date | None = None) -> AssetInstallation:
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
        if await self._has_active_installation(asset_id):
            raise ValueError("Asset is currently installed. Uninstall the asset first before installing it at a new position.")
        
        # Enforce Store Gateway Rule
        if not asset.current_location_id or not await self._is_store(asset.current_location_id):
            raise ValueError("Asset must be in a STORE location before it can be installed.")

        await self._validate_position_capacity(location_position_id, asset_id=asset_id)
        pos = await self.session.get(LocationPosition, location_position_id)
        if not pos:
            raise ValueError("Position not found")
            
        old_location_id = asset.current_location_id
        asset.current_location_id = pos.location_id
        asset.asset_role = "INSTALLED"
        installed_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "INSTALLED"))
        if installed_status:
            asset.asset_status_id = installed_status.id

        event_remarks = remarks or f"Installed to position {pos.position_number}"
        if work_request_id:
            event_remarks = f"WR {work_request_id}: {event_remarks}"

        await self._record_movement(asset_id, old_location_id, pos.location_id, "TRANSFER", event_remarks, user_id)
        
        repo = AssetInstallationRepository(self.session)
        result = await repo.create(AssetInstallation(
            asset_id=asset_id,
            location_position_id=location_position_id,
            installed_on=installed_on or date.today(),
            installed_by=user_id,
            current_flag=True,
            installation_status="INSTALLED",
            remarks=remarks
        ))

        await self._record_timeline(asset_id, "ASSET_INSTALLED", event_remarks, {"location_position_id": str(location_position_id), "location_id": str(pos.location_id), "work_request_id": str(work_request_id) if work_request_id else None}, user_id)
        # Central activity log
        try:
            await ActivityService(self.session).asset_installed(asset_id=asset_id, asset_number=asset.asset_number, location_name=await self._format_location_label(pos.location_id), project_id=asset.project_id, performed_by=user_id)
        except Exception:
            # Activity logging must not block lifecycle operations
            pass
        await self._record_work_action(work_request_id, asset_id, "INSTALL", user_id)
        
        await self.session.flush()
        return result

    async def uninstall_asset(self, asset_id: UUID, to_location_id: UUID, user_id: UUID | None, work_request_id: UUID | None = None, remarks: str | None = None, removed_on: date | None = None) -> AssetInstallation | None:
        if not to_location_id:
            raise ValueError("A destination STORE location is required when uninstalling an asset.")
            
        # Enforce Store Gateway Rule
        if not await self._is_store(to_location_id):
            raise ValueError("The destination location must be a STORE.")

        current = await self._close_current_installation(asset_id, user_id, removed_on, "UNINSTALLED", remarks)
        if not current:
            raise ValueError("Asset has no active installation to uninstall")

        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
            
        old_location_id = asset.current_location_id
        asset.current_location_id = to_location_id
        asset.asset_role = "SPARE"
        spare_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "SPARE"))
        if spare_status:
            asset.asset_status_id = spare_status.id

        event_remarks = remarks or "Uninstalled and moved to store"
        if work_request_id:
            event_remarks = f"{await self._format_work_request_prefix(work_request_id)}{event_remarks}"

        await self._record_movement(asset_id, old_location_id, to_location_id, "TRANSFER", event_remarks, user_id)
        
        await self._record_timeline(asset_id, "ASSET_UNINSTALLED", event_remarks, {
            "location_position_id": str(current.location_position_id),
            "to_location_id": str(to_location_id),
            "work_request_id": str(work_request_id) if work_request_id else None
        }, user_id)
        await self._record_work_action(work_request_id, asset_id, "UNINSTALL", user_id)
        try:
            await ActivityService(self.session).asset_uninstalled(asset_id=asset_id, asset_number=asset.asset_number, from_location=await self._format_location_label(old_location_id), project_id=asset.project_id, performed_by=user_id)
        except Exception:
            pass

        await self.session.flush()
        return current

    async def move_asset(self, asset_id: UUID, to_location_id: UUID, user_id: UUID | None, work_request_id: UUID | None = None, remarks: str | None = None) -> AssetMovement:
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
        if await self._has_active_installation(asset_id):
            raise ValueError("Asset is currently installed at a position. Uninstall the asset first before moving it to another location.")
            
        old_location_id = asset.current_location_id
        asset.current_location_id = to_location_id
        
        if remarks:
            event_remarks = remarks
        else:
            from_label = await self._format_location_label(old_location_id)
            to_label = await self._format_location_label(to_location_id)
            event_remarks = f"Moved from location {from_label} to {to_label}"
        if work_request_id:
            event_remarks = f"{await self._format_work_request_prefix(work_request_id)}{event_remarks}"

        movement_type = await self.session.scalar(select(MovementType).where(MovementType.code == "TRANSFER"))
        movement = AssetMovement(
            asset_id=asset_id,
            movement_type_id=movement_type.id if movement_type else None,
            from_location_id=old_location_id,
            to_location_id=to_location_id,
            remarks=event_remarks,
            moved_at=datetime.now(),
            created_by=user_id
        )
        self.session.add(movement)
        
        await self._record_timeline(asset_id, "ASSET_MOVED", event_remarks, {
            "from_location_id": str(old_location_id) if old_location_id else None,
            "to_location_id": str(to_location_id),
            "work_request_id": str(work_request_id) if work_request_id else None
        }, user_id)
        await self._record_work_action(work_request_id, asset_id, "MOVE", user_id)
        try:
            from_label = await self._format_location_label(old_location_id)
            to_label = await self._format_location_label(to_location_id)
            await ActivityService(self.session).asset_moved(asset_id=asset_id, asset_number=asset.asset_number, from_location=from_label, to_location=to_label, performed_by=user_id)
        except Exception:
            pass
        await self.session.flush()
        return movement
        
    async def change_status(self, asset_id: UUID, status_id: int, user_id: UUID | None, work_request_id: UUID | None = None, remarks: str | None = None) -> Asset:
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
            
        old_status_id = asset.asset_status_id
        asset.asset_status_id = status_id
        
        event_remarks = remarks or "Asset status changed"
        if work_request_id:
            event_remarks = f"WR {work_request_id}: {event_remarks}"

        await self._record_timeline(asset_id, "STATUS_CHANGED", event_remarks, {
            "old_status_id": old_status_id,
            "new_status_id": status_id,
            "work_request_id": str(work_request_id) if work_request_id else None
        }, user_id)
        await self._record_work_action(work_request_id, asset_id, "CHANGE_STATUS", user_id)

        await self.session.flush()
        return asset

    async def dispatch_for_repair(self, asset_id: UUID, vendor_id: UUID | None, courier_number: str | None, fault_date: date | None, fault_description: str | None, user_id: UUID | None, work_request_id: UUID | None = None, dispatch_id: UUID | None = None) -> RepairHistory:
        asset = await self.session.get(Asset, asset_id)
        if not asset:
            raise ValueError("Asset not found")
        if await self._has_active_installation(asset_id):
            raise ValueError("Asset is currently installed at a position. Uninstall the asset and move it to a store before dispatching for repair.")
        if not asset.current_location_id or not await self._is_store(asset.current_location_id):
            raise ValueError("Asset must be located in a STORE before dispatching for repair.")

        repair_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "UNDER_REPAIR"))
        if not repair_status:
            raise ValueError("UNDER_REPAIR status is not configured")
            
        old_location_id = asset.current_location_id
        asset.asset_status_id = repair_status.id
        asset.current_location_id = None  # Asset leaves tracked locations

        event_remarks = fault_description or "Sent for repair"
        if work_request_id:
            event_remarks = f"{await self._format_work_request_prefix(work_request_id)}{event_remarks}"
        elif dispatch_id:
            event_remarks = f"{await self._format_dispatch_prefix(dispatch_id)}{event_remarks}"

        repair = RepairHistory(
            asset_id=asset_id,
            fault_date=fault_date or date.today(),
            fault_description=event_remarks,
            removed_from_location_id=old_location_id,
            removal_date=date.today(),
            dispatch_date=date.today(),
            courier_number=courier_number,
            vendor_id=vendor_id,
            created_by=user_id
        )
        self.session.add(repair)
        
        await self._record_movement(asset_id, old_location_id, None, "REPAIR", event_remarks, user_id, vendor_id)
        
        await self._record_timeline(asset_id, "REPAIR_DISPATCHED", f"Dispatched for repair. {event_remarks}", {
            "work_request_id": str(work_request_id) if work_request_id else None,
            "dispatch_id": str(dispatch_id) if dispatch_id else None,
            "vendor_id": str(vendor_id) if vendor_id else None
        }, user_id)
        await self._record_work_action(work_request_id, asset_id, "SEND_FOR_REPAIR", user_id)

        try:
            await ActivityService(self.session).log_activity(source="AUTO", module="ASSET", action="DISPATCH", title="Dispatched for Repair", description=f"Dispatched {asset.asset_number} for repair.", asset_id=asset_id, performed_by=user_id, metadata={"dispatch_id": str(dispatch_id) if dispatch_id else None, "vendor_id": str(vendor_id) if vendor_id else None})
        except Exception:
            pass

        await self.session.flush()
        return repair

    async def receive_from_repair(self, asset_id: UUID, to_location_id: UUID, return_date: date | None, repair_cost: float | None, repair_remarks: str | None, status_code: str | None, condition_code: str | None = None, user_id: UUID | None = None, work_request_id: UUID | None = None, dispatch_id: UUID | None = None) -> RepairHistory:
        if not to_location_id:
            raise ValueError("A destination STORE location is required to receive the asset.")
        if not await self._is_store(to_location_id):
            raise ValueError("Destination location must be a STORE.")

        repair_query = select(RepairHistory).where(
            RepairHistory.asset_id == asset_id,
            RepairHistory.return_date.is_(None)
        ).order_by(RepairHistory.created_at.desc())
        repair = (await self.session.execute(repair_query)).scalars().first()
        if not repair:
            # No active repair record found — this can happen for dispatches
            # submitted before lifecycle integration was added. Create a
            # backfill record so the receive flow can complete.
            import structlog
            structlog.get_logger().warning(
                "backfill_repair_record",
                asset_id=str(asset_id),
                reason="No active repair record found; creating backfill entry",
            )
            asset = await self.session.get(Asset, asset_id)
            repair = RepairHistory(
                asset_id=asset_id,
                fault_date=return_date or date.today(),
                fault_description="Backfilled from dispatch receive",
                removed_from_location_id=asset.current_location_id if asset else None,
                removal_date=return_date or date.today(),
                dispatch_date=return_date or date.today(),
                created_by=user_id,
            )
            self.session.add(repair)
            await self.session.flush()

        repair.return_date = return_date or date.today()
        repair.repair_cost = repair_cost
        repair.repair_remarks = repair_remarks
        
        target_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == (status_code or "IN_STOCK")))
        if not target_status:
            target_status = await self.session.scalar(select(AssetStatus).where(AssetStatus.code == "IN_STOCK"))
            
        asset = await self.session.get(Asset, asset_id)
        if asset and target_status:
            asset.asset_status_id = target_status.id
            asset.current_location_id = to_location_id
            asset.asset_role = "SPARE"

            # Update asset condition if a condition_code was provided
            if condition_code:
                from app.models.master import AssetCondition
                target_condition = await self.session.scalar(
                    select(AssetCondition).where(AssetCondition.code == condition_code)
                )
                if target_condition:
                    asset.asset_condition_id = target_condition.id

        event_remarks = repair_remarks or "Returned from repair"
        if work_request_id:
            event_remarks = f"{await self._format_work_request_prefix(work_request_id)}{event_remarks}"
        elif dispatch_id:
            event_remarks = f"{await self._format_dispatch_prefix(dispatch_id)}{event_remarks}"

        await self._record_movement(asset_id, repair.removed_from_location_id, to_location_id, "RECEIVE", event_remarks, user_id, repair.vendor_id)

        await self._record_timeline(asset_id, "REPAIR_RETURNED", f"Returned from repair. {event_remarks}", {
            "work_request_id": str(work_request_id) if work_request_id else None,
            "dispatch_id": str(dispatch_id) if dispatch_id else None,
            "cost": repair_cost
        }, user_id)
        await self._record_work_action(work_request_id, asset_id, "RETURN_FROM_REPAIR", user_id)

        try:
            await ActivityService(self.session).log_activity(source="AUTO", module="ASSET", action="RECEIVE", title="Received from Repair", description=f"Received {asset.asset_number} from repair.", asset_id=asset_id, performed_by=user_id, metadata={"dispatch_id": str(dispatch_id) if dispatch_id else None})
        except Exception:
            pass

        await self.session.flush()
        return repair
