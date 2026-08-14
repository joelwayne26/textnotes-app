"""
SQLAlchemy Extensions for FastAPI
Uses async engine for non-blocking database operations
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models"""
    pass


# Database URL - convert postgresql to postgresql+asyncpg for async
DATABASE_URL = "postgresql+asyncpg://notes:notes_secret@localhost:5432/notes_db"

# Async Engine Configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in logs
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# Async Session Factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides database sessions.
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Legacy sync db for migrations (Alembic doesn't support async well)
from sqlalchemy import create_engine as sync_create_engine

SYNC_DATABASE_URL = "postgresql://notes:notes_secret@localhost:5432/notes_db"
sync_engine = sync_create_engine(SYNC_DATABASE_URL)
