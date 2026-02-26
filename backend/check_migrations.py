#!/usr/bin/env python3
"""Check Alembic migration status."""
import sys
import os

sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')
os.chdir('/root/.openclaw/workspace/MasterDataCleaner/backend')

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory

# Load config
alembic_cfg = Config('/root/.openclaw/workspace/MasterDataCleaner/backend/alembic.ini')

# Get current revision
script = ScriptDirectory.from_config(alembic_cfg)
current = script.get_current_head()

print(f"Current head: {current}")

# Get all revisions
revisions = list(script.walk_revisions())
print(f"Total migrations: {len(revisions)}")
for rev in revisions:
    print(f"  {rev.revision}")
