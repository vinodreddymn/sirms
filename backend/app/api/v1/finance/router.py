from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginatedResponse, PaginationParams, pagination_params
from app.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.schemas.finance import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    ExpenseAttachmentCreate,
    ExpenseAttachmentResponse,
)
from app.services.finance_service import FinanceService


router = APIRouter(prefix="/expenses", tags=["Expenses"], dependencies=[Depends(get_current_active_user)])


@router.get("", response_model=PaginatedResponse[ExpenseResponse])
async def list_expenses(
    params: PaginationParams = Depends(pagination_params),
    category_id: str | None = Query(default=None),
    payment_status_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ExpenseResponse]:
    service = FinanceService(db)
    filters = {
        "search": params.search,
        "limit": params.page_size,
        "offset": params.offset,
        "category_id": category_id,
        "payment_status_id": payment_status_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    items, total = await service.list_expenses(offset=params.offset, limit=params.page_size, filters=filters)
    # rows from view are mapping objects; pass through as dicts to Pydantic
    return PaginatedResponse.create([ExpenseResponse.model_validate(item) for item in items], total, params)


@router.post("", response_model=ExpenseResponse)
async def create_expense(payload: ExpenseCreate, db: AsyncSession = Depends(get_db)) -> ExpenseResponse:
    try:
        expense = await FinanceService(db).create_expense(payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ExpenseResponse.model_validate(expense)


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: UUID, db: AsyncSession = Depends(get_db)) -> ExpenseResponse:
    expense = await FinanceService(db).get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(expense_id: UUID, payload: ExpenseUpdate, db: AsyncSession = Depends(get_db)) -> ExpenseResponse:
    try:
        expense = await FinanceService(db).update_expense(expense_id, payload.model_dump(exclude_unset=True))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}")
async def delete_expense(expense_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    ok = await FinanceService(db).delete_expense(expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "ok"}


@router.get("/{expense_id}/attachments", response_model=PaginatedResponse[ExpenseAttachmentResponse])
async def list_expense_attachments(
    expense_id: UUID,
    params: PaginationParams = Depends(pagination_params),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ExpenseAttachmentResponse]:
    try:
        items, total = await FinanceService(db).list_attachments(expense_id, offset=params.offset, limit=params.page_size)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return PaginatedResponse.create([ExpenseAttachmentResponse.model_validate(item) for item in items], total, params)


@router.post("/{expense_id}/attachments", response_model=ExpenseAttachmentResponse)
async def upload_attachment(expense_id: UUID, payload: ExpenseAttachmentCreate, db: AsyncSession = Depends(get_db)) -> ExpenseAttachmentResponse:
    try:
        att = await FinanceService(db).create_attachment(expense_id, payload.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ExpenseAttachmentResponse.model_validate(att)


@router.delete("/attachments/{attachment_id}")
async def delete_attachment(
    attachment_id: UUID,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    # Only system administrators may delete attachments
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Permission denied")
    ok = await FinanceService(db).delete_attachment(attachment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"status": "ok"}
