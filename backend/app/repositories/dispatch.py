"""Repository layer for Dispatch module."""

from __future__ import annotations

from typing import Any
from unittest import result
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset
from app.models.common import Vendor
from app.models.dispatch import Dispatch, DispatchItem
from app.repositories.base import BaseRepository


class DispatchRepository(BaseRepository[Dispatch]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Dispatch, session)

    async def generate_dispatch_number(self, db: AsyncSession) -> str:
        result = await db.execute(
            text("SELECT common.get_next_sequence('DISPATCH')")
        )
        return result.scalar_one()


    async def generate_challan_number(self, db: AsyncSession) -> str:
        result = await db.execute(
            text("SELECT common.get_next_sequence('DELIVERY_CHALLAN')")
        )
        return result.scalar_one()

    async def get_details(self, dispatch_id: UUID) -> dict[str, Any] | None:
        query = (
            select(Dispatch)
            .options(
                selectinload(Dispatch.items)
                .selectinload(DispatchItem.asset),
                selectinload(Dispatch.items)
                .selectinload(DispatchItem.asset)
                .selectinload(Asset.asset_category),
                selectinload(Dispatch.items)
                .selectinload(DispatchItem.asset)
                .selectinload(Asset.asset_subcategory),
            )
            .where(Dispatch.id == dispatch_id, Dispatch.is_active.is_(True))
        )
        result = await self.session.execute(query)
        dispatch = result.scalars().first()

        if not dispatch:
            return None

        vendor_name = None
        if dispatch.vendor_id:
            vendor = await self.session.get(Vendor, dispatch.vendor_id)
            vendor_name = vendor.vendor_name if vendor else None

        return {
            "id": dispatch.id,
            "dispatch_no": dispatch.dispatch_no,
            "delivery_challan_no": dispatch.delivery_challan_no,
            "dispatch_date": dispatch.dispatch_date,
            "vendor_id": dispatch.vendor_id,
            "vendor_name": vendor_name,
            "purpose": dispatch.purpose,
            "courier_name": dispatch.courier_name,
            "tracking_number": dispatch.tracking_number,
            "remarks": dispatch.remarks,
            "status": dispatch.status,
            "created_at": dispatch.created_at,
            "updated_at": dispatch.updated_at,
            "items": [
                {
                    "id": item.id,
                    "dispatch_id": item.dispatch_id,
                    "asset_id": item.asset_id,
                    "asset_number": item.asset.asset_number if item.asset else None,
                    "asset_category": item.asset.asset_category.name if item.asset and item.asset.asset_category else None,
                    "asset_subcategory": item.asset.asset_subcategory.name if item.asset and item.asset.asset_subcategory else None,
                    "asset_serial_number": item.asset.serial_number if item.asset else None,
                    "dispatch_type": item.dispatch_type,
                    "component_name": item.component_name,
                    "quantity": item.quantity,
                    "condition": item.condition,
                    "status": item.status,
                    "return_date": item.return_date,
                    "result": item.result,
                    "repair_cost": item.repair_cost,
                    "remarks": item.remarks,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                for item in dispatch.items
                if item.is_active
            ],
        }

    async def list_dispatches(self, offset: int = 0, limit: int = 100, search: str | None = None) -> tuple[list[dict[str, Any]], int]:
        query = select(Dispatch).where(Dispatch.is_active.is_(True))
        
        if search:
            query = query.where(Dispatch.dispatch_no.ilike(f"%{search}%"))
            
        count_query = select(text("COUNT(*)")).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        query = query.order_by(Dispatch.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        
        dispatches = []
        for dispatch in result.scalars().all():
            vendor_name = None
            if dispatch.vendor_id:
                vendor = await self.session.get(Vendor, dispatch.vendor_id)
                vendor_name = vendor.vendor_name if vendor else None

            dispatches.append({
                "id": dispatch.id,
                "dispatch_no": dispatch.dispatch_no,
                "delivery_challan_no": dispatch.delivery_challan_no,
                "dispatch_date": dispatch.dispatch_date,
                "vendor_id": dispatch.vendor_id,
                "vendor_name": vendor_name,
                "purpose": dispatch.purpose,
                "courier_name": dispatch.courier_name,
                "tracking_number": dispatch.tracking_number,
                "remarks": dispatch.remarks,
                "status": dispatch.status,
                "created_at": dispatch.created_at,
                "updated_at": dispatch.updated_at,
            })
            
        return dispatches, total


class DispatchItemRepository(BaseRepository[DispatchItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(DispatchItem, session)
