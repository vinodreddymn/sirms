from typing import Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import Expense, ExpenseAttachment


class ExpenseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> Expense | None:
        return await self.session.get(Expense, entity_id)

    async def create(self, entity: Expense) -> Expense:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def update(self, entity: Expense, values: dict[str, Any]) -> Expense:
        for key, value in values.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        return entity

    async def delete(self, entity: Expense) -> None:
        await self.session.delete(entity)
        await self.session.flush()


class ExpenseAttachmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, entity: ExpenseAttachment) -> ExpenseAttachment:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> ExpenseAttachment | None:
        return await self.session.get(ExpenseAttachment, entity_id)

    async def delete(self, entity: ExpenseAttachment) -> None:
        await self.session.delete(entity)
        await self.session.flush()

    async def list_by_expense(self, expense_id: UUID, offset: int = 0, limit: int = 100) -> list[ExpenseAttachment]:
        result = await self.session.execute(select(ExpenseAttachment).where(ExpenseAttachment.expense_id == expense_id).offset(offset).limit(limit))
        return result.scalars().all()

    async def count_by_expense(self, expense_id: UUID) -> int:
        result = await self.session.execute(select(ExpenseAttachment).where(ExpenseAttachment.expense_id == expense_id))
        return len(result.scalars().all())
