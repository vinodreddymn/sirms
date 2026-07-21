from datetime import date, datetime
from io import BytesIO
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.db.session import get_db
from app.models.asset import Asset, AssetMovement, MaintenanceHistory
from app.models.incident import Incident, WorkOrder
from app.schemas.reports import ExportRequest, ReportRequest, ReportResponse
from app.utils.export import CSVExporter, ExcelExporter

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORT_MODELS = {
    "asset-register": Asset,
    "incident-register": Incident,
    "maintenance-history": MaintenanceHistory,
    "work-orders": WorkOrder,
    "asset-movements": AssetMovement,
}


@router.post("/generate", response_model=ReportResponse)
async def generate_report(payload: ReportRequest, db: AsyncSession = Depends(get_db)) -> ReportResponse:
    data = await _load_report_data(db, payload.report_type, payload.filters)
    return ReportResponse(
        id=uuid4(),
        title=_report_title(payload.report_type),
        data=data,
        generated_at=datetime.utcnow(),
        format=payload.format,
    )


@router.post("/export")
async def export_report(payload: ExportRequest, db: AsyncSession = Depends(get_db)):
    data = await _load_report_data(db, payload.report_type, payload.filters)
    filename = payload.report_type.replace("_", "-")
    if payload.format.lower() == "csv":
        content = CSVExporter(filename).to_string(data)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
        )
    if payload.format.lower() in {"xlsx", "excel"}:
        content = ExcelExporter(filename).to_bytes(data)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'},
        )
    raise ValidationException("Unsupported export format")


async def _load_report_data(
    db: AsyncSession,
    report_type: str,
    filters: dict | None,
) -> list[dict]:
    model = REPORT_MODELS.get(report_type)
    if not model:
        raise ValidationException(f"Unsupported report type: {report_type}")

    query = select(model)
    for field, value in (filters or {}).items():
        if hasattr(model, field):
            query = query.where(getattr(model, field) == value)
    result = await db.execute(query.limit(5000))
    return [_model_to_dict(item) for item in result.scalars().all()]


def _model_to_dict(item) -> dict:
    values = {}
    for column in item.__table__.columns:
        value = getattr(item, column.name)
        if isinstance(value, UUID):
            value = str(value)
        elif isinstance(value, (date, datetime)):
            value = value.isoformat()
        values[column.name] = value
    return values


def _report_title(report_type: str) -> str:
    return report_type.replace("-", " ").replace("_", " ").title()
