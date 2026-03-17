from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pathlib import Path

from app.services.upload_service import (
    save_upload_file,
    get_user_files,
    build_processing_chain,
)
from app.services.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/upload", tags=["upload"])


@router.get("/files")
def list_user_files(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_user_files(db, user.id)
    return [{"id": r.id, "filename": r.filename, "uploaded_at": r.upload_date} for r in records]


@router.post("/file")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    try:
        filename = file.filename
        ext = Path(filename).suffix.lower()

        tmp_path = save_upload_file(file, ext)
        build_processing_chain(file_path=tmp_path, ext=ext, filename=filename, user_id=user.id)

        return {
            "message": "File uploaded and queued for processing",
            "filename": filename,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
