import logging
import os
import shutil
import uuid
from pathlib import Path
from celery import chain
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.config import settings
from app.database import SessionLocal
from app.models.file_metadata import FileMetadata
from app.services.doclingocr_service import extract_text
from app.services.transcription_service import transcribe_audio
from app.services.embedding_service import index_documents

logger = logging.getLogger(__name__)

DOCUMENT_TYPES = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
AUDIO_TYPES = {".wav", ".mp3"}


def get_user_files(db: Session, user_id: int) -> list[FileMetadata]:
    from sqlalchemy import func
    latest = (
        db.query(func.max(FileMetadata.id).label("id"))
        .filter(FileMetadata.user_id == user_id)
        .group_by(FileMetadata.filename)
        .subquery()
    )
    return (
        db.query(FileMetadata)
        .join(latest, FileMetadata.id == latest.c.id)
        .order_by(FileMetadata.upload_date.desc())
        .all()
    )

# def get_user_files(db: Session, user_id: int) -> list[FileMetadata]:
#     return (
#         db.query(FileMetadata)
#         .filter(FileMetadata.user_id == user_id)
#         .order_by(FileMetadata.filename, FileMetadata.upload_date.desc())
#         .distinct(FileMetadata.filename)
#         .all()
#     )

def save_upload_file(file, ext: str) -> str:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = str(upload_dir / f"{uuid.uuid4()}{ext}")
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return dest


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def extract_content_task(self, file_path: str, ext: str, filename: str, user_id: int):
    try:
        if ext in DOCUMENT_TYPES:
            extracted_data = extract_text(file_path, filename)
        elif ext in AUDIO_TYPES:
            extracted_data = transcribe_audio(file_path, filename)

        logger.info(f"Extraction complete for '{filename}'")
        return {
            "extracted_data": extracted_data,
            "filename": filename,
            "user_id": user_id,
            "file_path": file_path
        }
    except Exception as exc:
        logger.error(f"Extraction failed for '{filename}': {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def index_content_task(self, prev_result: dict):
    filename = prev_result["filename"]
    try:
        index_documents(
            prev_result["extracted_data"],
            filename,
            prev_result["user_id"]
        )
        return {
            "file_path": prev_result["file_path"],
            "filename": filename,
            "user_id": prev_result["user_id"],
        }
    except Exception as exc:
        logger.error(f"Indexing failed for '{filename}': {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def final_task(prev_result: dict):

    filename = prev_result.get("filename", "")
    user_id = prev_result.get("user_id")
    file_path = prev_result.get("file_path", "")

    db = SessionLocal()
    try:
        record = FileMetadata(filename=filename, user_id=user_id)
        db.add(record)
        db.commit()
        logger.info(f"Metadata saved for '{filename}'")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save metadata for '{filename}': {e}")
    finally:
        db.close()

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Deleted temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not delete temp file {file_path}: {e}")


# Chain

def build_processing_chain(file_path: str, ext: str, filename: str, user_id: int):
    return chain(
        extract_content_task.s(file_path, ext, filename, user_id),
        index_content_task.s(),
        final_task.s(),
    ).delay()
