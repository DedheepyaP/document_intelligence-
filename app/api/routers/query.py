from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.services import query_rag
from app.models.user import User
from app.services.auth import get_current_user
from app.core.rate_limiter import limiter
from app.database import get_db

router = APIRouter(prefix="/rag", tags=["query"])


@router.post("/query")
@limiter.limit("10/minute")
def ask_question(
    request: Request,
    question: str = Query(...),
    filename: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not question.strip():
        raise HTTPException(400, "Question cannot be empty")

    result = query_rag(
        question=question,
        role=user.role_obj.name,
        filename_filter=filename,
        user_id=user.id,
        db=db,
    )

    return result
