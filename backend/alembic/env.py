"""Alembic environment configuration.

This file is the entry point for the Alembic CLI (e.g., `alembic upgrade head`).
It uses the standard async Alembic pattern (async engine + run_sync) to run
migrations within the existing EnvironmentContext, avoiding re-entrant
command.upgrade() calls that would conflict with the CLI's own context.

For app startup migrations, see app.db.migrate.run_async_migrations() which
uses command.upgrade() directly (safe because there's no pre-existing context).
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import Base
from app.db.migrate import (
    _configure_alembic_url,
    target_metadata,
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Configure URL from app settings
_configure_alembic_url(config)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _do_run_migrations(connection: Connection) -> None:
    """Run migrations within a connection context (called via run_sync).

    This uses the alembic context proxy, which is only available when
    running via the Alembic CLI. Do NOT move this to a shared module.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Uses the standard async Alembic pattern: create an async engine from
    the config, connect, and run migrations via run_sync. This avoids
    calling command.upgrade() which would create a re-entrant
    EnvironmentContext that conflicts with the CLI's own context.
    """
    section = config.get_section(config.config_ini_section, {})
    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def _run_async():
        async with connectable.connect() as conn:
            await conn.run_sync(_do_run_migrations)
        await connectable.dispose()

    asyncio.run(_run_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
