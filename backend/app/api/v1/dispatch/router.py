"""API router for Dispatch module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.security import User
from app.schemas.dispatch import (
    DispatchCreate,
    DispatchDetailsRead,
    DispatchItemRead,
    DispatchRead,
    DispatchUpdate,
    ReceiveItemRequest,
)
from app.services.dispatch_service import DispatchService


router = APIRouter(
    prefix="/dispatches",
    tags=["Dispatches"],
    dependencies=[Depends(get_current_active_user)],
)


@router.get("", response_model=PaginatedResponse[DispatchRead])
async def list_dispatches(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DispatchRead]:
    service = DispatchService(db)
    items, total = await service.list_dispatches(
        offset=params.offset,
        limit=params.page_size,
        search=params.search,
    )
    return PaginatedResponse.create([DispatchRead(**item) for item in items], total, params)


@router.get("/{dispatch_id}", response_model=DispatchDetailsRead)
async def get_dispatch(
    dispatch_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DispatchDetailsRead:
    service = DispatchService(db)
    details = await service.get_dispatch_details(dispatch_id)
    if not details:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    return DispatchDetailsRead(**details)


@router.post("", response_model=DispatchRead)
async def create_dispatch(
    payload: DispatchCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DispatchRead:
    service = DispatchService(db)
    try:
        dispatch = await service.create_dispatch(payload.model_dump(), current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    return await get_dispatch(dispatch.id, db)


@router.put("/{dispatch_id}", response_model=DispatchRead)
async def update_dispatch(
    dispatch_id: UUID,
    payload: DispatchUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DispatchRead:
    service = DispatchService(db)
    try:
        dispatch = await service.update_dispatch(dispatch_id, payload.model_dump(exclude_unset=True), current_user.id)
        if not dispatch:
            raise HTTPException(status_code=404, detail="Dispatch not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    return await get_dispatch(dispatch_id, db)


@router.post("/{dispatch_id}/submit", response_model=DispatchRead)
async def submit_dispatch(
    dispatch_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DispatchRead:
    import structlog
    logger = structlog.get_logger()
    logger.info("submit_dispatch_called", dispatch_id=str(dispatch_id))
    service = DispatchService(db)
    try:
        dispatch = await service.submit_dispatch(dispatch_id, current_user.id)
        if not dispatch:
            raise HTTPException(status_code=404, detail="Dispatch not found")
    except ValueError as e:
        logger.error("submit_dispatch_error", error=str(e), dispatch_id=str(dispatch_id))
        raise HTTPException(status_code=422, detail=str(e))
        
    return await get_dispatch(dispatch_id, db)


@router.post("/{dispatch_id}/items/{item_id}/receive", response_model=DispatchItemRead)
async def receive_item(
    dispatch_id: UUID,
    item_id: UUID,
    payload: ReceiveItemRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DispatchItemRead:
    import structlog
    logger = structlog.get_logger()
    logger.info("receive_item_called", dispatch_id=str(dispatch_id), item_id=str(item_id), payload=payload.model_dump(mode="json"))
    service = DispatchService(db)
    try:
        item = await service.receive_item(item_id, dispatch_id, payload.model_dump(), current_user.id)
        if not item:
            raise HTTPException(status_code=404, detail="Dispatch item not found")
    except ValueError as e:
        logger.error("receive_item_error", error=str(e), dispatch_id=str(dispatch_id), item_id=str(item_id))
        raise HTTPException(status_code=422, detail=str(e))
        
    return DispatchItemRead.model_validate(item, from_attributes=True)

