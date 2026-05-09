"""Database migration runner using Alembic.

This module provides a reusable async migration runner that can be called
from both the app startup (main.py) and the Alembic CLI (env.py).

It handles:
- Async engine creation from app settings
- URL conversion (sync → async drivers)
- Running all pending Alembic migrations
"""

import logging
import os

from alembic.config import Config as AlembicConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import get_settings
from app.db.database import Base

logger = logging.getLogger(__name__)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def _build_alembic_config() -> AlembicConfig:
    """Create an Alembic Config object with the correct paths and URL."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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


def _do_run_migrations(connection: Connection) -> None:
    """Run migrations within a connection context (called via run_sync)."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(alembic_config: AlembicConfig | None = None) -> None:
    """Run all pending Alembic migrations using an async engine.

    This is the shared entry point used by:
    - App startup: main.py lifespan handler
    - Alembic CLI: env.py run_migrations_online()

    Args:
        alembic_config: Optional Alembic Config object. If not provided,
            one is created automatically from app settings.
    """
    cfg = alembic_config or _build_alembic_config()
    _configure_alembic_url(cfg)

    connectable = async_engine_from_config(
        cfg.get_section(cfg.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()
