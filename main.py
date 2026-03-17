import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from collections import defaultdict
from time import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter
from app.core import settings
from app.services.auth import get_current_user, get_current_admin_user
from app.core.telemetry import setup_telemetry

from app.api.routers.upload_api import router as upload_router
from app.api.routers.query import router as query_router
from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    force=True,
)
app = FastAPI(title="Document Intelligence API")

setup_telemetry("document-api", app=app)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

rate_limit_store = defaultdict(list)


@app.get("/")
def health_check():
    return {"status": "ok"}

protected_router = [Depends(get_current_user)]

app.include_router(auth_router)
app.include_router(upload_router, tags=["upload"], dependencies=protected_router)
app.include_router(query_router, tags=["query"], dependencies=protected_router)
app.include_router(users_router, dependencies=[Depends(get_current_admin_user)])
