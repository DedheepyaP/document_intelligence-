from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session

from app.services import query_rag
from app.models.user import User
from app.services.auth import get_current_user
from app.core.rate_limiter import limiter, redis_client
from app.database import get_db
from app.core.config import settings
from app.core.callbacks import TokenUsageCallbackHandler
from datetime import datetime

router = APIRouter(prefix="/rag", tags=["query"])


@router.post("/query")
@limiter.limit("10/minute")
async def ask_question(
    request: Request,
    question: str = Query(...),
    filename: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not question.strip():
        raise HTTPException(400, "Question cannot be empty")

    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    redis_key = f"token_usage:{user.id}:{today_str}"
    
    current_tokens = redis_client.get(redis_key)
    current_tokens = int(current_tokens) if current_tokens else 0
    
    if current_tokens >= settings.DAILY_TOKEN_LIMIT:
        raise HTTPException(429, f"Daily token limit of {settings.DAILY_TOKEN_LIMIT} exceeded.")

    token_callback = TokenUsageCallbackHandler()

    result = query_rag(
        question=question,
        role=user.role_obj.name,
        filename_filter=filename,
        user_id=user.id,
        db=db,
        callbacks=[token_callback]
    )
    
    if token_callback.total_tokens > 0:
        redis_client.incrby(redis_key, token_callback.total_tokens)
        redis_client.expire(redis_key, 86400)

    return result
