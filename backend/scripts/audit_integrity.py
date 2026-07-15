"""Run database integrity checks (orphans / broken relationships).

Usage (from backend/):
  python scripts/audit_integrity.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.database.init_db import init_db  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.services.integrity import run_integrity_audit  # noqa: E402


def main() -> int:
    init_db()
    db = SessionLocal()
    try:
        report = run_integrity_audit(db)
    finally:
        db.close()
    print(json.dumps(report, indent=2))
    if report["ok"]:
        print("INTEGRITY OK")
        return 0
    print(f"INTEGRITY ISSUES: {report['issue_count']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

