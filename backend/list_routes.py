#!/usr/bin/env python3
import sys
sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')

from app.main import app
print("All routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = route.methods if hasattr(route, 'methods') else ''
        print(f"  {route.path} {methods}")
