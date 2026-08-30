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
async def update_incident(incident_id: UUID, payload: IncidentUpdate, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> IncidentRead:
    service = IncidentService(db)
    incident = await service.update_incident(incident_id, payload.model_dump(exclude_unset=True), current_user.id)
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
        from app.services.asset_service import AssetService
        await AssetService(db).apply_asset_action(incident_id, payload.model_dump(), current_user.id)
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
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> IncidentUpdateRead:
    service = IncidentService(db)
    try:
        update = await service.create_incident_update(incident_id, payload.model_dump(), current_user.id)
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
