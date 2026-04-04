import time

from app.tasks.celery_app import celery_app


@celery_app.task(name="submission.process_file")
def process_file_submission(submission_id: int) -> dict[str, int | str]:
    # Заглушка первого шага очереди: имитируем короткую обработку.
    time.sleep(1)
    return {"submission_id": submission_id, "result": "queued_for_analysis"}
