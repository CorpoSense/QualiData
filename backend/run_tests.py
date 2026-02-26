#!/usr/bin/env python3
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys
sys.path.insert(0, '/root/.openclaw/workspace/MasterDataCleaner/backend')

# Run tests manually
import pytest
sys.exit(pytest.main([
    '/root/.openclaw/workspace/MasterDataCleaner/backend/tests/test_datasets.py',
    '-v', '--tb=short'
]))
