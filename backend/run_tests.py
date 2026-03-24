#!/usr/bin/env python3
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"

import sys

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Run tests manually
import pytest

sys.exit(
    pytest.main(
        [
            str(BASE_DIR / "tests/test_datasets.py"),
            "-v",
            "--tb=short",
        ]
    )
)
