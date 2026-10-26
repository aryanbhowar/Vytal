"""FastAPI entry point for the Vytal backend.

Run from the project root:
    .venv\\Scripts\\python -m uvicorn app.main:app --app-dir backend --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_routes import router as health_router
from app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description=(
            "Personalized health-risk assessment API. Not a diagnostic tool and "
            "not clinically validated."
        ),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health_router)
    return application


app = create_app()
