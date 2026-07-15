"""Restore the live SQLite database from a verified backup.

IMPORTANT: Stop the API process before restoring.

Usage (from backend/):
  python scripts/restore_db.py backups/albertaprep_backup_YYYYMMDD_HHMMSS.db
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.backup import restore_sqlite_backup, verify_backup_file  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("Usage: python scripts/restore_db.py <backup.db>")
        return 2
    backup = Path(args[0])
    if not backup.is_absolute():
        backup = (BACKEND / backup).resolve()

    print(f"Verifying {backup.name}…")
    report = verify_backup_file(backup)
    if not report["ok"]:
        print("VERIFY FAILED — restore aborted.")
        print(report)
        return 1

    try:
        dest = restore_sqlite_backup(backup)
    except Exception as exc:
        print(f"RESTORE FAILED: {type(exc).__name__}: {exc}")
        return 1

    print("RESTORE OK")
    print(f"  restored_from: {backup.name}")
    print(f"  live_db: {dest.name}")
    print(f"Restart the API, then run: python scripts/verify_backup.py {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

