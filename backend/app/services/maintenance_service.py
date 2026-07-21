from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import ChecklistItem, MaintenanceChecklist, MaintenanceHistory, MaintenanceSchedule, StockTransaction
from app.repositories.maintenance import (
    ChecklistItemRepository,
    MaintenanceHistoryRepository,
    MaintenanceRepository,
    MaintenanceScheduleRepository,
    StockTransactionRepository,
)


class MaintenanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_checklist(self, checklist_id: UUID) -> MaintenanceChecklist | None:
        repo = MaintenanceRepository(MaintenanceChecklist, self.session)
        return await repo.get_by_id(checklist_id)

    async def list_checklists(self, offset: int = 0, limit: int = 100) -> tuple[list[MaintenanceChecklist], int]:
        repo = MaintenanceRepository(MaintenanceChecklist, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def create_checklist(self, values: dict[str, Any]) -> MaintenanceChecklist:
        entity = MaintenanceChecklist(**values)
        repo = MaintenanceRepository(MaintenanceChecklist, self.session)
        return await repo.create(entity)

    async def update_checklist(self, checklist_id: UUID, values: dict[str, Any]) -> MaintenanceChecklist | None:
        repo = MaintenanceRepository(MaintenanceChecklist, self.session)
        checklist = await repo.get_by_id(checklist_id)
        if not checklist:
            return None
        return await repo.update(checklist, values)

    async def list_checklist_items(self, checklist_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[ChecklistItem], int]:
        repo = ChecklistItemRepository(ChecklistItem, self.session)
        items = await repo.list_by_checklist(checklist_id, offset=offset, limit=limit)
        return items, await repo.count_by_checklist(checklist_id)

    async def create_checklist_item(self, checklist_id: UUID, values: dict[str, Any]) -> ChecklistItem:
        values["checklist_id"] = checklist_id
        entity = ChecklistItem(**values)
        repo = ChecklistItemRepository(ChecklistItem, self.session)
        return await repo.create(entity)

    async def update_checklist_item(self, item_id: UUID, values: dict[str, Any]) -> ChecklistItem | None:
        repo = ChecklistItemRepository(ChecklistItem, self.session)
        item = await repo.get_by_id(item_id)
        if not item:
            return None
        return await repo.update(item, values)

    async def get_schedule(self, schedule_id: UUID) -> MaintenanceSchedule | None:
        repo = MaintenanceScheduleRepository(MaintenanceSchedule, self.session)
        return await repo.get_by_id(schedule_id)

    async def list_schedules(self, offset: int = 0, limit: int = 100) -> tuple[list[MaintenanceSchedule], int]:
        repo = MaintenanceScheduleRepository(MaintenanceSchedule, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def create_schedule(self, values: dict[str, Any]) -> MaintenanceSchedule:
        entity = MaintenanceSchedule(**values)
        repo = MaintenanceScheduleRepository(MaintenanceSchedule, self.session)
        return await repo.create(entity)

    async def update_schedule(self, schedule_id: UUID, values: dict[str, Any]) -> MaintenanceSchedule | None:
        repo = MaintenanceScheduleRepository(MaintenanceSchedule, self.session)
        schedule = await repo.get_by_id(schedule_id)
        if not schedule:
            return None
        return await repo.update(schedule, values)

    async def list_history(self, offset: int = 0, limit: int = 100) -> tuple[list[MaintenanceHistory], int]:
        repo = MaintenanceHistoryRepository(MaintenanceHistory, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def create_history(self, values: dict[str, Any]) -> MaintenanceHistory:
        entity = MaintenanceHistory(**values)
        repo = MaintenanceHistoryRepository(MaintenanceHistory, self.session)
        return await repo.create(entity)

    async def list_schedule_history(self, schedule_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[MaintenanceHistory], int]:
        repo = MaintenanceHistoryRepository(MaintenanceHistory, self.session)
        items = await repo.list_by_schedule(schedule_id, offset=offset, limit=limit)
        return items, await repo.count_by_schedule(schedule_id)


class StockService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_transaction(self, transaction_id: UUID) -> StockTransaction | None:
        repo = StockTransactionRepository(StockTransaction, self.session)
        return await repo.get_by_id(transaction_id)

    async def list_transactions(self, offset: int = 0, limit: int = 100) -> tuple[list[StockTransaction], int]:
        repo = StockTransactionRepository(StockTransaction, self.session)
        items = await repo.list(offset=offset, limit=limit)
        return items, await repo.count()

    async def create_transaction(self, values: dict[str, Any]) -> StockTransaction:
        entity = StockTransaction(**values)
        repo = StockTransactionRepository(StockTransaction, self.session)
        return await repo.create(entity)
