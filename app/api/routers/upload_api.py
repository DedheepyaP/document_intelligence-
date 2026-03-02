from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pathlib import Path 
import shutil
import tempfile
import os

from app.services.upload_service import create_file_metadata, build_processing_chain
from app.services.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/file")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):    
    try:
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
             raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        filename = file.filename
        ext = Path(filename).suffix.lower()
        
        record = create_file_metadata(db, filename, user.id)

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        build_processing_chain(
            file_path=tmp_path,
            ext=ext,
            filename=filename,
            user_id=user.id
        )

        return {
            "message": "File uploaded and queued for processing",
            "file_id": record.id,
            "filename": filename
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
