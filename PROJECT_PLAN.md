# MVP-проект: веб-система анализа файлов и URL (VirusTotal-подобная, с песочницей Container Sandbox)

## 1) С чего начинать: стратегия реализации по этапам

Ниже — реалистичный план, который можно выполнить итеративно и безопасно.

### Этап 0. Foundation (1–2 дня)
- Определить границы MVP и критерии demo-ready.
- Завести monorepo со структурой сервисов.
- Подготовить базовую инфраструктуру: Docker Compose для backend-частей (API, worker, Redis, PostgreSQL, MinIO).
- **Важно:** подсистема запуска подозрительных файлов работает **вне Docker**, только через Container Sandbox VM.

### Этап 1. Базовый backend + статический анализ (4–6 дней)
- Реализовать API загрузки файла/URL и создания задач анализа.
- Асинхронная обработка через очередь (Celery + Redis).
- Статический анализ файлов:
  - MD5/SHA-256,
  - MIME/file type,
  - PE-анализ (если PE): секции, entropy, imports,
  - YARA-проверка,
  - базовые эвристики.
- Сохранение результатов в PostgreSQL.
- Отчет JSON + человекочитаемый summary.

### Этап 2. URL-анализ (2–4 дня)
- Валидация URL и нормализация.
- Парсинг домена, DNS/WHOIS/SSL базовые проверки.
- Детект признаков риска (возраст домена, редиректы, cert anomalies).
- Включение URL-score в общую модель риска.

### Этап 3. Dynamic Analyzer через Container Sandbox (6–10 дней)
- Поднять отдельную Windows VM для анализа.
- Настроить lifecycle:
  - restore snapshot,
  - передача sample в VM,
  - запуск агента/скрипта анализа,
  - сбор артефактов,
  - shutdown + rollback snapshot.
- Собирать минимум поведенческих артефактов:
  - процесс-дерево,
  - файловые изменения,
  - сетевые соединения,
  - попытки persistence.

### Этап 4. Frontend MVP (3–5 дней)
- Страницы:
  - Upload File,
  - Analyze URL,
  - Task Status,
  - Report View.
- Показ risk-score, триггеров, IOC, технических деталей.

### Этап 5. Hardening + Demo-подготовка (2–3 дня)
- Рейт-лимиты, аутентификация, аудит-логи.
- Ограничения размера/типа файла.
- Политики fail-safe и timeouts.
- Подготовка демонстрационного сценария на безопасных тестовых образцах (EICAR и benign samples).

---

## 2) Архитектура системы

## Компоненты

1. **Frontend (Next.js/React)**
   - UI загрузки файлов/URL,
   - просмотр статуса задач,
   - визуализация отчета.

2. **Backend API (FastAPI)**
   - REST API,
   - валидация входных данных,
   - создание задач,
   - агрегация отчетов,
   - RBAC и auth.

3. **Queue/Worker (Celery + Redis)**
   - тяжелые задачи (анализ) уходят в фон,
   - ретраи, дедлайны, ограничения параллелизма.

4. **Static Analyzer Service (Python)**
   - hashlib, python-magic, pefile, yara-python,
   - извлечение признаков и формирование промежуточного verdict.

5. **Dynamic Analyzer Service (Orchestrator)**
   - управление Container Sandbox через Docker CLI/API,
   - orchestration шага анализа,
   - сбор артефактов из VM,
   - контроль таймаута и rollback.

6. **Container Sandbox Controller**
   - отдельный модуль/процесс со строгим API,
   - операции: restore snapshot, start VM, copy-in/copy-out, execute, poweroff.

7. **Database (PostgreSQL)**
   - сущности: users, submissions, artifacts, static_results, dynamic_results, url_results, risk_scores, audit_logs.

8. **Storage (MinIO/S3-совместимое)**
   - хранение исходных файлов и артефактов анализа,
   - адресация по SHA-256, дедупликация.

## Поток обработки (файл)
1. User upload → API валидирует размер/тип.
2. API считает быстрый SHA-256 pre-check для дедупликации.
3. Создается задача в Celery.
4. Static Analyzer выполняется первым.
5. При policy `dynamic=true` задача передается в Dynamic Analyzer.
6. Dynamic Analyzer запускает VM (snapshot restore → run → collect → rollback).
7. Aggregator считает итоговый risk-score и категорию.
8. Отчет доступен во frontend.

## Поток обработки (URL)
1. URL normalization + validation.
2. DNS/WHOIS/SSL checks.
3. Optional isolated browser check в VM (по флагу).
4. Scoring + verdict + отчет.

---

## 3) Технологический стек (MVP)

- **Frontend:** Next.js + TypeScript + Tailwind (быстро сделать читаемый UI).
- **Backend:** FastAPI + Pydantic + SQLAlchemy.
- **Queue:** Celery + Redis.
- **DB:** PostgreSQL.
- **Storage:** MinIO (локально) или S3.
- **Static analysis libs:** pefile, yara-python, python-magic, hashlib.
- **Dynamic sandbox:** Container Sandbox + Docker CLI/API + Windows VM agent.
- **Observability:** structlog/loguru + Prometheus (минимум health + task metrics).
- **Containerization:** Docker Compose для API/worker/db/redis/storage.

**Ключевой принцип:** Docker — для сервисной части, а **выполнение подозрительных объектов только внутри Container Sandbox VM**.

---

## 4) Прозрачная риск-модель (пример)

Базовый диапазон: 0–100.

### Файловые признаки (статический)
- Совпадение YARA malware rule: +40
- Высокая энтропия секции (>7.2): +12 за секцию (до +24)
- Подозрительные API (CreateRemoteThread, WriteProcessMemory, etc.): +20
- Признаки packing/obfuscation: +15
- Extension mismatch MIME/real type: +10
- Подозрительные PE-секции/аномалии headers: +10
- Обнаружение автозапуска (Run keys strings и т.п. в static indicators): +10

### Динамические признаки
- Создание/инжект в новые процессы: +25
- Persistence (Run key, Startup folder, scheduled task): +20
- Массовые файловые изменения в системных путях: +15
- Подозрительная сеть (C2-like beacons / rare ASN / known bad IOC): +20
- Попытки отключения защитных механизмов: +20

### URL-признаки
- Очень молодой домен (например <30 дней): +20
- Подозрительные редиректы/цепочки: +15
- SSL anomalies/self-signed mismatch: +15
- Фишинг-подобные доменные признаки (typosquatting heuristics): +15
- Обнаружены вредоносные скриптовые индикаторы: +20

### Итоговая категория
- **0–24:** SAFE
- **25–59:** SUSPICIOUS
- **60+:** MALWARE-LIKE

Добавить confidence (0–1), зависящий от полноты данных (был ли dynamic analysis, были ли сетевые артефакты и т.д.).

---

## 5) Безопасность (обязательно)

## Изоляция и Container Sandbox
- Отдельный хост/узел для sandbox (не на dev-машине).
- VM сеть: Host-only/NAT с жесткой фильтрацией; без bridge в prod по умолчанию.
- Отключить clipboard drag&drop/shared folders.
- Immutable base image + snapshot restore перед каждым запуском.
- Жесткий timeout выполнения (например 120 сек) и принудительный poweroff.
- Лимиты CPU/RAM/диск для VM.

## Безопасность backend
- JWT/OAuth2, RBAC (admin/analyst/viewer).
- Rate limiting + upload quotas.
- Ограничения файла (размер, расширения, content-type, magic).
- Не исполнять пользовательский контент на host.
- Сканировать входящий архив на zip-bomb признаки.
- Аудит-логи действий пользователей и системных операций.

## Data security
- Хранение samples по SHA-256 с дедупликацией.
- Шифрование at-rest (по возможности) и TLS in-transit.
- Ограниченный retention период для потенциально опасных образцов.

## Fail-safe принципы
- Если dynamic модуль не отвечает/ошибка rollback → статус `ANALYSIS_FAILED_SAFE`.
- Файл не должен попадать на host execution path ни при каком сценарии.
- При исключении задача завершаетcя с безопасным отказом, без повторного запуска на host.

---

## 6) Реалистичное MVP-ограничение

### Что обязательно в MVP
- Upload file + URL submit.
- Static analysis (hash/type/PE/YARA + базовая эвристика).
- Базовый Dynamic sandbox цикл в Container Sandbox.
- Risk scoring и финальный отчет с категориями SAFE/SUSPICIOUS/MALWARE-LIKE.
- История задач и просмотр отчетов.

### Что можно упростить
- Dynamic phase v1: только процесс/файлы/сеть (без глубокого kernel telemetry).
- URL dynamic browser analysis сделать опциональным и только для приоритетных задач.
- IOC-enrichment через внешние TI-фиды отложить на v2.

### Как безопасно показать на защите
- Использовать EICAR и безопасные тестовые симуляторы поведения.
- Демонстрировать rollback snapshot после каждого запуска.
- Показать, что host не исполняет sample и что есть журнал orchestration-операций.

---

## 7) Стартовый backlog (первые 2 спринта)

## Спринт 1
- [ ] API: `/submit/file`, `/submit/url`, `/task/{id}`, `/report/{id}`
- [ ] Модель БД (минимум 6 таблиц)
- [ ] Static Analyzer worker + JSON schema результата
- [ ] Риск-модель v1
- [ ] Frontend: upload/status/report

## Спринт 2
- [ ] Container Sandbox Controller (snapshot restore/start/exec/collect/rollback)
- [ ] Dynamic artifacts parser
- [ ] Интеграция dynamic verdict в общий report
- [ ] Audit logging + rate limit + file constraints
- [ ] Demo сценарий и threat model документ

---

## 8) Практически: что делать прямо сейчас

1. Создать каркас репозитория (api, worker, frontend, infra, docs).
2. Описать OpenAPI для submit/status/report.
3. Сделать минимальный worker со static анализом и risk-score.
4. Подключить PostgreSQL + Redis + MinIO в docker-compose.
5. Поднять отдельную sandbox VM и вручную проверить lifecycle snapshot.
6. После этого сделать автоматический Dynamic Analyzer orchestration.

Если хочешь, следующим шагом я могу сразу дать:
- целевую структуру репозитория,
- стартовые модели БД,
- контракты API (request/response),
- skeleton-код FastAPI + Celery + базовый static analyzer.
