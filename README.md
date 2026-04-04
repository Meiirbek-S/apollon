# Apollon

MVP-платформа анализа файлов и URL на вредоносную активность.

## Реализованные шаги
- Шаг 1: backend foundation (FastAPI + PostgreSQL + Redis + MinIO)
- Шаг 2: submissions + БД + очередь (Celery skeleton)
- Шаг 3: реальный upload файла в MinIO + дедупликация по SHA-256

## Документация по шагам
- `STEP_01_BACKEND_FOUNDATION.md`
- `STEP_02_SUBMISSIONS_AND_QUEUE.md`
- `STEP_03_FILE_UPLOAD_TO_MINIO.md`
