"""Alembic environment configuration.

This file is the entry point for the Alembic CLI (e.g., `alembic upgrade head`).
It delegates URL configuration and metadata to app.db.migrate, but keeps
its own _do_run_migrations() since the alembic context proxy is only
available during CLI execution.
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
    _build_alembic_config,
    _configure_alembic_url,
    run_async_migrations,
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

    Uses the shared run_async_migrations() from app.db.migrate,
    which calls alembic.command.upgrade() internally.
    """
    asyncio.run(run_async_migrations(config))


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
