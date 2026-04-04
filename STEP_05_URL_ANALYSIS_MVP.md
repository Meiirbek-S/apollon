# Шаг 5: Базовый URL analysis (MVP)

Цель шага:
- добавить submission для URL,
- обработку URL в worker,
- endpoint отчета по URL,
- простой риск-вердикт SAFE/SUSPICIOUS без внешних TI-интеграций.

---

## Что добавлено

- `POST /api/v1/submissions/url`
- worker task `submission.process_url`
- таблица `url_analysis_results`
- `GET /api/v1/submissions/{id}/url-report`
- универсальный `GET /api/v1/submissions/{id}/report` теперь работает и для URL

---

## Что анализируем на этом этапе

- нормализация URL (`http/https`)
- выделение домена
- DNS resolve (`socket.gethostbyname`)
- использует ли URL HTTPS
- базовые эвристики риска:
  - нет HTTPS
  - URL c raw IP
  - punycode (`xn--`)
  - домен не резолвится

---

## Команды

```bash
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

Создать URL-submission:

```bash
curl -X POST http://localhost:8000/api/v1/submissions/url \
  -H "Content-Type: application/json" \
  -d '{"url":"http://example.com"}'
```

Проверить статус:

```bash
curl http://localhost:8000/api/v1/submissions/<submission_id>
```

Получить URL-report (2 варианта):

```bash
# унифицированный endpoint
curl http://localhost:8000/api/v1/submissions/<submission_id>/report

# специализированный endpoint (оставлен для совместимости)
curl http://localhost:8000/api/v1/submissions/<submission_id>/url-report
```

---

## Ожидаемый результат

- submission создается со `source_type=URL`
- worker берет `submission.process_url`
- status меняется до `DONE` или `FAILED`
- `/url-report` возвращает `normalized_url`, `domain`, `resolved_ip`, `uses_https`, `risk_level`
