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
