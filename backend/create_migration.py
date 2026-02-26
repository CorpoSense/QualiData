#!/usr/bin/env python3
"""Create initial Alembic migration."""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')
os.chdir('/root/.openclaw/workspace/MasterDataCleaner/backend')

from alembic.config import Config
from alembic import command

# Load config
alembic_cfg = Config('/root/.openclaw/workspace/MasterDataCleaner/backend/alembic.ini')

# Create initial migration with autogenerate
command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
