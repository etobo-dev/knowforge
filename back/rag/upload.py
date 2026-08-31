import hashlib
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from config import get_settings
from db.models import Document
from db.repositories.documents import db_find_by_user_and_content_hash
from db.services.document_upload import handle_existing_document, handle_new_document


def _check_content_type(content_type: str) -> None:
    settings = get_settings()
    if content_type not in settings.allowed_mime_types:
        raise ValueError(
            f"Unsupported file type: {content_type}. "
            f"Allowed: {', '.join(sorted(settings.allowed_mime_types))}"
        )


def _check_file_size(size: int) -> None:
    settings = get_settings()
    if size > settings.max_file_size:
        raise ValueError(
            f"File too large: {size / 1024 / 1024:.1f} MB. "
            f"Max: {settings.max_file_size / 1024 / 1024:.0f} MB"
        )


async def upload_document(
    file: UploadFile,
    user_id: uuid.UUID,
    db: Session,
) -> tuple[Document, bool]:
    if file.content_type is None:
        raise ValueError("Missing content type")
    _check_content_type(file.content_type)

    content = await file.read()
    content_hash = hashlib.sha256(content).hexdigest()
    size = len(content)
    _check_file_size(size)

    existing_document = db_find_by_user_and_content_hash(db, user_id, content_hash)

    if existing_document:
        return handle_existing_document(db, existing_document, content)

    return handle_new_document(
        db=db,
        file=file,
        user_id=user_id,
        content_hash=content_hash,
        size=size,
        content=content,
    )
