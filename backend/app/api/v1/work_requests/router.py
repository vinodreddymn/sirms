from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.work_request import (
    WorkRequestAttachmentCreate,
    WorkRequestAttachmentRead,
    WorkRequestCreate,
    WorkRequestRead,
    WorkRequestUpdateCreate,
    WorkRequestUpdateRead,
    WorkRequestUpdate,
    WorkRequestAssetAction,
)
from app.services.incident_service import IncidentService

router = APIRouter(
    prefix="/work-requests",
    tags=["Work Requests"],
    dependencies=[Depends(get_current_active_user)],
)


# ---------------------------------------------------------------------------
# WORK REQUEST COLLECTION
# ---------------------------------------------------------------------------

@router.get("", response_model=PaginatedResponse[WorkRequestRead])
async def list_work_requests(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkRequestRead]:
    service = IncidentService(db)
    items, total = await service.list_incidents(offset=params.offset, limit=params.page_size, search=params.search)
    return PaginatedResponse.create([WorkRequestRead.model_validate(item) for item in items], total, params)


@router.post("", response_model=WorkRequestRead)
async def create_work_request(payload: WorkRequestCreate, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> WorkRequestRead:
    service = IncidentService(db)
    try:
        incident = await service.create_incident(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    # Log activity
    try:
        from app.services.activity_service import ActivityService
        await ActivityService(db).work_request_created(incident.id, incident.work_request_number, project_id=incident.project_id, performed_by=current_user.id)
    except Exception:
        pass
    return WorkRequestRead.model_validate(incident)


# ---------------------------------------------------------------------------
# INDIVIDUAL WORK REQUEST
# ---------------------------------------------------------------------------

@router.get("/{work_request_id}", response_model=WorkRequestRead)
async def get_work_request(work_request_id: UUID, db: AsyncSession = Depends(get_db)) -> WorkRequestRead:
    service = IncidentService(db)
    incident = await service.get_incident(work_request_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Work Request not found")
    return WorkRequestRead.model_validate(incident)


@router.put("/{work_request_id}", response_model=WorkRequestRead)
async def update_work_request(work_request_id: UUID, payload: WorkRequestUpdate, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> WorkRequestRead:
    service = IncidentService(db)
    incident = await service.update_incident(work_request_id, payload.model_dump(exclude_unset=True), current_user.id)
    if not incident:
        raise HTTPException(status_code=404, detail="Work Request not found")
    return WorkRequestRead.model_validate(incident)


@router.post("/{work_request_id}/asset-actions", response_model=WorkRequestRead)
async def apply_work_request_asset_action(
    work_request_id: UUID,
    payload: WorkRequestAssetAction,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WorkRequestRead:
    try:
        from app.services.asset_service import AssetService
        await AssetService(db).apply_asset_action(work_request_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    incident = await IncidentService(db).get_incident(work_request_id)
    return WorkRequestRead.model_validate(incident)


@router.get("/{work_request_id}/updates", response_model=PaginatedResponse[WorkRequestUpdateRead])
async def list_work_request_updates(
    work_request_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[WorkRequestUpdateRead]:
    service = IncidentService(db)
    items, total = await service.list_incident_updates(work_request_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([WorkRequestUpdateRead.model_validate(item) for item in items], total, params)


@router.post("/{work_request_id}/updates", response_model=WorkRequestUpdateRead)
async def create_work_request_update(
    work_request_id: UUID,
    payload: WorkRequestUpdateCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WorkRequestUpdateRead:
    service = IncidentService(db)
    try:
        update = await service.create_incident_update(work_request_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return WorkRequestUpdateRead.model_validate(update)


@router.get("/{work_request_id}/attachments", response_model=list[WorkRequestAttachmentRead])
async def list_work_request_attachments(work_request_id: UUID, db: AsyncSession = Depends(get_db)) -> list[WorkRequestAttachmentRead]:
    service = IncidentService(db)
    items = await service.list_incident_attachments(work_request_id)
    return [WorkRequestAttachmentRead.model_validate(item) for item in items]


@router.post("/{work_request_id}/attachments", response_model=WorkRequestAttachmentRead)
async def create_work_request_attachment(
    work_request_id: UUID, payload: WorkRequestAttachmentCreate, db: AsyncSession = Depends(get_db)
) -> WorkRequestAttachmentRead:
    service = IncidentService(db)
    try:
        attachment = await service.create_incident_attachment(work_request_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return WorkRequestAttachmentRead.model_validate(attachment)
