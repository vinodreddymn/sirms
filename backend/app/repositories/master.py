from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import MasterLookupMixin
from app.repositories.base import BaseRepository


class MasterRepository:
    def __init__(self, model: type[MasterLookupMixin], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: int) -> MasterLookupMixin | None:
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalars().first()

    def _filtered_query(self, filters: dict[str, int] | None = None):
        query = select(self.model)
        for field_name, value in (filters or {}).items():
            query = query.where(getattr(self.model, field_name) == value)
        return query

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: dict[str, int] | None = None,
    ) -> list[MasterLookupMixin]:
        result = await self.session.execute(self._filtered_query(filters).offset(offset).limit(limit))
        return result.scalars().all()

    async def count(self, filters: dict[str, int] | None = None) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(self._filtered_query(filters).subquery()),
        )
        return result.scalar_one()

    async def create(self, entity: MasterLookupMixin) -> MasterLookupMixin:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: MasterLookupMixin, values: dict[str, Any]) -> MasterLookupMixin:
        for key, value in values.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity
