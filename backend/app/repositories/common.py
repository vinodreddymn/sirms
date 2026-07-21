from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class CommonRepository:
    def __init__(self, model: type[Any], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> Any | None:
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalars().first()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.session.execute(select(self.model))
        return len(result.scalars().all())

    async def create(self, entity: Any) -> Any:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: Any, values: dict[str, Any]) -> Any:
        for key, value in values.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, entity: Any) -> None:
        await self.session.delete(entity)
        await self.session.flush()
