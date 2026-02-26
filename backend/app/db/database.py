"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import get_settings

settings = get_settings()

# Create async engine (for Alembic and async endpoints)
async_database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace("mysql://", "mysql+aiomysql://")

async_engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Sync engine for Alembic (if needed)
sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql://"
).replace("mysql+aiomysql://", "mysql://")

sync_engine = create_engine(
    sync_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
)

# Sync session factory
SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_async_session() -> AsyncSession:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session() -> sessionmaker:
    """Get sync session for Alembic."""
    return SessionLocal


async def init_db():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
