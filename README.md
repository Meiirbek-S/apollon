# AegisScan

Учебный проект веб-системы для анализа файлов и URL на признаки вредоносной активности.

## Цели MVP
- загрузка файла и URL;
- статический и URL-анализ;
- оркестрация динамического анализа только через VirtualBox;
- risk scoring: SAFE / SUSPICIOUS / MALWARE-LIKE;
- формирование отчета через API.

## Безопасность (обязательно)
- sample **никогда** не исполняется на хосте;
- запуск только в изолированной VM;
- snapshot rollback после каждого анализа;
- no shared folders / no clipboard / no drag&drop для sandbox VM.

## Структура
- `backend/app/api/v1/endpoints` — REST API
- `backend/app/services` — static/url/dynamic/scoring сервисы
- `backend/app/workers` — Celery задачи
- `backend/app/models` и `backend/app/db` — заготовка persistence слоя
- `rules/yara` — YARA правила
- `scripts` — скрипты и заметки по VM

## Быстрый старт (локально)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Документация API: http://127.0.0.1:8000/docs

## Docker Compose
```bash
cd infrastructure
docker compose up --build
```

## Доступные endpoint'ы
- `POST /api/v1/submit/file`
- `POST /api/v1/submit/url`
- `GET /api/v1/submissions/{id}`
- `GET /api/v1/submissions/{id}/status`
- `GET /api/v1/submissions/{id}/report`
- `GET /api/v1/submissions/{id}/artifacts`
- `GET /api/v1/hash/{sha256}`
- `POST /api/v1/admin/reanalyze/{id}`
- `GET /api/v1/metrics`
- `GET /api/v1/health`

## Важно
Текущая реализация — инженерный каркас. Следующий шаг: подключение реальной БД, хранилища артефактов и завершение пайплайна анализаторов.
