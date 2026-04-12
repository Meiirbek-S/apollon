# Шаг 3: Реальная загрузка файла в MinIO + дедупликация по SHA-256

Цель шага:
- принять реальный файл через API,
- посчитать SHA-256 и размер,
- сохранить файл в MinIO,
- создать запись `submissions` с `storage_key`, `size_bytes`, `content_type`,
- если артефакт уже был загружен (по SHA-256), не грузить файл повторно в MinIO.

---

## Что добавлено

- Новый endpoint: `POST /api/v1/submissions/file/upload` (multipart/form-data).
- Ограничение размера загрузки (`MAX_UPLOAD_SIZE_MB`, default 20 MB).
- MinIO client helper и автосоздание bucket.
- Миграция `20260404_0002_add_file_metadata_columns.py`.

---

## Важная логика дедупликации

- Дедуп работает только по уже загруженным объектам (`storage_key IS NOT NULL`).
- Если раньше был создан submission только с метаданными (через `POST /file`), он **не** блокирует первый реальный upload.
- При дедупе создается **новый** submission (новый `submission_id`) и новая задача в очереди, но reuse существующего `storage_key`.
- В ответе будет:
  - `deduplicated: true`
  - `reused_from_submission_id: <id исходного submission с артефактом>`

---

## Обнови зависимости и контейнеры

```bash
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml up -d --build
```

Применить миграции:

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

---

## Проверка upload endpoint

```bash
curl -X POST http://localhost:8000/api/v1/submissions/file/upload \
  -F "file=@/absolute/path/to/test.bin"
```

Ожидаемый ответ:
- `submission_id`
- `status: QUEUED`
- `task_id`
- `deduplicated` (false при первом upload, true при повторном того же файла)
- `reused_from_submission_id` (null при первом upload)

Проверка созданной заявки:

```bash
curl http://localhost:8000/api/v1/submissions/<submission_id>
```

Должны появиться поля:
- `content_type`
- `size_bytes`
- `storage_key`

---

## Граница шага

Что пока не делаем:
- static analysis (YARA/PE/entropy),
- dynamic analysis (VirtualBox),
- вердикты и risk scoring.
