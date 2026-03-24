#!/usr/bin/env python3
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import app

print("Dataset routes:")
for r in app.routes:
    if hasattr(r, "path") and "dataset" in r.path:
        methods = r.methods if hasattr(r, "methods") else ""
        print(f"  {r.path} {methods}")
