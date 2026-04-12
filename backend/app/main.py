from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

_default_origins = {"http://localhost:3000", "http://127.0.0.1:3000"}
configured_origins = set(getattr(settings, "cors_origins", []) or [])
cors_origins = sorted(_default_origins | configured_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "Apollon backend foundation is running",
    }
