"""
FastAPI Application Factory
Modern ASGI web framework with automatic OpenAPI docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import Settings
from app.extensions import db, Base
from app.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup/shutdown events"""
    # Startup: Create database tables
    from app.models import User, Note, Folder, Tag, Attachment, note_tags
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: Cleanup if needed
    pass


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Features:
    - Auto-generated OpenAPI/Swagger docs at /docs
    - CORS enabled for frontend
    - JWT authentication via Bearer tokens
    - SQLAlchemy ORM integration
    """
    settings = settings or Settings()
    
    app = FastAPI(
        title="TextNotes API",
        description="📝 Modern Notes API built with FastAPI, PostgreSQL, and SQLAlchemy",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include all API routes
    app.include_router(api_router, prefix="/api")
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "notes-api", "framework": "FastAPI"}
    
    return app
