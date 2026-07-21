from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.db.session import get_db
from app.schemas.stock import StockTransactionCreate, StockTransactionRead
from app.services.maintenance_service import StockService

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("/transactions", response_model=PaginatedResponse[StockTransactionRead])
async def list_transactions(
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[StockTransactionRead]:
    service = StockService(db)
    items, total = await service.list_transactions(offset=params.offset, limit=params.page_size)
    return PaginatedResponse.create([StockTransactionRead.from_orm(item) for item in items], total, params)


@router.post("/transactions", response_model=StockTransactionRead)
async def create_transaction(payload: StockTransactionCreate, db: AsyncSession = Depends(get_db)) -> StockTransactionRead:
    service = StockService(db)
    transaction = await service.create_transaction(payload.model_dump())
    return StockTransactionRead.from_orm(transaction)


@router.get("/transactions/{transaction_id}", response_model=StockTransactionRead)
async def get_transaction(transaction_id: UUID, db: AsyncSession = Depends(get_db)) -> StockTransactionRead:
    service = StockService(db)
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return StockTransactionRead.from_orm(transaction)
