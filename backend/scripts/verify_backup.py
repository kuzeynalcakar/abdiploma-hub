"""Create a backup and verify tables + row counts.

Usage (from backend/):
  python scripts/verify_backup.py
  python scripts/verify_backup.py path/to/existing_backup.db
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.backup import create_backup, verify_backup_file  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    created = None
    if args:
        backup_path = Path(args[0])
        print(f"Verifying existing backup: {backup_path.name}")
    else:
        print("Creating backup…")
        try:
            created = create_backup()
        except Exception as exc:
            print(f"BACKUP FAILED: {type(exc).__name__}: {exc}")
            return 1
        backup_path = Path(created["path"])
        print(f"Created: {backup_path.name} ({created['size_bytes']:,} bytes)")

    result = verify_backup_file(backup_path)
    print(json.dumps(result, indent=2, default=str))
    if result["ok"]:
        print("VERIFY OK")
        return 0
    print("VERIFY FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

