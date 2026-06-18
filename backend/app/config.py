import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "GreenMind AI"
    SECRET_KEY: str = "greenmind-super-secret-jwt-key-2026-hackathon-mvp"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day

    # Database Settings
    MONGODB_URI: str = "mongodb+srv://laxmi:9323624053@cluster0.f6keeyj.mongodb.net/?appName=Cluster0"
    DATABASE_NAME: str = "greenmind"
    SQLITE_DB_PATH: str = "greenmind_fallback.db"

    # AI API keys
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
