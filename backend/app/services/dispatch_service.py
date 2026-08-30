"""Service layer for Dispatch module."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.dispatch import Dispatch, DispatchItem
from app.models.asset import Asset, AssetTimelineEvent
from app.models.master import AssetStatus
from app.repositories.dispatch import DispatchItemRepository, DispatchRepository
from app.services.asset_lifecycle_service import AssetLifecycleService
from app.services.activity_service import ActivityService


class DispatchService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dispatch_repo = DispatchRepository(session)
        self.item_repo = DispatchItemRepository(session)

    async def list_dispatches(self, offset: int, limit: int, search: str | None = None) -> tuple[list[dict[str, Any]], int]:
        return await self.dispatch_repo.list_dispatches(offset, limit, search)

    async def get_dispatch_details(self, dispatch_id: UUID) -> dict[str, Any] | None:
        return await self.dispatch_repo.get_details(dispatch_id)

    async def create_dispatch(self, values: dict[str, Any], user_id: UUID) -> Dispatch:
        items_data = values.pop("items", [])
        
        # Generate dispatch number
        dispatch_no = await self.dispatch_repo.generate_dispatch_number(self.session)
        values["dispatch_no"] = dispatch_no
        values["created_by"] = user_id

        dispatch = await self.dispatch_repo.create(Dispatch(**values))

        for item_data in items_data:
            item_data["dispatch_id"] = dispatch.id
            item_data["created_by"] = user_id
            await self.item_repo.create(DispatchItem(**item_data))

        try:
            await ActivityService(self.session).dispatch_created(dispatch.id, dispatch.dispatch_no, project_id=dispatch.project_id, performed_by=user_id)
        except Exception:
            pass

        return dispatch

    async def update_dispatch(self, dispatch_id: UUID, values: dict[str, Any], user_id: UUID) -> Dispatch | None:
        dispatch = await self.dispatch_repo.get_by_id(dispatch_id)
        if not dispatch:
            return None

        if dispatch.status != "Draft":
            raise ValueError("Only Draft dispatches can be updated")

        values["updated_by"] = user_id
        return await self.dispatch_repo.update(dispatch, values)

    async def submit_dispatch(self, dispatch_id: UUID, user_id: UUID) -> Dispatch | None:
        dispatch = await self.dispatch_repo.get_by_id(dispatch_id)
        if not dispatch:
            return None
        
        if dispatch.status != "Draft":
            raise ValueError("Only Draft dispatches can be submitted")

        # Load items
        result = await self.session.execute(select(DispatchItem).where(DispatchItem.dispatch_id == dispatch_id, DispatchItem.is_active.is_(True)))
        items = result.scalars().all()

        if not items:
            raise ValueError("Cannot submit a dispatch without items")

        # Generate challan number
        challan_no = await self.dispatch_repo.generate_challan_number(self.session)
        
        # Update dispatch
        dispatch.delivery_challan_no = challan_no
        dispatch.status = "Dispatched"
        dispatch.updated_by = user_id
        
        # Process assets
        lifecycle = AssetLifecycleService(self.session)
        for item in items:
            if item.dispatch_type == "Asset" and item.asset_id:
                asset = await self.session.get(Asset, item.asset_id)
                if asset:
                    # Dispatch using lifecycle service
                    await lifecycle.dispatch_for_repair(
                        asset_id=asset.id,
                        vendor_id=dispatch.vendor_id,
                        courier_number=dispatch.tracking_number or dispatch.courier_name,
                        fault_date=dispatch.dispatch_date,
                        fault_description=dispatch.purpose,
                        user_id=user_id,
                        dispatch_id=dispatch.id
                    )
            elif item.dispatch_type == "Component" and item.asset_id:
                # Component dispatch - parent asset status remains unchanged, but record history
                timeline_event = AssetTimelineEvent(
                    asset_id=item.asset_id,
                    event_type="COMPONENT_DISPATCHED",
                    description=f"Component '{item.component_name}' dispatched for {dispatch.purpose}. Challan: {challan_no}",
                    created_by=user_id,
                )
                self.session.add(timeline_event)

        await self.session.flush()
        # Log dispatch submission
        try:
            await ActivityService(self.session).dispatch_sent(dispatch.id, dispatch.dispatch_no, vendor_name=None, performed_by=user_id)
        except Exception:
            pass
        return dispatch

    async def receive_item(self, item_id: UUID, dispatch_id: UUID, values: dict[str, Any], user_id: UUID) -> DispatchItem | None:
        item = await self.item_repo.get_by_id(item_id)
        if not item or item.dispatch_id != dispatch_id:
            return None

        if item.status == "Returned":
            raise ValueError("Item is already returned")

        dispatch = await self.dispatch_repo.get_by_id(dispatch_id)
        if not dispatch or dispatch.status not in ["Dispatched", "Partially Returned"]:
            raise ValueError("Can only receive items for Dispatched or Partially Returned dispatches")

        # Update item
        item.status = "Returned"
        item.return_date = values["return_date"]
        item.result = values["result"]
        item.repair_cost = values.get("repair_cost")
        item.remarks = values.get("remarks")
        item.updated_by = user_id

        # Update Asset
        if item.asset_id:
            asset = await self.session.get(Asset, item.asset_id)
            if asset:
                if item.dispatch_type == "Asset":
                    # Map dispatch result → asset status code
                    # Valid codes from master: IN_STOCK, INSTALLED, UNDER_REPAIR, SCRAPPED
                    if item.result in ["Repaired", "Replaced", "Returned Without Repair"]:
                        new_status_code = "IN_STOCK"
                    elif item.result == "Beyond Repair":
                        new_status_code = "SCRAPPED"
                    else:
                        new_status_code = "IN_STOCK"

                    # Map dispatch result → asset condition code
                    # Condition codes align with dispatch item condition values
                    condition_code_map = {
                        "Repaired": "Working",
                        "Replaced": "Working",
                        "Returned Without Repair": "Faulty",
                        "Beyond Repair": "Damaged",
                    }
                    condition_code = condition_code_map.get(item.result)

                    store_location_id = values.get("store_location_id") or values.get("to_location_id")
                    if not store_location_id:
                        raise ValueError("A store location is required to receive an asset")

                    lifecycle = AssetLifecycleService(self.session)
                    await lifecycle.receive_from_repair(
                        asset_id=asset.id,
                        to_location_id=UUID(str(store_location_id)) if isinstance(store_location_id, str) else store_location_id,
                        return_date=datetime.strptime(values["return_date"], "%Y-%m-%d").date() if isinstance(values["return_date"], str) else values["return_date"],
                        repair_cost=values.get("repair_cost"),
                        repair_remarks=values.get("remarks"),
                        status_code=new_status_code,
                        condition_code=condition_code,
                        user_id=user_id,
                        dispatch_id=dispatch_id
                    )
                else:
                    # Component return
                    event_type = "COMPONENT_RETURNED"
                    event_desc = f"Component '{item.component_name}' returned. Result: {item.result}."
                    timeline_event = AssetTimelineEvent(
                        asset_id=asset.id,
                        event_type=event_type,
                        description=event_desc,
                        created_by=user_id,
                    )
                    self.session.add(timeline_event)

        # Check dispatch status
        result = await self.session.execute(select(DispatchItem).where(DispatchItem.dispatch_id == dispatch_id, DispatchItem.is_active.is_(True)))
        all_items = result.scalars().all()
        
        all_returned = all(i.status == "Returned" for i in all_items)
        if all_returned:
            dispatch.status = "Closed"
        else:
            dispatch.status = "Partially Returned"
            
        dispatch.updated_by = user_id
        
        await self.session.flush()
        return item
