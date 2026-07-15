"""Create a timestamped database backup.

Usage (from backend/):
  python scripts/backup_db.py

Environment:
  BACKUP_DIR              Target directory (default: backend/backups)
  BACKUP_RETENTION_DAYS   Delete backups older than N days (default: 14)
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.backup import create_backup  # noqa: E402


def main() -> int:
    try:
        result = create_backup()
    except Exception as exc:
        print(f"BACKUP FAILED: {type(exc).__name__}: {exc}")
        return 1
    print("BACKUP OK")
    print(f"  file: {result['filename']}")
    print(f"  size: {result['size_bytes']:,} bytes")
    print(f"  deleted_old: {result['deleted_old']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

