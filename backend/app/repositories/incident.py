from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class IncidentRepository:
    def __init__(self, model: type[Any], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> Any | None:
        result = await self.session.execute(select(self.model).where(self.model.id == entity_id))
        return result.scalars().first()

    def _search_filter(self, search: str | None):
        if not search or self.model.__name__ != "Incident":
            return None
        pattern = f"%{search.strip()}%"
        return or_(self.model.incident_number.ilike(pattern), self.model.description.ilike(pattern))

    async def list(self, offset: int = 0, limit: int = 100, search: str | None = None) -> list[Any]:
        query = select(self.model)
        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)
        result = await self.session.execute(query.offset(offset).limit(limit))
        return result.scalars().all()

    async def count(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(self.model)
        search_filter = self._search_filter(search)
        if search_filter is not None:
            query = query.where(search_filter)
        return (await self.session.scalar(query)) or 0

    async def create(self, entity: Any) -> Any:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: Any, values: dict[str, Any]) -> Any:
        for key, value in values.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity


class IncidentUpdateRepository(IncidentRepository):
    async def list_by_incident(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(self.model).where(self.model.incident_id == incident_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_incident(self, incident_id: UUID) -> int:
        result = await self.session.execute(select(self.model).where(self.model.incident_id == incident_id))
        return len(result.scalars().all())


class WorkOrderRepository(IncidentRepository):
    async def get_by_incident(self, incident_id: UUID) -> Any | None:
        result = await self.session.execute(select(self.model).where(self.model.incident_id == incident_id))
        return result.scalars().first()

    async def list_by_incident(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(self.model).where(self.model.incident_id == incident_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_incident(self, incident_id: UUID) -> int:
        result = await self.session.execute(select(self.model).where(self.model.incident_id == incident_id))
        return len(result.scalars().all())


class WorkOrderTaskRepository(IncidentRepository):
    async def list_by_work_order(self, work_order_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(self.model).where(self.model.work_order_id == work_order_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_work_order(self, work_order_id: UUID) -> int:
        result = await self.session.execute(select(self.model).where(self.model.work_order_id == work_order_id))
        return len(result.scalars().all())


class IncidentAttachmentRepository(IncidentRepository):
    async def list_by_incident(self, incident_id: UUID, offset: int = 0, limit: int = 100) -> list[Any]:
        result = await self.session.execute(
            select(self.model).where(self.model.incident_id == incident_id).offset(offset).limit(limit)
        )
        return result.scalars().all()

    async def count_by_incident(self, incident_id: UUID) -> int:
        result = await self.session.execute(select(self.model).where(self.model.incident_id == incident_id))
        return len(result.scalars().all())
