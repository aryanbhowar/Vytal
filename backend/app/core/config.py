"""Central application settings.

Values can be overridden with environment variables (documented in `.env.example`).
Nothing here is secret: Vytal needs no API keys or credentials.
"""

import os
from dataclasses import dataclass, field

APP_NAME = "Vytal"
APP_VERSION = "0.1.0"

# Vite's development server runs on this origin. The Vite proxy normally makes
# CORS unnecessary, but allowing it lets the frontend call the API directly too.
DEFAULT_ALLOWED_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _split_origins(raw_value: str) -> list[str]:
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    allowed_origins: list[str] = field(
        default_factory=lambda: _split_origins(
            os.getenv("VYTAL_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
        )
    )


settings = Settings()
