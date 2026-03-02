import logging
import os
from celery import chain
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.models.file_metadata import FileMetadata
# from app.services.ocr_service import extract_text
from app.services.doclingocr_service import extract_text
from app.services.transcription_service import transcribe_audio
from app.services.embedding_service import index_documents

logger = logging.getLogger(__name__)

DOCUMENT_TYPES = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
AUDIO_TYPES = {".wav", ".mp3"}



def create_file_metadata(db: Session, filename: str, user_id: int) -> FileMetadata:
    record = FileMetadata(filename=filename, user_id=user_id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


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
        chunks = index_documents(
            prev_result["extracted_data"],
            filename,
            prev_result["user_id"]
        )
        # logger.info(f"Indexed '{filename}' {chunks} chunks created")
        return {"file_path": prev_result["file_path"], "filename": filename}
    except Exception as exc:
        logger.error(f"Indexing failed for '{filename}': {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def cleanup_task(prev_result: dict):
    file_path = prev_result.get("file_path", "")
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
        cleanup_task.s()
    ).delay()
