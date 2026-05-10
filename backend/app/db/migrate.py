"""Database migration runner using Alembic.

This module provides a reusable async migration runner that can be called
from both the app startup (main.py) and the Alembic CLI (env.py).

It handles:
- Async engine creation from app settings
- URL conversion (sync → async drivers)
- Running all pending Alembic migrations via alembic.command.upgrade()
- Fallback to create_all() if Alembic migrations fail
"""

import logging
import os

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.db.database import Base

logger = logging.getLogger(__name__)

# Target metadata for autogenerate support (used by env.py)
target_metadata = Base.metadata


def _build_alembic_config() -> AlembicConfig:
    """Create an Alembic Config object with the correct paths and URL."""
    # migrate.py is at backend/app/db/migrate.py → go up 3 levels to backend/
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_cfg = AlembicConfig(os.path.join(backend_dir, "alembic.ini"))
    alembic_cfg.set_main_option(
        "script_location", os.path.join(backend_dir, "alembic")
    )
    return alembic_cfg


def _configure_alembic_url(alembic_config: AlembicConfig) -> None:
    """Set the sqlalchemy.url on the alembic config from app settings.

    Converts sync driver URLs to async equivalents (e.g. postgresql://
    → postgresql+asyncpg://).
    """
    settings = get_settings()
    database_url = settings.database_url

    if database_url.startswith("postgresql://"):
        import urllib.parse

        parsed = urllib.parse.urlparse(database_url)
        query = urllib.parse.parse_qs(parsed.query)

        # Remove sslmode from query (asyncpg uses connect_args instead)
        query.pop("sslmode", None)

        new_query = urllib.parse.urlencode(query, doseq=True)
        new_path = parsed.path
        if new_query:
            new_path = f"{parsed.path}?{new_query}"

        database_url = f"postgresql+asyncpg://{parsed.netloc}{new_path}"

    alembic_config.set_main_option("sqlalchemy.url", database_url)


def _get_async_url() -> str:
    """Get the async-compatible database URL from app settings."""
    settings = get_settings()
    database_url = settings.database_url

    if database_url.startswith("postgresql://"):
        import urllib.parse

        parsed = urllib.parse.urlparse(database_url)
        query = urllib.parse.parse_qs(parsed.query)
        query.pop("sslmode", None)
        new_query = urllib.parse.urlencode(query, doseq=True)
        new_path = parsed.path
        if new_query:
            new_path = f"{parsed.path}?{new_query}"
        database_url = f"postgresql+asyncpg://{parsed.netloc}{new_path}"

    return database_url


async def _create_all_fallback() -> None:
    """Fallback: create all tables directly using SQLAlchemy metadata.

    This is used when Alembic migrations fail (e.g., missing alembic_version
    table, corrupted migration history). It creates all tables that don't
    already exist, but cannot alter existing tables (e.g., add new columns).
    """
    from sqlalchemy import text

    url = _get_async_url()
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        # Check if any tables already exist to avoid overwriting
        existing_tables = set()
        try:
            if "sqlite" in url:
                result = await conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
            else:
                result = await conn.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public'"
                    )
                )
            existing_tables = {row[0] for row in result}
        except Exception:
            logger.debug("Could not list existing tables, proceeding with create_all")

        if existing_tables:
            logger.info(
                f"create_all fallback: {len(existing_tables)} tables already exist. "
                "Only new tables will be created; existing tables will NOT be altered. "
                "Run 'alembic upgrade head' manually to apply column-level migrations."
            )

        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


async def run_async_migrations(alembic_config: AlembicConfig | None = None) -> None:
    """Run all pending Alembic migrations using alembic.command.upgrade().

    This is the shared entry point used by:
    - App startup: main.py lifespan handler
    - Alembic CLI: env.py run_migrations_online()

    If Alembic migrations fail, falls back to create_all() to ensure
    at least the base tables exist.

    Args:
        alembic_config: Optional Alembic Config object. If not provided,
            one is created automatically from app settings.
    """
    cfg = alembic_config or _build_alembic_config()
    _configure_alembic_url(cfg)

    try:
        command.upgrade(cfg, "head")
        logger.info("Alembic migrations applied successfully")
    except Exception as e:
        logger.warning(
            f"Alembic migration failed: {e}. "
            "Falling back to create_all() to ensure base tables exist."
        )
        await _create_all_fallback()
