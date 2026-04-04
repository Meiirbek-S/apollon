from celery import Celery

from app.core.config import settings

# include гарантирует импорт модуля с task-декораторами при старте worker.
celery_app = Celery(
    "apollon_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.submission_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
)
