"""Resync fixed SCI10 JSON bank into production DB without touching other courses."""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.question_import import import_questions
from app.database.session import SessionLocal

BACKEND = Path(__file__).resolve().parents[1]
PROD_DB = BACKEND / "albertaprep.db"
BACKUP_DIR = BACKEND / "backups"
JSON_PATH = BACKEND.parent / "questions.json" / "science10_questions_final.json"
ALIAS = BACKEND.parent / "questions.json" / "course_questions_final.json"
PRESERVE = ("BIO30", "MATH30-1", "CHEM30", "PHYS30", "MATH30-2", "MATH20-1", "SCI30")


def scrub_261() -> None:
    bank = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    q = bank[261]
    correct = next(c["text"] for c in q["choices"] if c["is_correct"])
    q["choices"] = [
        {"text": correct, "is_correct": True},
        {"text": "hour-by-hour weather forecasts for the coming week", "is_correct": False},
        {"text": "exact hurricane track predictions a decade into the future", "is_correct": False},
        {"text": "instantaneous barometric pressure at a student's desk only", "is_correct": False},
    ]
    q["answer"] = correct
    text = json.dumps(bank, indent=2, ensure_ascii=False) + "\n"
    JSON_PATH.write_text(text, encoding="utf-8")
    ALIAS.write_text(text, encoding="utf-8")


def course_count(conn: sqlite3.Connection, code: str) -> int:
    return conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = ? AND q.is_active = 1
        """,
        (code,),
    ).fetchone()[0]


def sci10_ids(conn: sqlite3.Connection) -> list[int]:
    return [
        r[0]
        for r in conn.execute(
            """
            SELECT q.id FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'SCI10'
            """
        ).fetchall()
    ]


def main() -> int:
    scrub_261()

    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_sci10_student_resync_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    print("Backup:", dest)

    bank = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert len(bank) == 300

    conn = sqlite3.connect(PROD_DB)
    ids = sci10_ids(conn)
    ua = qh = 0
    if ids:
        ph = ",".join("?" * len(ids))
        ua = conn.execute(
            f"SELECT COUNT(*) FROM user_answers WHERE question_id IN ({ph})", ids
        ).fetchone()[0]
        qh = conn.execute(
            f"SELECT COUNT(*) FROM question_history WHERE question_id IN ({ph})", ids
        ).fetchone()[0]
    preserve = {code: course_count(conn, code) for code in PRESERVE}
    ua_all = conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0]
    qh_all = conn.execute("SELECT COUNT(*) FROM question_history").fetchone()[0]
    print(f"Before: SCI10={len(ids)} ua_sci10={ua} qh_sci10={qh}")
    print("Preserved courses:", preserve)

    conn.execute("PRAGMA foreign_keys = ON")
    if ids:
        ph = ",".join("?" * len(ids))
        for table in (
            "user_answers",
            "quiz_attempt_questions",
            "question_history",
            "question_reports",
            "answer_choices",
        ):
            n = conn.execute(
                f"DELETE FROM {table} WHERE question_id IN ({ph})", ids
            ).rowcount
            print(f"Deleted {n} from {table}")
        n = conn.execute(f"DELETE FROM questions WHERE id IN ({ph})", ids).rowcount
        print(f"Deleted {n} SCI10 questions")
    conn.commit()
    conn.close()

    db = SessionLocal()
    try:
        import_questions(db, bank)
    finally:
        db.close()

    conn = sqlite3.connect(PROD_DB)
    after = {code: course_count(conn, code) for code in PRESERVE}
    sci10 = course_count(conn, "SCI10")
    ua_after = conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0]
    qh_after = conn.execute("SELECT COUNT(*) FROM question_history").fetchone()[0]
    conn.close()

    for code, before in preserve.items():
        if after[code] != before:
            raise SystemExit(f"{code} count changed {before}->{after[code]}")
    if sci10 != 300:
        raise SystemExit(f"SCI10 count {sci10} != 300")
    if ua_after != ua_all - ua:
        raise SystemExit(f"user_answers {ua_all}->{ua_after}, expected {ua_all - ua}")
    if qh_after != qh_all - qh:
        raise SystemExit(f"question_history {qh_all}->{qh_after}, expected {qh_all - qh}")
    print("SYNC OK: SCI10=300, other courses preserved, non-SCI10 user data preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
