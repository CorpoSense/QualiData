#!/usr/bin/env python3
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys

sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')

from app.main import app

print("App loaded successfully!")
print(f"Routes: {[r.path for r in app.routes if hasattr(r, 'path')][:15]}")
