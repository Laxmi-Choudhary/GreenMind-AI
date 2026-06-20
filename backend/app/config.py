import os
import secrets
import logging
from typing import Optional, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# =====================================================
# Environment Variable Aliases
# =====================================================

_ENV_ALIASES = {
    "redis_url": "REDIS_URL",
    "mongodb_uri": "MONGODB_URI",
    "gemini_api_key": "GEMINI_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "secret_key": "SECRET_KEY",
}

for old_key, new_key in _ENV_ALIASES.items():
    if old_key in os.environ and new_key not in os.environ:
        os.environ[new_key] = os.environ[old_key]


# =====================================================
# Application Settings
# =====================================================

class Settings(BaseSettings):
    # -------------------------------------------------
    # App Settings
    # -------------------------------------------------

    APP_NAME: str = "GreenMind AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # -------------------------------------------------
    # Security Settings
    # -------------------------------------------------

    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------------------------------
    # Database Settings
    # -------------------------------------------------

    MONGODB_URI: Optional[str] = None
    DATABASE_NAME: str = "greenmind"

    SQLITE_DB_PATH: str = "greenmind_fallback.db"

    # -------------------------------------------------
    # Redis
    # -------------------------------------------------

    REDIS_URL: Optional[str] = None

    # -------------------------------------------------
    # AI Providers
    # -------------------------------------------------

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://greenmind-ai.vercel.app",
    ]

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_access_expiry(cls, value: int):
        if value <= 0:
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES must be > 0"
            )
        return value

    @field_validator("REFRESH_TOKEN_EXPIRE_DAYS")
    @classmethod
    def validate_refresh_expiry(cls, value: int):
        if value <= 0:
            raise ValueError(
                "REFRESH_TOKEN_EXPIRE_DAYS must be > 0"
            )
        return value

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value: str):
        allowed = {
            "development",
            "staging",
            "production"
        }

        value = value.lower()

        if value not in allowed:
            raise ValueError(
                f"ENVIRONMENT must be one of {allowed}"
            )

        return value

    # -------------------------------------------------
    # Pydantic Settings Config
    # -------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )


# =====================================================
# Create Settings Instance
# =====================================================

settings = Settings()

# =====================================================
# Generate Dev Secret Key
# =====================================================

if not settings.SECRET_KEY:
    settings.SECRET_KEY = secrets.token_urlsafe(32)

    logger.warning(
        "No SECRET_KEY provided. "
        "Generated temporary SECRET_KEY. "
        "Set SECRET_KEY in .env for production."
    )

# =====================================================
# Production Safety Checks
# =====================================================

if (
    settings.ENVIRONMENT == "production"
    and not os.getenv("SECRET_KEY")
):
    logger.error(
        "SECRET_KEY is missing in production!"
    )

logger.info(
    f"{settings.APP_NAME} "
    f"({settings.ENVIRONMENT}) configuration loaded."
)