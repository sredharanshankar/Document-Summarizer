from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config/settings.py -> backend/
_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables / .env."""

    # An absolute path, not a bare ".env": pydantic-settings resolves a
    # relative env_file against the process's current working directory,
    # not this file's location. Since uvicorn here is launched from the
    # repo root (via `--app-dir backend`), a relative path silently missed
    # backend/.env entirely and fell back to defaults with no error.
    model_config = SettingsConfigDict(env_file=_BACKEND_ROOT / ".env", extra="ignore")

    # --- AI provider -------------------------------------------------
    ai_api_key: str = ""
    ai_model: str = "openai/gpt-oss-120b"
    ai_provider: Literal["groq", "fallback"] = "groq"
    ai_request_timeout_seconds: int = 30

    # --- OCR -----------------------------------------------------------
    ocr_enabled: bool = True
    tesseract_cmd: str | None = None

    # --- Uploads ---------------------------------------------------------
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: tuple[str, ...] = (".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt")

    # --- CORS ------------------------------------------------------------
    # Stored as a raw comma-separated string, not list[str]: pydantic-settings
    # tries to JSON-decode env values for list-typed fields before any
    # validator runs, which fails outright for a plain "a,b,c" .env value.
    # Splitting it ourselves via the property below sidesteps that entirely.
    cors_allow_origins: str = "http://localhost:5173"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    # --- Misc ------------------------------------------------------------
    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
