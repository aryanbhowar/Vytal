"""Central application settings, read from environment variables.

Every variable is optional and documented in `.env.example`. Vytal needs no
secrets, API keys or credentials.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "Vytal"
APP_VERSION = "0.2.0"
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Vite's development server origin. In production the backend serves the
# frontend itself (same origin), so CORS is not needed there.
DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"

# Saved model artifacts, relative to the models directory.
MODEL_ARTIFACTS = {
    "heart": "heart/heart_logreg_v1.joblib",
    "respiratory": "respiratory/respiratory_logreg_v1.joblib",
}


def _split_origins(raw_value: str) -> list[str]:
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None or not value.strip() else int(value)


@dataclass(frozen=True)
class Settings:
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    allowed_origins: list[str] = field(
        default_factory=lambda: _split_origins(os.getenv("VYTAL_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS))
    )
    models_dir: Path = field(
        default_factory=lambda: Path(os.getenv("VYTAL_MODELS_DIR", str(PROJECT_ROOT / "models")))
    )
    # Interactive API docs (/docs). On by default for development; turn off in production.
    enable_api_docs: bool = field(default_factory=lambda: _env_bool("VYTAL_ENABLE_API_DOCS", True))
    # A real assessment request is under 1 KB; anything far larger is malformed or abusive.
    max_request_body_bytes: int = field(default_factory=lambda: _env_int("VYTAL_MAX_REQUEST_BYTES", 16_384))
    # Per-client limit on prediction requests (0 disables). Counts per client IP address.
    predict_rate_limit_per_minute: int = field(default_factory=lambda: _env_int("VYTAL_PREDICT_RATE_LIMIT_PER_MINUTE", 30))
    # Folder with the built frontend (`npm run build`). When it exists, the backend serves the website too.
    frontend_dist_dir: Path = field(
        default_factory=lambda: Path(os.getenv("VYTAL_FRONTEND_DIST", str(PROJECT_ROOT / "frontend" / "dist")))
    )
    serve_frontend: bool = field(default_factory=lambda: _env_bool("VYTAL_SERVE_FRONTEND", False))


def load_settings() -> Settings:
    return Settings()
