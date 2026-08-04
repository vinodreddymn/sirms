from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.finance_service import FinanceService


@pytest.mark.asyncio
async def test_list_attachments_returns_attachment_details(monkeypatch):
    expense_id = uuid4()
    attachment_id = uuid4()

    class DummySession:
        async def get(self, model, entity_id):
            return SimpleNamespace(id=entity_id, file_name="receipt.pdf", file_path="/tmp/receipt.pdf", mime_type="application/pdf")

    class FakeAttachmentRepository:
        def __init__(self, session):
            self.session = session

        async def list_by_expense(self, expense_id, offset=0, limit=100):
            return [SimpleNamespace(attachment_id=attachment_id)]

        async def count_by_expense(self, expense_id):
            return 1

    async def fake_get_expense(self, expense_id):
        return object()

    monkeypatch.setattr(FinanceService, "get_expense", fake_get_expense)
    monkeypatch.setattr("app.services.finance_service.ExpenseAttachmentRepository", FakeAttachmentRepository)

    service = FinanceService(DummySession())
    items, total = await service.list_attachments(expense_id, offset=0, limit=10)

    assert total == 1
    assert len(items) == 1
    assert items[0]["attachment_id"] == attachment_id
    assert items[0]["filename"] == "receipt.pdf"
    assert items[0]["url"].endswith("/download")
