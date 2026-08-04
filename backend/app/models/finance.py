from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base import Base, UUIDPrimaryKeyMixin, AuditMixin


class Expense(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "expenses"
    __table_args__ = ({"schema": "finance"},)

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("common.projects.id", ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    expense_number: Mapped[str] = mapped_column("expense_no", String(50), nullable=False, unique=True)

    expense_date: Mapped[date] = mapped_column(Date, nullable=False)

    expense_category_id: Mapped[UUID] = mapped_column(
        ForeignKey("master.expense_categories.expense_category_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text)

    bill_reference: Mapped[str | None] = mapped_column(String(120))

    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    payment_mode_id: Mapped[UUID] = mapped_column(
        ForeignKey("master.payment_modes.payment_mode_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )

    payment_status_id: Mapped[UUID] = mapped_column(
        ForeignKey("master.payment_statuses.payment_status_id", ondelete="RESTRICT", onupdate="RESTRICT"),
        nullable=False,
    )

    remarks: Mapped[str | None] = mapped_column(Text)

    # Audit fields (DB has created_at/created_by/updated_at/updated_by but no is_active)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("now()"), nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    updated_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))


class ExpenseAttachment(Base):
    __tablename__ = "expense_attachments"
    __table_args__ = ({"schema": "finance"},)

    expense_id: Mapped[UUID] = mapped_column(
        ForeignKey("finance.expenses.id", ondelete="CASCADE", onupdate="RESTRICT"), nullable=False
    )

    attachment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )

    file_name: Mapped[str | None] = mapped_column(String(255))
    file_url: Mapped[str | None] = mapped_column(Text)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=text("now()"))

    @property
    def id(self) -> UUID:
        return self.attachment_id

    @property
    def created_at(self) -> datetime | None:
        return self.uploaded_at

    @property
    def updated_at(self) -> datetime | None:
        return None
