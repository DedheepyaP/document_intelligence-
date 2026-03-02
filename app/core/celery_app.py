from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "document_system",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.services.upload_service"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_pool="solo",
    worker_prefetch_multiplier=1,
)
