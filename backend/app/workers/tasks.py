from datetime import datetime

from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.run_static_analysis")
def run_static_analysis(submission_id: str) -> dict:
    return {"submission_id": submission_id, "kind": "static", "completed_at": datetime.utcnow().isoformat()}


@celery_app.task(name="app.workers.tasks.run_url_analysis")
def run_url_analysis(submission_id: str) -> dict:
    return {"submission_id": submission_id, "kind": "url", "completed_at": datetime.utcnow().isoformat()}


@celery_app.task(name="app.workers.tasks.run_dynamic_analysis")
def run_dynamic_analysis(submission_id: str) -> dict:
    return {"submission_id": submission_id, "kind": "dynamic", "completed_at": datetime.utcnow().isoformat()}
