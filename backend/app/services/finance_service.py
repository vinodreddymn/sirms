from datetime import date, datetime
from typing import Any, Tuple
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common import Attachment
from app.models.finance import Expense, ExpenseAttachment
from app.repositories.finance import ExpenseRepository, ExpenseAttachmentRepository


class FinanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_expense(self, expense_id: UUID) -> Expense | None:
        repo = ExpenseRepository(self.session)
        return await repo.get_by_id(expense_id)

    async def list_expenses(self, offset: int = 0, limit: int = 100, filters: dict | None = None) -> tuple[list[Any], int]:
        # Use the view for list queries
        sql_parts = ["SELECT * FROM finance.vw_expenses WHERE 1=1"]
        where_parts: list[str] = []
        params: dict[str, Any] = {}
        if filters:
            if filters.get("project_id"):
                where_parts.append("AND project_id = :project_id")
                params["project_id"] = str(filters["project_id"])
            if filters.get("category_id"):
                where_parts.append("AND expense_category_id = :category_id")
                params["category_id"] = filters["category_id"]
            if filters.get("date_from"):
                where_parts.append("AND expense_date >= :date_from")
                params["date_from"] = date.fromisoformat(str(filters["date_from"]))
            if filters.get("date_to"):
                where_parts.append("AND expense_date <= :date_to")
                params["date_to"] = date.fromisoformat(str(filters["date_to"]))
            if filters.get("payment_mode_id"):
                where_parts.append("AND payment_mode_id = :payment_mode_id")
                params["payment_mode_id"] = filters["payment_mode_id"]
            if filters.get("payment_status_id"):
                where_parts.append("AND payment_status_id = :payment_status_id")
                params["payment_status_id"] = filters["payment_status_id"]
            if filters.get("min_amount"):
                where_parts.append("AND amount >= :min_amount")
                params["min_amount"] = filters["min_amount"]
            if filters.get("max_amount"):
                where_parts.append("AND amount <= :max_amount")
                params["max_amount"] = filters["max_amount"]
            if filters.get("search"):
                where_parts.append("AND (expense_number ILIKE :search OR description ILIKE :search OR bill_reference ILIKE :search)")
                params["search"] = f"%{filters['search']}%"

            sql_parts.extend(where_parts)

            # Sorting
            sort_by = filters.get("sort_by") or "expense_date"
            sort_dir = filters.get("sort_dir") or "desc"
            if sort_by not in ("expense_date", "amount", "created_at"):
                sort_by = "expense_date"
            if sort_dir.lower() not in ("asc", "desc"):
                sort_dir = "desc"
            sql_parts.append(f"ORDER BY {sort_by} {sort_dir}")
        else:
            sql_parts.append("ORDER BY expense_date DESC")
        sql_parts.append("OFFSET :offset LIMIT :limit")
        params["offset"] = offset
        params["limit"] = limit

        query = " ".join(sql_parts)
        result = await self.session.execute(text(query), params)
        rows = result.mappings().all()

        count_sql = "SELECT count(*) as total FROM finance.vw_expenses WHERE 1=1"
        if where_parts:
            count_sql = "SELECT count(*) as total FROM finance.vw_expenses WHERE 1=1 " + " ".join(where_parts)
        count_res = await self.session.execute(text(count_sql), params)
        total = count_res.scalar() or 0
        return rows, int(total)

    async def create_expense(self, values: dict[str, Any]) -> Expense:
        # Basic validation
        if values.get("amount") is None or values["amount"] < 0:
            raise ValueError("Amount must be zero or positive")
        # project exists
        exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM common.projects WHERE id = :id)"), {"id": str(values["project_id"])})
        if not exists:
            raise ValueError("Project not found")
        # category (master table uses expense_category_id)
        cat_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.expense_categories WHERE expense_category_id = :id)"), {"id": str(values["expense_category_id"])})
        if not cat_exists:
            raise ValueError("Expense category not found")
        # payment mode
        pm_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.payment_modes WHERE payment_mode_id = :id)"), {"id": str(values["payment_mode_id"])})
        if not pm_exists:
            raise ValueError("Payment mode not found")
        # payment status
        ps_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.payment_statuses WHERE payment_status_id = :id)"), {"id": str(values["payment_status_id"])})
        if not ps_exists:
            raise ValueError("Payment status not found")

        # business number: prefer DB generator but fall back if not configured
        if "expense_number" not in values or not values.get("expense_number"):
            try:
                gen = await self.session.scalar(text("SELECT common.generate_business_number('EXPENSE')"))
                values.setdefault("expense_number", gen)
            except Exception:
                # DB function/sequence might not be configured in some environments — rollback
                # the failed DB operation to clear the transaction and fall back to a generated value.
                try:
                    await self.session.rollback()
                except Exception:
                    pass
                values.setdefault("expense_number", f"EXP-{datetime.now():%Y%m%d%H%M%S}")
        values.setdefault("created_at", datetime.now())
        entity = Expense(**values)
        repo = ExpenseRepository(self.session)
        return await repo.create(entity)

    async def update_expense(self, expense_id: UUID, values: dict[str, Any]) -> Expense | None:
        repo = ExpenseRepository(self.session)
        expense = await repo.get_by_id(expense_id)
        if not expense:
            return None
        if values.get("amount") is not None and values["amount"] < 0:
            raise ValueError("Amount must be zero or positive")
        # Validate foreign keys if provided
        if values.get("project_id"):
            exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM common.projects WHERE id = :id)"), {"id": str(values["project_id"])})
            if not exists:
                raise ValueError("Project not found")
        if values.get("expense_category_id"):
            cat_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.expense_categories WHERE expense_category_id = :id)"), {"id": str(values["expense_category_id"])})
            if not cat_exists:
                raise ValueError("Expense category not found")
        if values.get("payment_mode_id"):
            pm_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.payment_modes WHERE payment_mode_id = :id)"), {"id": str(values["payment_mode_id"])})
            if not pm_exists:
                raise ValueError("Payment mode not found")
        if values.get("payment_status_id"):
            ps_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM master.payment_statuses WHERE payment_status_id = :id)"), {"id": str(values["payment_status_id"])})
            if not ps_exists:
                raise ValueError("Payment status not found")

        return await repo.update(expense, values)

    async def delete_expense(self, expense_id: UUID) -> bool:
        repo = ExpenseRepository(self.session)
        expense = await repo.get_by_id(expense_id)
        if not expense:
            return False
        await repo.delete(expense)
        return True

    async def create_attachment(self, expense_id: UUID, values: dict[str, Any]) -> ExpenseAttachment:
        # ensure expense exists
        expense = await self.get_expense(expense_id)
        if not expense:
            raise ValueError("Expense not found")
        # ensure attachment exists in common.attachments
        att_exists = await self.session.scalar(text("SELECT EXISTS(SELECT 1 FROM common.attachments WHERE id = :id)"), {"id": str(values["attachment_id"])})
        if not att_exists:
            raise ValueError("Attachment not found")
        values = dict(values)
        values.pop("category", None)
        values["expense_id"] = expense_id
        entity = ExpenseAttachment(**values)
        repo = ExpenseAttachmentRepository(self.session)
        return await repo.create(entity)

    async def list_attachments(self, expense_id: UUID, offset: int = 0, limit: int = 100) -> tuple[list[dict[str, Any]], int]:
        expense = await self.get_expense(expense_id)
        if not expense:
            raise ValueError("Expense not found")

        repo = ExpenseAttachmentRepository(self.session)
        items = await repo.list_by_expense(expense_id, offset=offset, limit=limit)
        total = await repo.count_by_expense(expense_id)

        result: list[dict[str, Any]] = []
        for item in items:
            attachment = await self.session.get(Attachment, item.attachment_id)
            if not attachment:
                continue
            if getattr(attachment, "is_active", True) is False:
                continue
            result.append(
                {
                    "id": getattr(item, "id", None),
                    "expense_id": getattr(item, "expense_id", expense_id),
                    "attachment_id": getattr(item, "attachment_id", None),
                    "category": None,
                    "filename": getattr(item, "file_name", None) or getattr(attachment, "file_name", None),
                    "url": getattr(item, "file_url", None) or f"/api/v1/uploads/{getattr(attachment, 'id', item.attachment_id)}/download",
                    "created_at": getattr(item, "uploaded_at", None),
                    "updated_at": None,
                }
            )

        return result, total

    async def delete_attachment(self, attachment_id: UUID) -> bool:
        repo = ExpenseAttachmentRepository(self.session)
        att = await repo.get_by_id(attachment_id)
        if not att:
            return False
        await repo.delete(att)
        return True
