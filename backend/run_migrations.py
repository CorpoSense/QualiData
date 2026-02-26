#!/usr/bin/env python3
"""Run Alembic migrations."""
import sys
import os

# Add backend to path
sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')
os.chdir('/root/.openclaw/workspace/MasterDataCleaner/backend')

from alembic.config import Config
from alembic import command

# Load config
alembic_cfg = Config('/root/.openclaw/workspace/MasterDataCleaner/backend/alembic.ini')

# Run upgrade
command.upgrade(alembic_cfg, 'head')
