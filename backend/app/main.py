from fastapi import FastAPI
<<<<<<< HEAD
=======
from fastapi.middleware.cors import CORSMiddleware
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

<<<<<<< HEAD
=======
cors_origins = getattr(
    settings,
    "cors_origins",
    ["http://localhost:3000", "http://127.0.0.1:3000"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "message": "Apollon backend foundation is running",
    }
