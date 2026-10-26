"""FastAPI entry point for the Vytal backend.

Development (from the project root):
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --app-dir backend --reload
Production: see docs/deployment/DEPLOYMENT.md (serves the built frontend too).
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import PROJECT_ROOT, Settings, load_settings

# The backend reuses the ML package (feature schema, model loading) so inference
# matches training exactly. Make it importable however the server is started.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.api.assessment_routes import router as assessment_router  # noqa: E402
from app.api.health_routes import router as health_router  # noqa: E402
from app.core.errors import install_error_handlers  # noqa: E402
from app.core.security import (  # noqa: E402
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    SlidingWindowRateLimiter,
)
from app.services.model_registry import load_registry  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _mount_frontend(application: FastAPI, dist_dir: Path) -> None:
    """Serve the built single-page app; unknown non-API paths return index.html."""
    index = dist_dir / "index.html"
    application.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

    @application.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Not Found")
        candidate = (dist_dir / path).resolve()
        if path and candidate.is_file() and dist_dir.resolve() in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(index)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.model_registry = load_registry(settings)
        yield

    application = FastAPI(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description="Personalized health-risk assessment API. Not a diagnostic tool and not clinically validated.",
        lifespan=lifespan,
        docs_url="/docs" if settings.enable_api_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.enable_api_docs else None,
    )
    application.state.settings = settings
    application.state.rate_limiter = SlidingWindowRateLimiter(settings.predict_rate_limit_per_minute)
    # Middleware runs outermost-last-added: size limit first, then CORS, then headers.
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
                               allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    application.add_middleware(RequestSizeLimitMiddleware, max_bytes=settings.max_request_body_bytes)
    install_error_handlers(application)
    application.include_router(health_router)
    application.include_router(assessment_router)
    if settings.serve_frontend and (settings.frontend_dist_dir / "index.html").exists():
        _mount_frontend(application, settings.frontend_dist_dir)
    return application


app = create_app()
