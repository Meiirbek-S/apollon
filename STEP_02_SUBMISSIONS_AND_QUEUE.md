# Шаг 2: Submissions + БД + очередь (без анализа файлов)

Цель шага:
- добавить таблицу `submissions`,
- сделать API для создания задачи анализа файла (метаданные),
- подключить Celery worker как очередь,
- пока **без** загрузки бинарного файла и без статического/динамического анализа.

---

## Что уже добавлено в код

- SQLAlchemy-база и сессии: `backend/app/db/base.py`, `backend/app/db/session.py`
- Модель `Submission`: `backend/app/models/submission.py`
- Схемы API: `backend/app/schemas/submission.py`
- Эндпоинты:
  - `POST /api/v1/submissions/file`
  - `GET /api/v1/submissions/{submission_id}`
- Celery app + задача-заглушка:
  - `backend/app/tasks/celery_app.py`
  - `backend/app/tasks/submission_tasks.py`
- Alembic конфиг и первая миграция:
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/20260404_0001_create_submissions.py`
- В `docker-compose` добавлен сервис `worker`.

---

## Важно перед запуском

1) Обязательно создай `.env` из шаблона:
```bash
cp .env.example .env
```

2) Если запускать `docker compose` **до** создания `.env`, будут warning'и про пустые `POSTGRES_*` и `MINIO_*`.

---

## Команды запуска

Из корня проекта:

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

Применить миграцию в контейнере API:

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Если запускаешь Alembic с хоста (не из контейнера):

```bash
alembic -c backend/alembic.ini upgrade head
```

Проверка API:

```bash
curl http://localhost:8000/health/live

curl -X POST http://localhost:8000/api/v1/submissions/file \
  -H "Content-Type: application/json" \
  -d '{"filename":"invoice.exe","sha256":"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"}'

curl http://localhost:8000/api/v1/submissions/1
```

---


## Если ранее падало с ошибкой `type "submissiontype" already exists`

Это был кейс частично примененной миграции (тип enum создался, таблица — нет).

После обновления миграции просто выполни повторно:

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Ожидаемо: миграция пройдет без ошибки дублирования enum-типов.

---

## Что должно получиться

- `POST /api/v1/submissions/file` возвращает `submission_id`, `status=QUEUED`, `task_id`.
- В БД появляется запись в таблице `submissions`.
- Worker принимает задачу `submission.process_file` (пока заглушка).
- `GET /api/v1/submissions/{id}` отдает данные сабмита.

---

## Граница этого шага

Что **не** делаем здесь:
- загрузку и хранение реального файла,
- хэширование содержимого,
- YARA/PE/static analyzer,
- запуск в Container Sandbox.
