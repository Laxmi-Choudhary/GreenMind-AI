import os
import secrets
import logging
from typing import Optional
from pydantic_settings import BaseSettings

# Normalize common lowercase environment variable names to the uppercase keys used by the config model.
_env_aliases = {
    "redis_url": "REDIS_URL",
    "mongodb_uri": "MONGODB_URI",
    "gemini_api_key": "GEMINI_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
}
for old_key, new_key in _env_aliases.items():
    if old_key in os.environ and new_key not in os.environ:
        os.environ[new_key] = os.environ[old_key]

class Settings(BaseSettings):
    APP_NAME: str = "GreenMind AI"
    # SECURITY: Do not hardcode SECRET_KEY in source. Provide via .env in production.
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour for access tokens (short-lived)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # refresh token lifetime

    # Database Settings
    # Provide a managed MongoDB URI via environment in production. Leave empty to use SQLite fallback.
    MONGODB_URI: Optional[str] = None
    DATABASE_NAME: str = "greenmind"
    SQLITE_DB_PATH: str = "greenmind_fallback.db"

    # AI API keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Optional Redis connection URL (allow unused env var without failing)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # allow extra environment variables (e.g., third-party services) without failing validation
        extra = "ignore"

settings = Settings()

# If SECRET_KEY is not provided (dev), generate an ephemeral key and warn.
if not settings.SECRET_KEY:
    settings.SECRET_KEY = secrets.token_urlsafe(32)
    logging.warning("No SECRET_KEY set in environment; generated an ephemeral SECRET_KEY. Set SECRET_KEY in .env for production.")
