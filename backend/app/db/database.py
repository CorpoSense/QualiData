"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

# Base class for models
Base = declarative_base()

# Lazy engine creation
_async_engine = None
_sync_engine = None


def get_async_engine():
    """Get or create async engine."""
    global _async_engine
    if _async_engine is None:
        # Convert to async URL
        database_url = settings.database_url
        if database_url.startswith("postgresql://"):
            async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif database_url.startswith("mysql://"):
            async_database_url = database_url.replace("mysql://", "mysql+aiomysql://")
        else:
            async_database_url = database_url

        # Handle SSL for Aiven
        if "sslmode" in async_database_url:
            # asyncpg uses different SSL parameter
            async_database_url = async_database_url.replace("?sslmode=require", "?ssl=require")

        _async_engine = create_async_engine(
            async_database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
        )
    return _async_engine


def get_sync_engine():
    """Get or create sync engine."""
    global _sync_engine
    if _sync_engine is None:
        database_url = settings.database_url
        if database_url.startswith("postgresql+asyncpg://"):
            sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif database_url.startswith("mysql+aiomysql://"):
            sync_database_url = database_url.replace("mysql+aiomysql://", "mysql://")
        else:
            sync_database_url = database_url

        _sync_engine = create_engine(
            sync_database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
        )
    return _sync_engine


# Lazy session factories
def get_async_session_maker():
    """Get async session maker."""
    return async_sessionmaker(
        get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_sync_session_maker():
    """Get sync session maker."""
    return sessionmaker(
        get_sync_engine(),
        autocommit=False,
        autoflush=False,
    )


# For backwards compatibility
@property
def async_engine():
    return get_async_engine()


@property
def sync_engine():
    return get_sync_engine()


AsyncSessionLocal = get_async_session_maker()
SessionLocal = get_sync_session_maker()


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
    async with get_async_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
