from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AttachmentCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    checksum: str | None = None


class AttachmentRead(AttachmentCreate):
    id: UUID
    created_at: datetime


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    size: int
    url: str
    created_at: datetime
