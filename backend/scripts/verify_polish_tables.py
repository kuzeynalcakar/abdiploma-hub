"""Verify polish-related tables exist without modifying data."""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "albertaprep.db"

EXPECTED = ("quiz_feedback", "question_reports")

def main() -> int:
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN (?, ?)",
        EXPECTED,
    ).fetchall()
    found = {r[0] for r in rows}
    missing = [t for t in EXPECTED if t not in found]
    if missing:
        print("MISSING TABLES:", ", ".join(missing))
        return 1
    for table in EXPECTED:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"OK: {table} exists ({count} rows)")
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
