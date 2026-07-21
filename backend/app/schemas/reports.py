from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_type: str
    filters: dict | None = None
    format: str = "json"


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    data: list[dict] | None = None
    generated_at: datetime
    format: str


class ExportRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    report_type: str
    format: str = "csv"
    filters: dict | None = None


class SavedReportCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    report_type: str
    filters: dict | None = None


class SavedReportRead(SavedReportCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
