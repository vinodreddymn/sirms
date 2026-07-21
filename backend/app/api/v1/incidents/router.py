from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.incident import (
    IncidentAttachmentCreate,
    IncidentAttachmentRead,
    IncidentCreate,
    IncidentRead,
    IncidentUpdateCreate,
    IncidentUpdateRead,
    IncidentUpdate,
    WorkOrderCreate,
    WorkOrderRead,
    WorkOrderTaskCreate,
    WorkOrderTaskRead,
    WorkOrderTaskUpdate,
    WorkOrderUpdate,
    IncidentAssetAction,
)
from app.services.incident_service import IncidentService

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
    dependencies=[Depends(get_current_active_user)],
)


# ---------------------------------------------------------------------------
# INCIDENT COLLECTION
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse[IncidentRead])
async def list_incidents(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[IncidentRead]:
    service = IncidentService(db)
    items, total = await service.list_incidents(offset=params.offset, limit=params.page_size, search=params.search)
    return PaginatedResponse.create([IncidentRead.from_orm(item) for item in items], total, params)


@router.post("", response_model=IncidentRead)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)) -> IncidentRead:
    service = IncidentService(db)
    try:
        incident = await service.create_incident(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return IncidentRead.from_orm(incident)


# ---------------------------------------------------------------------------
# WORK-ORDER ROUTES  (must come BEFORE /{incident_id} to avoid routing conflict)
# ---------------------------------------------------------------------------

@router.get("/work-orders", response_model=PaginatedResponse[WorkOrderRead])
async def list_work_orders(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkOrderRead]:
    service = IncidentService(db)
    items, total = await service.list_work_orders(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([WorkOrderRead.from_orm(item) for item in items], total, params)


@router.post("/work-orders", response_model=WorkOrderRead)
async def create_work_order(payload: WorkOrderCreate, db: AsyncSession = Depends(get_db)) -> WorkOrderRead:
    service = IncidentService(db)
    try:
        work_order = await service.create_work_order(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return WorkOrderRead.from_orm(work_order)


@router.put("/work-orders/tasks/{task_id}", response_model=WorkOrderTaskRead)
async def update_work_order_task(task_id: UUID, payload: WorkOrderTaskUpdate, db: AsyncSession = Depends(get_db)) -> WorkOrderTaskRead:
    service = IncidentService(db)
    task = await service.update_work_order_task(task_id, payload.model_dump(exclude_unset=True))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return WorkOrderTaskRead.from_orm(task)


@router.get("/work-orders/{work_order_id}", response_model=WorkOrderRead)
async def get_work_order(work_order_id: UUID, db: AsyncSession = Depends(get_db)) -> WorkOrderRead:
    service = IncidentService(db)
    work_order = await service.get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WorkOrderRead.from_orm(work_order)


@router.put("/work-orders/{work_order_id}", response_model=WorkOrderRead)
async def update_work_order(work_order_id: UUID, payload: WorkOrderUpdate, db: AsyncSession = Depends(get_db)) -> WorkOrderRead:
    service = IncidentService(db)
    work_order = await service.update_work_order(work_order_id, payload.model_dump(exclude_unset=True))
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    return WorkOrderRead.from_orm(work_order)


@router.get("/work-orders/{work_order_id}/tasks", response_model=PaginatedResponse[WorkOrderTaskRead])
async def list_work_order_tasks(
    work_order_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkOrderTaskRead]:
    service = IncidentService(db)
    items, total = await service.list_work_order_tasks(work_order_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([WorkOrderTaskRead.from_orm(item) for item in items], total, params)


@router.post("/work-orders/{work_order_id}/tasks", response_model=WorkOrderTaskRead)
async def create_work_order_task(work_order_id: UUID, payload: WorkOrderTaskCreate, db: AsyncSession = Depends(get_db)) -> WorkOrderTaskRead:
    service = IncidentService(db)
    task = await service.create_work_order_task(work_order_id, payload.model_dump())
    return WorkOrderTaskRead.from_orm(task)


# ---------------------------------------------------------------------------
# INDIVIDUAL INCIDENT  (parameterised — must come AFTER all static prefixes)
# ---------------------------------------------------------------------------

@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: UUID, db: AsyncSession = Depends(get_db)) -> IncidentRead:
    service = IncidentService(db)
    incident = await service.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentRead.from_orm(incident)


@router.put("/{incident_id}", response_model=IncidentRead)
async def update_incident(incident_id: UUID, payload: IncidentUpdate, db: AsyncSession = Depends(get_db)) -> IncidentRead:
    service = IncidentService(db)
    incident = await service.update_incident(incident_id, payload.model_dump(exclude_unset=True))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return IncidentRead.from_orm(incident)


@router.post("/{incident_id}/asset-actions", response_model=IncidentRead)
async def apply_incident_asset_action(
    incident_id: UUID,
    payload: IncidentAssetAction,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentRead:
    try:
        await IncidentService(db).apply_asset_action(incident_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    incident = await IncidentService(db).get_incident(incident_id)
    return IncidentRead.from_orm(incident)


@router.get("/{incident_id}/updates", response_model=PaginatedResponse[IncidentUpdateRead])
async def list_incident_updates(
    incident_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[IncidentUpdateRead]:
    service = IncidentService(db)
    items, total = await service.list_incident_updates(incident_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([IncidentUpdateRead.from_orm(item) for item in items], total, params)


@router.post("/{incident_id}/updates", response_model=IncidentUpdateRead)
async def create_incident_update(
    incident_id: UUID,
    payload: IncidentUpdateCreate,
    db: AsyncSession = Depends(get_db),
) -> IncidentUpdateRead:
    service = IncidentService(db)
    try:
        update = await service.create_incident_update(incident_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return IncidentUpdateRead.from_orm(update)


@router.get("/{incident_id}/attachments", response_model=PaginatedResponse[IncidentAttachmentRead])
async def list_incident_attachments(
    incident_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[IncidentAttachmentRead]:
    service = IncidentService(db)
    items, total = await service.list_incident_attachments(incident_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([IncidentAttachmentRead.from_orm(item) for item in items], total, params)


@router.post("/{incident_id}/attachments", response_model=IncidentAttachmentRead)
async def create_incident_attachment(
    incident_id: UUID,
    payload: IncidentAttachmentCreate,
    db: AsyncSession = Depends(get_db),
) -> IncidentAttachmentRead:
    service = IncidentService(db)
    attachment = await service.create_incident_attachment(incident_id, payload.model_dump())
    return IncidentAttachmentRead.from_orm(attachment)
