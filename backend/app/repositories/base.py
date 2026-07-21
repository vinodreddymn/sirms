from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: Any) -> T | None:
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalars().first()

    async def list(self, offset: int = 0, limit: int = 100) -> list[T]:
        result = await self.session.execute(select(self.model).offset(offset).limit(limit))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.session.execute(select(self.model))
        return len(result.scalars().all())

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: T, values: dict[str, Any]) -> T:
        for key, value in values.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def soft_delete(self, entity: T) -> T:
        if hasattr(entity, "is_active"):
            setattr(entity, "is_active", False)
            await self.session.flush()
        return entity

    async def hard_delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()
