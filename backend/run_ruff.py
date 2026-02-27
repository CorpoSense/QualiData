#!/usr/bin/env python3
import subprocess
result = subprocess.run(['/root/.openclaw/workspace/MasterDataCleaner/backend/.venv_new/bin/ruff', 'check', '/root/.openclaw/workspace/MasterDataCleaner/backend/'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
