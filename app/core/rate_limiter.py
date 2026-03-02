from fastapi import Request
from slowapi import Limiter
from jose import jwt, JWTError

from app.core.config import settings


def get_user_id_from_request(request: Request) -> str:
    
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass

    return request.client.host


limiter = Limiter(key_func=get_user_id_from_request)
