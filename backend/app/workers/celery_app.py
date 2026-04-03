from celery import Celery

from app.core.config import settings

celery_app = Celery("aegisscan", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_routes = {
    "app.workers.tasks.run_static_analysis": {"queue": "static"},
    "app.workers.tasks.run_url_analysis": {"queue": "url"},
    "app.workers.tasks.run_dynamic_analysis": {"queue": "dynamic"},
}
