# Apollon

MVP-платформа анализа файлов и URL на вредоносную активность.

## Реализованные шаги
- Шаг 1: backend foundation (FastAPI + PostgreSQL + Redis + MinIO)
- Шаг 2: submissions + БД + очередь (Celery skeleton)
- Шаг 3: реальный upload файла в MinIO + дедупликация по SHA-256
- Шаг 4: минимальный static analysis в worker + endpoint отчета
- Шаг 5: базовый URL analysis (submission + worker + report)
- Шаг 6: enhanced static file analysis (PE + YARA + scoring model v2)
- Шаг 7: dynamic analysis prep (safe contracts + dry-run task)

## Документация по шагам
- `STEP_01_BACKEND_FOUNDATION.md`
- `STEP_02_SUBMISSIONS_AND_QUEUE.md`
- `STEP_03_FILE_UPLOAD_TO_MINIO.md`
- `STEP_04_STATIC_ANALYSIS_WORKER.md`
- `STEP_05_URL_ANALYSIS_MVP.md`
- `STEP_06_ENHANCED_STATIC_FILE_ANALYSIS.md`
- `STEP_07_DYNAMIC_ANALYSIS_PREP.md`


## Frontend MVP
- Path: `frontend/`
- Stack: Next.js + TypeScript
- Configure API base via `frontend/.env.example` -> `.env.local`

# 1) Перейти в корень проекта
cd /workspace/apollon
# 2) Подготовить env для backend/infra
cp .env.example .env
# 3) Запустить backend-часть (API + worker + postgres + redis + minio)
docker compose -f infra/docker-compose.yml up -d --build
# 4) Применить миграции БД
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
# 5) Проверить, что backend поднят
docker compose -f infra/docker-compose.yml ps
curl http://localhost:8000/
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
# 6) Подготовить frontend env
cd /workspace/apollon/frontend
cp .env.example .env.local
# 7) Установить зависимости frontend
npm install
# 8) Запустить frontend (dev)
npm run dev
# 9) Открыть в браузере
# frontend: http://localhost:3000
# backend api: http://localhost:8000
# minio console: http://localhost:9001
# 10) Остановка всего backend-стека (из /workspace/apollon)
cd /workspace/apollon
docker compose -f infra/docker-compose.yml down
