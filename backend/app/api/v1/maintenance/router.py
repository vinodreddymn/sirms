from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.maintenance import (
    ChecklistItemCreate,
    ChecklistItemRead,
    ChecklistItemUpdate,
    MaintenanceChecklistCreate,
    MaintenanceChecklistRead,
    MaintenanceChecklistUpdate,
    MaintenanceHistoryCreate,
    MaintenanceHistoryRead,
    MaintenanceHistoryUpdate,
    MaintenanceScheduleCreate,
    MaintenanceScheduleRead,
    MaintenanceScheduleUpdate,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("/checklists", response_model=PaginatedResponse[MaintenanceChecklistRead])
async def list_checklists(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MaintenanceChecklistRead]:
    service = MaintenanceService(db)
    items, total = await service.list_checklists(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([MaintenanceChecklistRead.from_orm(item) for item in items], total, params)


@router.post("/checklists", response_model=MaintenanceChecklistRead)
async def create_checklist(payload: MaintenanceChecklistCreate, db: AsyncSession = Depends(get_db)) -> MaintenanceChecklistRead:
    service = MaintenanceService(db)
    checklist = await service.create_checklist(payload.model_dump())
    return MaintenanceChecklistRead.from_orm(checklist)


@router.get("/checklists/{checklist_id}", response_model=MaintenanceChecklistRead)
async def get_checklist(checklist_id: UUID, db: AsyncSession = Depends(get_db)) -> MaintenanceChecklistRead:
    service = MaintenanceService(db)
    checklist = await service.get_checklist(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return MaintenanceChecklistRead.from_orm(checklist)


@router.put("/checklists/{checklist_id}", response_model=MaintenanceChecklistRead)
async def update_checklist(checklist_id: UUID, payload: MaintenanceChecklistUpdate, db: AsyncSession = Depends(get_db)) -> MaintenanceChecklistRead:
    service = MaintenanceService(db)
    checklist = await service.update_checklist(checklist_id, payload.model_dump(exclude_unset=True))
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    return MaintenanceChecklistRead.from_orm(checklist)


@router.get("/checklists/{checklist_id}/items", response_model=PaginatedResponse[ChecklistItemRead])
async def list_checklist_items(
    checklist_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ChecklistItemRead]:
    service = MaintenanceService(db)
    items, total = await service.list_checklist_items(checklist_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([ChecklistItemRead.from_orm(item) for item in items], total, params)


@router.post("/checklists/{checklist_id}/items", response_model=ChecklistItemRead)
async def create_checklist_item(checklist_id: UUID, payload: ChecklistItemCreate, db: AsyncSession = Depends(get_db)) -> ChecklistItemRead:
    service = MaintenanceService(db)
    item = await service.create_checklist_item(checklist_id, payload.model_dump())
    return ChecklistItemRead.from_orm(item)


@router.put("/checklists/items/{item_id}", response_model=ChecklistItemRead)
async def update_checklist_item(item_id: UUID, payload: ChecklistItemUpdate, db: AsyncSession = Depends(get_db)) -> ChecklistItemRead:
    service = MaintenanceService(db)
    item = await service.update_checklist_item(item_id, payload.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ChecklistItemRead.from_orm(item)


@router.get("/schedules", response_model=PaginatedResponse[MaintenanceScheduleRead])
async def list_schedules(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MaintenanceScheduleRead]:
    service = MaintenanceService(db)
    items, total = await service.list_schedules(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([MaintenanceScheduleRead.from_orm(item) for item in items], total, params)


@router.post("/schedules", response_model=MaintenanceScheduleRead)
async def create_schedule(payload: MaintenanceScheduleCreate, db: AsyncSession = Depends(get_db)) -> MaintenanceScheduleRead:
    service = MaintenanceService(db)
    schedule = await service.create_schedule(payload.model_dump())
    return MaintenanceScheduleRead.from_orm(schedule)


@router.get("/schedules/{schedule_id}", response_model=MaintenanceScheduleRead)
async def get_schedule(schedule_id: UUID, db: AsyncSession = Depends(get_db)) -> MaintenanceScheduleRead:
    service = MaintenanceService(db)
    schedule = await service.get_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return MaintenanceScheduleRead.from_orm(schedule)


@router.put("/schedules/{schedule_id}", response_model=MaintenanceScheduleRead)
async def update_schedule(schedule_id: UUID, payload: MaintenanceScheduleUpdate, db: AsyncSession = Depends(get_db)) -> MaintenanceScheduleRead:
    service = MaintenanceService(db)
    schedule = await service.update_schedule(schedule_id, payload.model_dump(exclude_unset=True))
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return MaintenanceScheduleRead.from_orm(schedule)


@router.get("/history", response_model=PaginatedResponse[MaintenanceHistoryRead])
async def list_history(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MaintenanceHistoryRead]:
    service = MaintenanceService(db)
    items, total = await service.list_history(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([MaintenanceHistoryRead.from_orm(item) for item in items], total, params)


@router.post("/history", response_model=MaintenanceHistoryRead)
async def create_history(payload: MaintenanceHistoryCreate, db: AsyncSession = Depends(get_db)) -> MaintenanceHistoryRead:
    service = MaintenanceService(db)
    history = await service.create_history(payload.model_dump())
    return MaintenanceHistoryRead.from_orm(history)


@router.get("/schedules/{schedule_id}/history", response_model=PaginatedResponse[MaintenanceHistoryRead])
async def list_schedule_history(
    schedule_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MaintenanceHistoryRead]:
    service = MaintenanceService(db)
    items, total = await service.list_schedule_history(schedule_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([MaintenanceHistoryRead.from_orm(item) for item in items], total, params)
