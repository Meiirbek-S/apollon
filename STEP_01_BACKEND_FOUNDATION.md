# Шаг 1: Backend Foundation (FastAPI + PostgreSQL + Redis + MinIO через Docker Compose)

Этот шаг создает **минимальный рабочий фундамент backend** для проекта `apollon`:
- API-сервис на FastAPI,
- инфраструктура через Docker Compose,
- health-check эндпоинты,
- готовность к следующему шагу (DB-модели, очередь Celery, загрузка файлов).

> На этом шаге **нет** запуска файлов, **нет** dynamic analysis, **нет** VirtualBox orchestration.

---

## 1) Что создаем прямо сейчас

Внутри `project/apollon/` создайте структуру:

```text
apollon/
  backend/
    app/
      api/
        routes/
          health.py
      core/
        config.py
      main.py
    requirements.txt
    Dockerfile
  infra/
    docker-compose.yml
  .env.example
  .gitignore
  README.md
```

---

## 2) Файлы и содержимое

## Файл: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.venv/

# Env files
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Project runtime data
storage_data/
pg_data/
redis_data/
```

**Зачем:** чтобы не коммитить локальные/секретные/служебные файлы.

---

## Файл: `.env.example`

```dotenv
# API
API_HOST=0.0.0.0
API_PORT=8000
APP_NAME=Apollon API
APP_ENV=dev

# PostgreSQL
POSTGRES_DB=apollon
POSTGRES_USER=apollon
POSTGRES_PASSWORD=apollon_pass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_BUCKET=samples
```

**Зачем:** единый список переменных окружения без реальных секретов.

---

## Файл: `backend/requirements.txt`

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.0
pydantic==2.11.3
pydantic-settings==2.8.1
python-dotenv==1.1.0
```

**Зачем:** минимальный набор зависимостей для API на Python 3.13.

---

## Файл: `backend/Dockerfile`

```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Зачем:** контейнер API-сервиса.

---

## Файл: `backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Apollon API"
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_db: str = "apollon"
    postgres_user: str = "apollon"
    postgres_password: str = "apollon_pass"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    minio_host: str = "minio"
    minio_port: int = 9000
    minio_bucket: str = "samples"


settings = Settings()
```

**Зачем:** централизованная конфигурация приложения через переменные окружения.

---

## Файл: `backend/app/api/routes/health.py`

```python
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, object]:
    return {
        "status": "ready",
        "app": settings.app_name,
        "env": settings.app_env,
        "services": {
            "postgres": f"{settings.postgres_host}:{settings.postgres_port}",
            "redis": f"{settings.redis_host}:{settings.redis_port}",
            "minio": f"{settings.minio_host}:{settings.minio_port}",
        },
    }
```

**Зачем:** быстрые проверки работоспособности и базовой готовности конфигурации.

---

## Файл: `backend/app/main.py`

```python
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "Apollon backend foundation is running",
    }
```

**Зачем:** точка входа FastAPI.

---

## Файл: `infra/docker-compose.yml`

```yaml
version: "3.9"

services:
  api:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: apollon_api
    env_file:
      - ../.env
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - minio

  postgres:
    image: postgres:16-alpine
    container_name: apollon_postgres
    env_file:
      - ../.env
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - ../pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: apollon_redis
    ports:
      - "6379:6379"
    volumes:
      - ../redis_data:/data

  minio:
    image: minio/minio:latest
    container_name: apollon_minio
    env_file:
      - ../.env
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ../storage_data:/data
```

**Зачем:** поднимает foundation-инфраструктуру для backend.

---

## Файл: `README.md`

```md
# Apollon

MVP-платформа анализа файлов и URL на вредоносную активность.

## Шаг 1 (foundation)
- FastAPI backend
- PostgreSQL
- Redis
- MinIO
- health endpoints

См. `STEP_01_BACKEND_FOUNDATION.md` для пошагового запуска.
```

**Зачем:** короткая точка входа в проект.

---

## 3) Команды в терминале (по порядку)

Из папки `project/apollon/`:

```bash
# 1) Скопировать env-шаблон
cp .env.example .env

# 2) Запустить foundation-сервисы
docker compose -f infra/docker-compose.yml up -d --build

# 3) Проверить, что контейнеры поднялись
docker compose -f infra/docker-compose.yml ps

# 4) Проверить API
curl http://localhost:8000/
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Чтобы остановить:

```bash
docker compose -f infra/docker-compose.yml down
```

---

## 4) Что ты должен увидеть после запуска

- В `docker compose ... ps` должны быть контейнеры:
  - `apollon_api`
  - `apollon_postgres`
  - `apollon_redis`
  - `apollon_minio`
- `GET /` возвращает JSON с сообщением, что foundation работает.
- `GET /health/live` возвращает `{ "status": "ok" }`.
- `GET /health/ready` возвращает `status=ready` и адреса postgres/redis/minio из env.

---

## 5) Критерии готовности этапа

Этап считается завершенным, если:
- Создана структура файлов из этого документа.
- `docker compose up -d --build` завершается без ошибок.
- Все 4 контейнера в статусе `Up`.
- Все 3 API-запроса (`/`, `/health/live`, `/health/ready`) отвечают корректно.
- В проекте есть `.env` (локально), а в git — только `.env.example`.

---

## 6) Что будет следующим шагом (без реализации)

Следующий шаг: добавить **минимальный backend domain layer**:
- SQLAlchemy + Alembic,
- таблицу `submissions`,
- endpoint `POST /api/v1/submissions/file` (пока без deep analysis),
- постановку задачи в очередь (каркас Celery без сложной логики).
