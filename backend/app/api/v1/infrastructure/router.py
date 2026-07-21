from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.models.infrastructure import Location, LocationPosition
from app.schemas.infrastructure import (
    LocationCreate,
    LocationPositionCreate,
    LocationPositionRead,
    LocationPositionUpdate,
    LocationRead,
    LocationSearchRead,
    LocationTreeNode,
    LocationUpdate,
    PositionPreviewItem,
)
from app.services.infrastructure_service import InfrastructureService

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure"])


@router.get("/locations/tree", response_model=list[LocationTreeNode])
async def get_location_tree(db: AsyncSession = Depends(get_db)) -> list[LocationTreeNode]:
    service = InfrastructureService(db)
    return await service.get_location_tree()


@router.get("/position-templates/{template_id}/preview", response_model=list[PositionPreviewItem])
async def preview_template_positions(
    template_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[PositionPreviewItem]:
    """Return positions that would be auto-created from this template (for frontend preview)."""
    service = InfrastructureService(db)
    return await service.preview_template_positions(template_id)


@router.get("/locations", response_model=PaginatedResponse[LocationRead])
async def list_locations(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LocationRead]:
    service = InfrastructureService(db)
    items, total = await service.list_locations(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([LocationRead.from_orm(item) for item in items], total, params)


@router.get("/locations/search", response_model=list[LocationSearchRead])
async def search_locations(
    search: str = Query(min_length=2, max_length=100),
    project_id: UUID | None = None,
    limit: int = Query(default=25, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[LocationSearchRead]:
    service = InfrastructureService(db)
    return await service.search_locations(search=search.strip(), project_id=project_id, limit=limit)


@router.post("/locations", response_model=LocationRead)
async def create_location(payload: LocationCreate, db: AsyncSession = Depends(get_db)) -> LocationRead:
    service = InfrastructureService(db)
    location = await service.create_location(payload.model_dump())
    return LocationRead.from_orm(location)


@router.get("/locations/{location_id}", response_model=LocationRead)
async def get_location(location_id: UUID, db: AsyncSession = Depends(get_db)) -> LocationRead:
    service = InfrastructureService(db)
    location = await service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRead.from_orm(location)


@router.put("/locations/{location_id}", response_model=LocationRead)
async def update_location(location_id: UUID, payload: LocationUpdate, db: AsyncSession = Depends(get_db)) -> LocationRead:
    service = InfrastructureService(db)
    location = await service.update_location(location_id, payload.model_dump(exclude_unset=True))
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRead.from_orm(location)


@router.get("/locations/{location_id}/positions", response_model=PaginatedResponse[LocationPositionRead])
async def list_location_positions(
    location_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LocationPositionRead]:
    service = InfrastructureService(db)
    items, total = await service.list_positions(location_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([LocationPositionRead.from_orm(item) for item in items], total, params)


@router.post("/locations/{location_id}/positions", response_model=LocationPositionRead)
async def create_location_position(
    location_id: UUID,
    payload: LocationPositionCreate,
    db: AsyncSession = Depends(get_db),
) -> LocationPositionRead:
    service = InfrastructureService(db)
    values = payload.model_dump()
    values["location_id"] = location_id
    position = await service.create_position(values)
    return LocationPositionRead.from_orm(position)


@router.put("/positions/{position_id}", response_model=LocationPositionRead)
async def update_location_position(
    position_id: UUID,
    payload: LocationPositionUpdate,
    db: AsyncSession = Depends(get_db),
) -> LocationPositionRead:
    service = InfrastructureService(db)
    position = await service.update_position(position_id, payload.model_dump(exclude_unset=True))
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return LocationPositionRead.from_orm(position)
