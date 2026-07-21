from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.models.common import Customer, Project, Vendor
from app.schemas.common import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    VendorCreate,
    VendorRead,
    VendorUpdate,
)
from app.services.common_service import CommonService

router = APIRouter(prefix="/common", tags=["Common"])


@router.get("/customers", response_model=PaginatedResponse[CustomerRead])
async def list_customers(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CustomerRead]:
    service = CommonService(db)
    items, total = await service.list_entities(Customer, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([CustomerRead.from_orm(item) for item in items], total, params)


@router.post("/customers", response_model=CustomerRead)
async def create_customer(payload: CustomerCreate, db: AsyncSession = Depends(get_db)) -> CustomerRead:
    service = CommonService(db)
    customer = await service.create_entity(Customer, payload.model_dump())
    return CustomerRead.from_orm(customer)


@router.get("/customers/{customer_id}", response_model=CustomerRead)
async def get_customer(customer_id: UUID, db: AsyncSession = Depends(get_db)) -> CustomerRead:
    service = CommonService(db)
    customer = await service.get_entity(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerRead.from_orm(customer)


@router.put("/customers/{customer_id}", response_model=CustomerRead)
async def update_customer(customer_id: UUID, payload: CustomerUpdate, db: AsyncSession = Depends(get_db)) -> CustomerRead:
    service = CommonService(db)
    customer = await service.update_entity(Customer, customer_id, payload.model_dump(exclude_unset=True))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerRead.from_orm(customer)


@router.get("/projects", response_model=PaginatedResponse[ProjectRead])
async def list_projects(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProjectRead]:
    service = CommonService(db)
    items, total = await service.list_entities(Project, offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([ProjectRead.from_orm(item) for item in items], total, params)


@router.post("/projects", response_model=ProjectRead)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)) -> ProjectRead:
    service = CommonService(db)
    project = await service.create_entity(Project, payload.model_dump())
    return ProjectRead.from_orm(project)


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)) -> ProjectRead:
    service = CommonService(db)
    project = await service.get_entity(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.from_orm(project)


@router.put("/projects/{project_id}", response_model=ProjectRead)
async def update_project(project_id: UUID, payload: ProjectUpdate, db: AsyncSession = Depends(get_db)) -> ProjectRead:
    service = CommonService(db)
    project = await service.update_entity(Project, project_id, payload.model_dump(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.from_orm(project)


@router.get("/vendors", response_model=PaginatedResponse[VendorRead])
async def list_vendors(
    asset_category_id: int | None = None,
    asset_subcategory_id: int | None = None,
    manufacturer_id: int | None = None,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VendorRead]:
    service = CommonService(db)
    items, total = await service.list_vendors_for_asset(
        category_id=asset_category_id, subcategory_id=asset_subcategory_id, manufacturer_id=manufacturer_id,
        offset=params.offset, limit=params.page_size,
    )
    return PaginatedResponse.create([VendorRead.from_orm(item) for item in items], total, params)


@router.post("/vendors", response_model=VendorRead)
async def create_vendor(payload: VendorCreate, db: AsyncSession = Depends(get_db)) -> VendorRead:
    service = CommonService(db)
    vendor = await service.create_entity(Vendor, payload.model_dump())
    return VendorRead.from_orm(vendor)


@router.get("/vendors/{vendor_id}", response_model=VendorRead)
async def get_vendor(vendor_id: UUID, db: AsyncSession = Depends(get_db)) -> VendorRead:
    service = CommonService(db)
    vendor = await service.get_entity(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorRead.from_orm(vendor)


@router.put("/vendors/{vendor_id}", response_model=VendorRead)
async def update_vendor(vendor_id: UUID, payload: VendorUpdate, db: AsyncSession = Depends(get_db)) -> VendorRead:
    service = CommonService(db)
    vendor = await service.update_entity(Vendor, vendor_id, payload.model_dump(exclude_unset=True))
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return VendorRead.from_orm(vendor)
