from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "Apollon backend foundation is running",
    }
