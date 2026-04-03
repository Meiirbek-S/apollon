from fastapi import FastAPI

from app.api.v1.endpoints import admin, artifacts, hash_lookup, metrics, reports, status, submissions, submit
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(submit.router, prefix=settings.api_prefix, tags=["submit"])
app.include_router(status.router, prefix=settings.api_prefix, tags=["status"])
app.include_router(reports.router, prefix=settings.api_prefix, tags=["reports"])
app.include_router(submissions.router, prefix=settings.api_prefix, tags=["submissions"])
app.include_router(artifacts.router, prefix=settings.api_prefix, tags=["artifacts"])
app.include_router(hash_lookup.router, prefix=settings.api_prefix, tags=["hash"])
app.include_router(admin.router, prefix=settings.api_prefix, tags=["admin"])
app.include_router(metrics.router, prefix=settings.api_prefix, tags=["metrics"])


@app.get(f"{settings.api_prefix}/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
