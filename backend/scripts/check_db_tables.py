import sqlite3
from pathlib import Path

backend = Path(__file__).resolve().parents[1]
for name in ("albertaprep.db", "test_import_bio30.db"):
    db = backend / name
    if not db.exists():
        print(f"{name}: missing file")
        continue
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('quiz_feedback','question_reports')"
    ).fetchall()
    print(f"{name}: {[r[0] for r in rows]}")
