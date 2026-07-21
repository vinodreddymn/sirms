import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundException, ValidationException
from app.db.session import get_db
from app.models.common import Attachment
from app.schemas.uploads import UploadResponse
from app.utils.helpers import sanitize_filename

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)) -> UploadResponse:
    settings = get_settings()
    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise ValidationException(f"File exceeds {settings.max_upload_size_mb} MB upload limit")

    original_name = sanitize_filename(file.filename or "upload.bin")
    storage_dir = Path(settings.upload_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    storage_name = f"{uuid4()}_{original_name}"
    storage_path = storage_dir / storage_name
    storage_path.write_bytes(content)

    attachment = Attachment(
        file_name=original_name,
        file_path=str(storage_path),
        mime_type=file.content_type,
        file_size_bytes=len(content),
        checksum=hashlib.sha256(content).hexdigest(),
    )
    db.add(attachment)
    await db.flush()
    await db.refresh(attachment)
    return _attachment_to_upload_response(attachment)


@router.get("/{file_id}", response_model=UploadResponse)
async def get_file(file_id: UUID, db: AsyncSession = Depends(get_db)) -> UploadResponse:
    attachment = await _get_attachment_or_404(db, file_id)
    return _attachment_to_upload_response(attachment)


@router.get("/{file_id}/download")
async def download_file(file_id: UUID, db: AsyncSession = Depends(get_db)):
    attachment = await _get_attachment_or_404(db, file_id)
    path = Path(attachment.file_path)
    if not path.exists() or not path.is_file():
        raise NotFoundException("Stored file not found")
    return FileResponse(
        path,
        media_type=attachment.mime_type,
        filename=attachment.file_name,
    )


async def _get_attachment_or_404(db: AsyncSession, file_id: UUID) -> Attachment:
    attachment = await db.get(Attachment, file_id)
    if not attachment or not attachment.is_active:
        raise NotFoundException("Attachment not found")
    return attachment


def _attachment_to_upload_response(attachment: Attachment) -> UploadResponse:
    return UploadResponse(
        id=attachment.id,
        filename=attachment.file_name,
        size=attachment.file_size_bytes or 0,
        url=f"/api/v1/uploads/{attachment.id}/download",
        created_at=attachment.created_at,
    )
