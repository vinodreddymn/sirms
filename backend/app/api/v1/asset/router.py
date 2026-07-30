from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.repositories.asset import AssetListFilters
from app.schemas.asset import (
    AssetCreate,
    AssetDetailsRead,
    AssetDocumentRead,
    AssetInstallationCreate,
    AssetInstallationInfoRead,
    AssetInstallationRead,
    AssetListRead,
    AssetLookupRead,
    AssetMaintenanceHistoryRead,
    AssetMaintenanceScheduleRead,
    AssetMovementCreate,
    AssetMovementHistoryRead,
    AssetMovementListRead,
    AssetMovementRead,
    AssetPhotoRead,
    AssetRelationshipRead,
    AssetSpecificationCreate,
    AssetSpecificationDefinitionRead,
    AssetSpecificationRead,
    AssetSpecificationValueRead,
    AssetSummaryRead,
    AssetUpdate,
    AssetFieldNoteCreate,
    AssetFieldNoteRead,
    AssetReplacementRead,
    AssetReplacementRequest,
    AssetTimelineEventRead,
    ReplacementAssetRead,
    RepairHistoryCreate,
    RepairHistoryRead,
    AssetUninstall,
    AssetTransfer,
    AssetDispatch,
    AssetReceive,
)
from app.services.asset_service import AssetService

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
    dependencies=[Depends(get_current_active_user)],
)


@dataclass(slots=True)
class AssetQueryFilters:
    project_id: UUID | None = None
    category_id: int | None = None
    subcategory_id: int | None = None
    manufacturer_id: int | None = None
    model_id: int | None = None
    status_id: int | None = None
    condition_id: int | None = None
    lifecycle_id: int | None = None
    location_id: UUID | None = None
    warranty_status: str | None = None


def asset_query_filters(
    project_id: UUID | None = None,
    category_id: int | None = None,
    subcategory_id: int | None = None,
    manufacturer_id: int | None = None,
    model_id: int | None = None,
    status_id: int | None = None,
    condition_id: int | None = None,
    lifecycle_id: int | None = None,
    location_id: UUID | None = None,
    warranty_status: str | None = Query(default=None, pattern="^(active|expired|expiring_soon)$"),
) -> AssetQueryFilters:
    return AssetQueryFilters(
        project_id=project_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        manufacturer_id=manufacturer_id,
        model_id=model_id,
        status_id=status_id,
        condition_id=condition_id,
        lifecycle_id=lifecycle_id,
        location_id=location_id,
        warranty_status=warranty_status,
    )


def _to_repo_filters(filters: AssetQueryFilters) -> AssetListFilters:
    return AssetListFilters(
        project_id=filters.project_id,
        category_id=filters.category_id,
        subcategory_id=filters.subcategory_id,
        manufacturer_id=filters.manufacturer_id,
        model_id=filters.model_id,
        status_id=filters.status_id,
        condition_id=filters.condition_id,
        lifecycle_id=filters.lifecycle_id,
        location_id=filters.location_id,
        warranty_status=filters.warranty_status,
    )


def _asset_lookup(identifier: str | int | UUID | None, code: str | None, name: str | None) -> AssetLookupRead | None:
    if name is None:
        return None
    return AssetLookupRead(id=identifier, code=code, name=name)


def _coerce_specification_value(item: dict[str, object]) -> object:
    if item.get("value_text") is not None:
        return item["value_text"]
    if item.get("value_number") is not None:
        return item["value_number"]
    if item.get("value_boolean") is not None:
        return item["value_boolean"]
    if item.get("value_date") is not None:
        return item["value_date"]
    return item.get("value_json")


def _classify_relationship(
    relationship: AssetRelationshipRead,
    *,
    power_sources: list[AssetRelationshipRead],
    network_connections: list[AssetRelationshipRead],
    parent_assets: list[AssetRelationshipRead],
    child_assets: list[AssetRelationshipRead],
    related_assets: list[AssetRelationshipRead],
) -> None:
    label = (relationship.relationship_type or "").lower()
    if "power" in label:
        power_sources.append(relationship)
        return
    if "network" in label or "connected" in label:
        network_connections.append(relationship)
        return
    if "parent" in label:
        (child_assets if relationship.direction == "outgoing" else parent_assets).append(relationship)
        return
    if "parent" in label or (relationship.direction == "incoming" and "child" in label):
        parent_assets.append(relationship)
        return
    if "child" in label or (relationship.direction == "outgoing" and "parent" in label):
        child_assets.append(relationship)
        return
    related_assets.append(relationship)


@router.get("/summary", response_model=AssetSummaryRead)
async def get_asset_summary(
    params: PaginationParams = Depends(pagination_params),
    filters: AssetQueryFilters = Depends(asset_query_filters),
    db: AsyncSession = Depends(get_db),
) -> AssetSummaryRead:
    service = AssetService(db)
    summary = await service.get_asset_summary(search=params.search, filters=_to_repo_filters(filters))
    return AssetSummaryRead(**summary)


@router.get("/movements", response_model=PaginatedResponse[AssetMovementListRead])
async def list_all_asset_movements(params: PaginationParams = Depends(pagination_params), db: AsyncSession = Depends(get_db)) -> PaginatedResponse[AssetMovementListRead]:
    items, total = await AssetService(db).list_all_movements(params.search or "", params.offset, params.page_size)
    return PaginatedResponse.create([AssetMovementListRead(**item) for item in items], total, params)


@router.get("/export")
async def export_assets(
    params: PaginationParams = Depends(pagination_params),
    filters: AssetQueryFilters = Depends(asset_query_filters),
    db: AsyncSession = Depends(get_db),
) -> Response:
    service = AssetService(db)
    content = await service.export_assets(search=params.search, filters=_to_repo_filters(filters))
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="assets.csv"'},
    )


@router.get("/specification-definitions", response_model=list[AssetSpecificationDefinitionRead])
async def list_specification_definitions(
    category_id: int | None = None,
    subcategory_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[AssetSpecificationDefinitionRead]:
    service = AssetService(db)
    items = await service.list_specification_definitions(
        category_id=category_id,
        subcategory_id=subcategory_id,
    )
    return [AssetSpecificationDefinitionRead(**item) for item in items]


@router.get("/{asset_id}/replacement-candidates", response_model=list[ReplacementAssetRead])
async def list_replacement_candidates(
    asset_id: UUID,
    search: str = Query(default="", min_length=0, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> list[ReplacementAssetRead]:
    items = await AssetService(db).list_replacement_candidates(asset_id, search)
    return [ReplacementAssetRead(**item) for item in items]


@router.get("", response_model=PaginatedResponse[AssetListRead])
async def list_assets(
    params: PaginationParams = Depends(pagination_params),
    filters: AssetQueryFilters = Depends(asset_query_filters),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AssetListRead]:
    service = AssetService(db)
    items, total = await service.list_assets(
        page=params.page,
        page_size=params.page_size,
        sort=params.sort,
        order=params.order,
        search=params.search,
        filters=_to_repo_filters(filters),
    )
    return PaginatedResponse.create([AssetListRead(**item) for item in items], total, params)


@router.post("", response_model=AssetDetailsRead)
async def create_asset(payload: AssetCreate, db: AsyncSession = Depends(get_db)) -> AssetDetailsRead:
    service = AssetService(db)
    try:
        asset = await service.create_asset(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    details = await service.get_asset_details(asset.id)
    if not details:
        raise HTTPException(status_code=500, detail="Failed to load created asset")
    return _build_asset_details(details)


@router.get("/{asset_id}", response_model=AssetDetailsRead)
async def get_asset(asset_id: UUID, db: AsyncSession = Depends(get_db)) -> AssetDetailsRead:
    service = AssetService(db)
    details = await service.get_asset_details(asset_id)
    if not details:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _build_asset_details(details)


@router.put("/{asset_id}", response_model=AssetDetailsRead)
async def update_asset(asset_id: UUID, payload: AssetUpdate, db: AsyncSession = Depends(get_db)) -> AssetDetailsRead:
    service = AssetService(db)
    try:
        asset = await service.update_asset(asset_id, payload.model_dump(exclude_unset=True))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    details = await service.get_asset_details(asset.id)
    if not details:
        raise HTTPException(status_code=500, detail="Failed to load updated asset")
    return _build_asset_details(details)


@router.delete("/{asset_id}", status_code=405)
async def delete_asset(asset_id: UUID) -> None:
    raise HTTPException(status_code=405, detail="Asset records are permanent. Update its operational status instead.")


@router.post("/{asset_id}/repairs", response_model=RepairHistoryRead)
async def add_repair_history(asset_id: UUID, payload: RepairHistoryCreate, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> RepairHistoryRead:
    try:
        repair = await AssetService(db).add_repair_history(asset_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RepairHistoryRead.model_validate(repair)


@router.post("/{asset_id}/replacement", response_model=AssetReplacementRead)
async def replace_asset(asset_id: UUID, payload: AssetReplacementRequest, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> AssetReplacementRead:
    try:
        replacement = await AssetService(db).replace_asset(asset_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return AssetReplacementRead.model_validate(replacement)


@router.get("/{asset_id}/timeline", response_model=list[AssetTimelineEventRead])
async def get_asset_timeline(asset_id: UUID, db: AsyncSession = Depends(get_db)) -> list[AssetTimelineEventRead]:
    return [AssetTimelineEventRead.model_validate(event) for event in await AssetService(db).list_timeline(asset_id)]


@router.post("/{asset_id}/field-notes", response_model=AssetFieldNoteRead)
async def add_field_note(asset_id: UUID, payload: AssetFieldNoteCreate, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> AssetFieldNoteRead:
    try:
        note = await AssetService(db).add_field_note(asset_id, payload.note, payload.observed_at, current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return AssetFieldNoteRead.model_validate(note)


@router.get("/{asset_id}/specifications", response_model=PaginatedResponse[AssetSpecificationRead])
async def list_asset_specifications(
    asset_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AssetSpecificationRead]:
    service = AssetService(db)
    items, total = await service.list_asset_specifications(asset_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([AssetSpecificationRead.model_validate(item) for item in items], total, params)


@router.post("/{asset_id}/specifications", response_model=AssetSpecificationRead)
async def create_asset_specification(asset_id: UUID, payload: AssetSpecificationCreate, db: AsyncSession = Depends(get_db)) -> AssetSpecificationRead:
    service = AssetService(db)
    spec = await service.create_asset_specification(asset_id, payload.model_dump())
    return AssetSpecificationRead.model_validate(spec)


@router.get("/{asset_id}/installations", response_model=PaginatedResponse[AssetInstallationRead])
async def list_asset_installations(
    asset_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AssetInstallationRead]:
    service = AssetService(db)
    items, total = await service.list_asset_installations(asset_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([AssetInstallationRead.model_validate(item) for item in items], total, params)


@router.post("/{asset_id}/installations", response_model=AssetInstallationRead)
async def create_asset_installation(asset_id: UUID, payload: AssetInstallationCreate, db: AsyncSession = Depends(get_db)) -> AssetInstallationRead:
    service = AssetService(db)
    installation = await service.create_asset_installation(asset_id, payload.model_dump())
    return AssetInstallationRead.model_validate(installation)


@router.get("/{asset_id}/movements", response_model=PaginatedResponse[AssetMovementRead])
async def list_asset_movements(
    asset_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AssetMovementRead]:
    service = AssetService(db)
    items, total = await service.list_asset_movements(asset_id, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([AssetMovementRead.model_validate(item) for item in items], total, params)


@router.post("/{asset_id}/movements", response_model=AssetMovementRead)
async def create_asset_movement(asset_id: UUID, payload: AssetMovementCreate, db: AsyncSession = Depends(get_db)) -> AssetMovementRead:
    service = AssetService(db)
    movement = await service.create_asset_movement(asset_id, payload.model_dump())
    return AssetMovementRead.model_validate(movement)


@router.post("/{asset_id}/uninstall", response_model=AssetInstallationRead)
async def uninstall_asset(asset_id: UUID, payload: AssetUninstall, db: AsyncSession = Depends(get_db)) -> AssetInstallationRead:
    service = AssetService(db)
    try:
        installation = await service.uninstall_asset(asset_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not installation:
        raise HTTPException(status_code=404, detail="No active installation found")
    return AssetInstallationRead.model_validate(installation)


@router.post("/{asset_id}/transfer", response_model=AssetDetailsRead)
async def transfer_asset(asset_id: UUID, payload: AssetTransfer, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> AssetDetailsRead:
    service = AssetService(db)
    try:
        asset = await service.transfer_asset(asset_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    details = await service.get_asset_details(asset.id)
    if not details:
        raise HTTPException(status_code=500, detail="Failed to load transferred asset")
    return _build_asset_details(details)


@router.post("/{asset_id}/dispatch", response_model=RepairHistoryRead)
async def dispatch_asset_for_repair(asset_id: UUID, payload: AssetDispatch, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> RepairHistoryRead:
    service = AssetService(db)
    try:
        repair = await service.dispatch_asset_for_repair(asset_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return RepairHistoryRead.model_validate(repair)


@router.post("/{asset_id}/receive", response_model=RepairHistoryRead)
async def receive_asset_from_repair(asset_id: UUID, payload: AssetReceive, current_user=Depends(get_current_active_user), db: AsyncSession = Depends(get_db)) -> RepairHistoryRead:
    service = AssetService(db)
    try:
        repair = await service.receive_asset_from_repair(asset_id, payload.model_dump(), current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return RepairHistoryRead.model_validate(repair)


def _build_asset_details(details: dict[str, object]) -> AssetDetailsRead:
    basic_information = AssetListRead(
        id=details["id"],
        asset_number=details["asset_number"],
        category=details["category_name"],
        subcategory=details["subcategory_name"],
        manufacturer=details["manufacturer_name"],
        model=details["model_name"],
        serial_number=details["serial_number"],
        barcode=details["barcode"],
        status=details["status_name"],
        condition=details["condition_name"],
        lifecycle=details["lifecycle_name"],
        current_location=details["current_location_name"],
        purchase_date=details["purchase_date"],
        warranty_expiry=details["warranty_expiry"],
        remarks=details["remarks"],
        created_at=details["created_at"],
        updated_at=details["updated_at"],
    )
    relationships_raw = details.get("relationships", [])
    power_sources: list[AssetRelationshipRead] = []
    network_connections: list[AssetRelationshipRead] = []
    parent_assets: list[AssetRelationshipRead] = []
    child_assets: list[AssetRelationshipRead] = []
    related_assets: list[AssetRelationshipRead] = []
    for item in relationships_raw:
        relationship = AssetRelationshipRead(**item)
        _classify_relationship(
            relationship,
            power_sources=power_sources,
            network_connections=network_connections,
            parent_assets=parent_assets,
            child_assets=child_assets,
            related_assets=related_assets,
        )
    installation = None
    if details.get("installation_position_id") or details.get("current_location_id") or details.get("installation_status"):
        installation = AssetInstallationInfoRead(
            location_id=details.get("current_location_id"),
            location_name=details.get("current_location_name"),
            position_id=details.get("installation_position_id"),
            position_name=details.get("installation_position_name"),
            installed_on=details.get("installation_date"),
            removed_on=details.get("installation_removed_on"),
            current_flag=bool(details.get("installation_current_flag", False)),
            installation_status=details.get("installation_status"),
            remarks=details.get("installation_remarks"),
            power_source=details.get("position_power_source"),
            electrical_panel=details.get("position_electrical_panel"),
            network_switch=details.get("position_network_switch"),
            switch_port=details.get("position_switch_port"),
            patch_panel=details.get("position_patch_panel"),
            junction_box=details.get("position_junction_box"),
            mounting_details=details.get("position_mounting_details"),
            infrastructure_details=details.get("position_infrastructure_details"),
        )
    return AssetDetailsRead(
        id=details["id"],
        asset_role=details.get("asset_role", "SPARE"),
        basic_information=basic_information,
        qr_code=details.get("qr_code"),
        project=AssetLookupRead(
            id=details["project_id"],
            code=details["project_code"],
            name=details["project_name"],
        ),
        status=AssetLookupRead(
            id=details["asset_status_id"],
            code=details["status_code"],
            name=details["status_name"],
        ),
        condition=_asset_lookup(
            details.get("asset_condition_id"),
            details.get("condition_code"),
            details.get("condition_name"),
        ),
        lifecycle=_asset_lookup(
            details.get("asset_lifecycle_id"),
            details.get("lifecycle_code"),
            details.get("lifecycle_name"),
        ),
        category=AssetLookupRead(
            id=details["asset_category_id"],
            code=details["category_code"],
            name=details["category_name"],
        ),
        subcategory=_asset_lookup(
            details.get("asset_subcategory_id"),
            details.get("subcategory_code"),
            details.get("subcategory_name"),
        ),
        manufacturer=_asset_lookup(
            details.get("manufacturer_id"),
            details.get("manufacturer_code"),
            details.get("manufacturer_name"),
        ),
        model=_asset_lookup(
            details.get("asset_model_id"),
            details.get("model_code"),
            details.get("model_name"),
        ),
        installation=installation,
        specifications=[
            AssetSpecificationValueRead(
                id=item["id"],
                specification_definition_id=item["specification_definition_id"],
                specification_name=item["specification_name"],
                code=item["code"],
                data_type=item["data_type"],
                unit=item["unit"],
                value=_coerce_specification_value(item),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
            for item in details.get("specifications", [])
        ],
        power_sources=power_sources,
        network_connections=network_connections,
        parent_assets=parent_assets,
        child_assets=child_assets,
        related_assets=related_assets,
        movement_history=[AssetMovementHistoryRead(**item) for item in details.get("movement_history", [])],
        documents=[AssetDocumentRead(**item) for item in details.get("documents", [])],
        photos=[AssetPhotoRead(**item) for item in details.get("photos", [])],
        maintenance_schedules=[
            AssetMaintenanceScheduleRead(**item) for item in details.get("maintenance_schedules", [])
        ],
        maintenance_history=[
            AssetMaintenanceHistoryRead(**item) for item in details.get("maintenance_history", [])
        ],
    )
