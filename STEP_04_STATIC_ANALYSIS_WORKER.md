# Шаг 4: Минимальный static analysis в worker (без YARA/PE)

Цель шага:
- после upload запускать фоновый анализ,
- считать MD5/SHA-256/size/mime,
- присваивать базовый risk level,
- сохранять отчет в БД,
- получать отчет через API.

---

## Что добавлено

- Таблица `static_analysis_results` (миграция `20260404_0003`).
- Worker-задача `submission.process_file` теперь:
  - скачивает файл из MinIO,
  - считает MD5 и SHA-256,
  - определяет MIME,
  - присваивает `SAFE` или `SUSPICIOUS`,
  - обновляет статус submission.
- Новый endpoint: `GET /api/v1/submissions/{submission_id}/report`.

---


## Поведение для deduplicated submissions

- Если повторный upload попал в дедуп и у исходного submission уже есть static report:
  - новый submission создается сразу со статусом `DONE`,
  - `task_id` возвращается как `reused-existing-report`,
  - `/api/v1/submissions/{new_id}/report` возвращает отчет через `reused_from_submission_id` (включая цепочку reuse, если она есть).

- Если исходный submission еще без отчета:
  - новый deduplicated submission получает `QUEUED`,
  - worker строит отдельный отчет для нового submission (или для первого submission в цепочке без готового отчета).

---


## Проверка регистрации Celery task

Если worker пишет `Received unregistered task of type 'submission.process_file'`, проверь запуск worker:

```bash
docker compose -f infra/docker-compose.yml logs -f worker
```

В логе worker в секции `[tasks]` должен быть:

- `submission.process_file`

Дополнительно можно проверить список задач командой:

```bash
docker compose -f infra/docker-compose.yml exec worker \
  celery -A app.tasks.celery_app:celery_app inspect registered
```

---

## Команды запуска

```bash
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Загрузка файла:

```bash
curl -X POST http://localhost:8000/api/v1/submissions/file/upload \
  -F "file=@/absolute/path/to/test.bin"
```

Проверка submission:

```bash
curl http://localhost:8000/api/v1/submissions/<submission_id>
```

Получить static report:

```bash
curl http://localhost:8000/api/v1/submissions/<submission_id>/report
```

---

## Ожидаемый результат

- Сначала submission со статусом `QUEUED/PROCESSING`.
- После работы worker — `DONE`.
- `GET /report` возвращает JSON:
  - `md5`
  - `sha256`
  - `file_size`
  - `mime_type`
  - `risk_level`

---

## Граница шага

Пока не делаем:
- YARA,
- PE-секции и entropy,
- dynamic analysis в VirtualBox,
- полноценный risk scoring на десятках признаков.
