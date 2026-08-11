from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Flask
    SECRET_KEY: str = "dev-secret-change-me"
    FLASK_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://notes:notes_secret@localhost:5432/notes_db"
    SQLALCHEMY_DATABASE_URI: str | None = None
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10,
    }

    # JWT
    JWT_SECRET_KEY: str = "jwt-dev-secret-change-me-min-32-chars-long"
    JWT_ACCESS_TOKEN_EXPIRES: int = 60 * 60 * 24  # 24 hours
    JWT_TOKEN_LOCATION: List[str] = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Uploads
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "md", "txt"}

    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"

    def model_post_init(self, __context) -> None:
        if not self.SQLALCHEMY_DATABASE_URI:
            object.__setattr__(self, "SQLALCHEMY_DATABASE_URI", self.DATABASE_URL)
