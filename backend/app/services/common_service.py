from typing import Any
from uuid import UUID

from sqlalchemy import exists, func, or_, select

from app.models.common import Vendor, VendorAssetScope

from app.repositories.common import CommonRepository


class CommonService:
    def __init__(self, session) -> None:
        self.session = session

    async def get_entity(self, model: type[Any], entity_id: UUID) -> Any | None:
        repo = CommonRepository(model, self.session)
        return await repo.get_by_id(entity_id)

    async def list_entities(self, model: type[Any], offset: int = 0, limit: int = 100) -> tuple[list[Any], int]:
        repo = CommonRepository(model, self.session)
        items = await repo.list(offset=offset, limit=limit)
        total = await repo.count()
        return items, total

    async def create_entity(self, model: type[Any], values: dict[str, Any]) -> Any:
        entity = model(**values)
        repo = CommonRepository(model, self.session)
        return await repo.create(entity)

    async def list_vendors_for_asset(self, *, category_id: int | None, subcategory_id: int | None, manufacturer_id: int | None, offset: int, limit: int) -> tuple[list[Vendor], int]:
        query = select(Vendor).where(Vendor.is_active.is_(True))
        if category_id is not None:
            has_scope = exists(select(VendorAssetScope.id).where(VendorAssetScope.vendor_id == Vendor.id, VendorAssetScope.is_active.is_(True)))
            matching_scope = exists(select(VendorAssetScope.id).where(
                VendorAssetScope.vendor_id == Vendor.id, VendorAssetScope.asset_category_id == category_id,
                VendorAssetScope.is_active.is_(True),
                or_(VendorAssetScope.asset_subcategory_id.is_(None), VendorAssetScope.asset_subcategory_id == subcategory_id),
                or_(VendorAssetScope.manufacturer_id.is_(None), VendorAssetScope.manufacturer_id == manufacturer_id),
            ))
            query = query.where(or_(~has_scope, matching_scope))
        items = (await self.session.execute(query.order_by(Vendor.vendor_name).offset(offset).limit(limit))).scalars().all()
        total = await self.session.scalar(select(func.count()).select_from(query.subquery()))
        return items, total or 0

    async def update_entity(self, model: type[Any], entity_id: UUID, values: dict[str, Any]) -> Any | None:
        repo = CommonRepository(model, self.session)
        entity = await repo.get_by_id(entity_id)
        if not entity:
            return None
        return await repo.update(entity, values)
