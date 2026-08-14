"""
Application Settings - Pydantic BaseSettings
Environment-based configuration for FastAPI
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    APP_NAME: str = "TextNotes API"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    VERSION: str = "2.0.0"

    # Database (Async for FastAPI)
    DATABASE_URL: str = "postgresql+asyncpg://notes:notes_secret@localhost:5432/notes_db"
    SYNC_DATABASE_URL: Optional[str] = None  # For Alembic migrations
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "jwt-dev-secret-change-me-min-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # File Uploads
    UPLOAD_FOLDER: str = "/app/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "md", "txt"}

    # Redis (optional caching layer)
    REDIS_URL: str = "redis://localhost:6379/0"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    def get_sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic migrations"""
        if self.SYNC_DATABASE_URL:
            return self.SYNC_DATABASE_URL
        # Convert async URL to sync
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


# Global settings instance
settings = Settings()
