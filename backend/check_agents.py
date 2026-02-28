#!/usr/bin/env python3
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys

sys.path.insert(0, "/root/.openclaw/workspace/MasterDataCleaner/backend")

from app.main import app

print("Agent routes:")
for r in app.routes:
    if hasattr(r, "path") and "/agents" in r.path:
        print(f"  {r.path}")
