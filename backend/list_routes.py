#!/usr/bin/env python3
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys

sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')

from app.main import app

print("All routes:")
for r in app.routes:
    if hasattr(r, 'path'):
        methods = r.methods if hasattr(r, 'methods') else ''
        print(f"  {r.path} {methods}")
