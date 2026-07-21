from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.models.master import LocationType, PositionType, AssetCategory, AssetSubcategory, Manufacturer, AssetModel, AssetStatus, AssetCondition, AssetLifecycle, MaintenanceType, FailureCategory, RootCauseCategory, IncidentStatus, IncidentPriority, IncidentCategory, WorkOrderStatus, RelationshipType, DocumentType, PhotoType, ProjectType, UserRoleTemplate, SpecificationDefinition, MovementType, StockTransactionType
from app.schemas.master import (
    LookupCreate, LookupRead, LookupUpdate,
    PositionTemplateCreate, PositionTemplateNodeCreate, PositionTemplateNodeRead,
    PositionTemplateNodeUpdate, PositionTemplateRead, PositionTemplateUpdate,
    SpecificationDefinitionCreate, SpecificationDefinitionRead, SpecificationDefinitionUpdate,
)
from app.services.master_service import MasterService

router = APIRouter(prefix="/master", tags=["Master"])

lookup_models = {
    "location-types": LocationType,
    "position-types": PositionType,
    "asset-categories": AssetCategory,
    "asset-subcategories": AssetSubcategory,
    "manufacturers": Manufacturer,
    "asset-models": AssetModel,
    "asset-status": AssetStatus,
    "asset-condition": AssetCondition,
    "asset-lifecycle": AssetLifecycle,
    "maintenance-types": MaintenanceType,
    "failure-categories": FailureCategory,
    "root-cause-categories": RootCauseCategory,
    "incident-status": IncidentStatus,
    "incident-priority": IncidentPriority,
    "incident-categories": IncidentCategory,
    "work-order-status": WorkOrderStatus,
    "relationship-types": RelationshipType,
    "document-types": DocumentType,
    "photo-types": PhotoType,
    "project-types": ProjectType,
    "user-role-templates": UserRoleTemplate,
    "movement-types": MovementType,
    "stock-transaction-types": StockTransactionType,
}


def get_model_for_table(table_name: str):
    model = lookup_models.get(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Lookup table not found")
    return model


# ─── Specification Definitions ────────────────────────────────────────────────

@router.get("/specification-definitions", response_model=PaginatedResponse[SpecificationDefinitionRead])
async def list_specification_definitions(
    category_id: int | None = None,
    subcategory_id: int | None = None,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SpecificationDefinitionRead]:
    service = MasterService(db)
    items, total = await service.list_specification_definitions(
        offset=params.offset,
        limit=params.page_size,
        category_id=category_id,
        subcategory_id=subcategory_id,
    )
    return PaginatedResponse.create([SpecificationDefinitionRead.model_validate(item) for item in items], total, params)


@router.post("/specification-definitions", response_model=SpecificationDefinitionRead)
async def create_specification_definition(
    payload: SpecificationDefinitionCreate,
    db: AsyncSession = Depends(get_db),
) -> SpecificationDefinitionRead:
    service = MasterService(db)
    try:
        item = await service.create_specification_definition(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return SpecificationDefinitionRead.model_validate(item)


@router.put("/specification-definitions/{definition_id}", response_model=SpecificationDefinitionRead)
async def update_specification_definition(
    definition_id: int,
    payload: SpecificationDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
) -> SpecificationDefinitionRead:
    service = MasterService(db)
    try:
        item = await service.update_specification_definition(definition_id, payload.model_dump(exclude_unset=True))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not item:
        raise HTTPException(status_code=404, detail="Specification definition not found")
    return SpecificationDefinitionRead.model_validate(item)


# ─── Position Templates ───────────────────────────────────────────────────────

@router.get("/position-templates", response_model=PaginatedResponse[PositionTemplateRead])
async def list_position_templates(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PositionTemplateRead]:
    service = MasterService(db)
    rows, total = await service.list_position_templates(offset=params.offset, limit=params.page_size)
    items = []
    for row in rows:
        tmpl = row["template"]
        read = PositionTemplateRead.model_validate(tmpl)
        read.node_count = row["node_count"]
        items.append(read)
    return PaginatedResponse.create(items, total, params)


@router.post("/position-templates", response_model=PositionTemplateRead, status_code=201)
async def create_position_template(
    payload: PositionTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> PositionTemplateRead:
    service = MasterService(db)
    template = await service.create_position_template(payload.model_dump())
    return PositionTemplateRead.model_validate(template)


@router.get("/position-templates/{template_id}", response_model=PositionTemplateRead)
async def get_position_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
) -> PositionTemplateRead:
    service = MasterService(db)
    data = await service.get_position_template_with_nodes(template_id)
    if not data:
        raise HTTPException(status_code=404, detail="Position template not found")
    tmpl = data["template"]
    read = PositionTemplateRead.model_validate(tmpl)
    read.nodes = [PositionTemplateNodeRead.model_validate(n) for n in data["nodes"]]
    read.node_count = data["node_count"]
    return read


@router.put("/position-templates/{template_id}", response_model=PositionTemplateRead)
async def update_position_template(
    template_id: int,
    payload: PositionTemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> PositionTemplateRead:
    service = MasterService(db)
    template = await service.update_position_template(template_id, payload.model_dump(exclude_unset=True))
    if not template:
        raise HTTPException(status_code=404, detail="Position template not found")
    return PositionTemplateRead.model_validate(template)


@router.get("/position-templates/{template_id}/nodes", response_model=list[PositionTemplateNodeRead])
async def list_template_nodes(
    template_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[PositionTemplateNodeRead]:
    service = MasterService(db)
    nodes = await service.get_template_nodes(template_id)
    return [PositionTemplateNodeRead.model_validate(n) for n in nodes]


@router.post("/position-templates/{template_id}/nodes", response_model=PositionTemplateNodeRead, status_code=201)
async def add_template_node(
    template_id: int,
    payload: PositionTemplateNodeCreate,
    db: AsyncSession = Depends(get_db),
) -> PositionTemplateNodeRead:
    service = MasterService(db)
    node = await service.add_template_node(template_id, payload.model_dump())
    return PositionTemplateNodeRead.model_validate(node)


@router.put("/position-template-nodes/{node_id}", response_model=PositionTemplateNodeRead)
async def update_template_node(
    node_id: int,
    payload: PositionTemplateNodeUpdate,
    db: AsyncSession = Depends(get_db),
) -> PositionTemplateNodeRead:
    service = MasterService(db)
    node = await service.update_template_node(node_id, payload.model_dump(exclude_unset=True))
    if not node:
        raise HTTPException(status_code=404, detail="Template node not found")
    return PositionTemplateNodeRead.model_validate(node)


@router.delete("/position-template-nodes/{node_id}", status_code=204)
async def delete_template_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    service = MasterService(db)
    deleted = await service.delete_template_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template node not found")


# ─── Generic Lookup CRUD ──────────────────────────────────────────────────────

@router.get("/{table_name}", response_model=PaginatedResponse[LookupRead])
async def list_lookup(
    table_name: str,
    asset_category_id: int | None = None,
    asset_subcategory_id: int | None = None,
    manufacturer_id: int | None = None,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[LookupRead]:
    model = get_model_for_table(table_name)
    service = MasterService(db)
    if table_name == "manufacturers":
        items, total = await service.list_manufacturers_for_asset(
            category_id=asset_category_id, subcategory_id=asset_subcategory_id, offset=params.offset, limit=params.page_size,
        )
        return PaginatedResponse.create([LookupRead.from_orm(item) for item in items], total, params)
    filters: dict[str, int] = {}
    if table_name == "asset-subcategories" and asset_category_id is not None:
        filters["asset_category_id"] = asset_category_id
    if table_name == "asset-models" and manufacturer_id is not None:
        filters["manufacturer_id"] = manufacturer_id
    if table_name == "asset-models" and asset_subcategory_id is not None:
        filters["asset_subcategory_id"] = asset_subcategory_id
    items, total = await service.list_lookups(
        model,
        offset=params.offset,
        limit=params.page_size,
        filters=filters,
    )
    return PaginatedResponse.create([LookupRead.from_orm(item) for item in items], total, params)


@router.post("/{table_name}", response_model=LookupRead)
async def create_lookup(table_name: str, payload: LookupCreate, db: AsyncSession = Depends(get_db)) -> LookupRead:
    model = get_model_for_table(table_name)
    service = MasterService(db)
    item = await service.create_lookup(model, payload.model_dump())
    return LookupRead.from_orm(item)


@router.get("/{table_name}/{item_id}", response_model=LookupRead)
async def get_lookup(table_name: str, item_id: int, db: AsyncSession = Depends(get_db)) -> LookupRead:
    model = get_model_for_table(table_name)
    service = MasterService(db)
    item = await service.get_lookup(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return LookupRead.from_orm(item)


@router.put("/{table_name}/{item_id}", response_model=LookupRead)
async def update_lookup(table_name: str, item_id: int, payload: LookupUpdate, db: AsyncSession = Depends(get_db)) -> LookupRead:
    model = get_model_for_table(table_name)
    service = MasterService(db)
    item = await service.update_lookup(model, item_id, payload.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return LookupRead.from_orm(item)
