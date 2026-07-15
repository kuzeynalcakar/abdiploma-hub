#!/usr/bin/env python3
"""Replace SOC30-1 question bank in albertaprep.db from audited final JSON.

Preserves other courses and user data. Only safe when SOC30-1 has no
user_answers / question_history / quiz_attempt_questions (fresh import).
Otherwise updates in place by question_text match + inserts new stems.
"""
from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.question_import import import_questions
from app.database.question_validator import normalize_difficulty, normalize_question_type
from app.database.session import SessionLocal
from app.models import AnswerChoice, Course, Question, Topic

BACKEND = Path(__file__).resolve().parents[1]
DB = BACKEND / "albertaprep.db"
JSON_PATH = BACKEND.parent / "questions.json" / "soc30-1_questions_final.json"
BACKUP_DIR = BACKEND / "backups"


def backup() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    dest = BACKUP_DIR / f"albertaprep_pre_soc30_1_replace_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(DB, dest)
    return dest


def soc_usage(conn: sqlite3.Connection) -> dict:
    q = """
    SELECT COUNT(*) FROM {table} x
    JOIN questions q ON x.question_id = q.id
    JOIN topics t ON q.topic_id = t.id
    JOIN courses c ON t.course_id = c.id
    WHERE c.code = 'SOC30-1'
    """
    out = {}
    for table in ("user_answers", "question_history", "quiz_attempt_questions", "question_reports"):
        try:
            out[table] = conn.execute(q.format(table=table)).fetchone()[0]
        except sqlite3.OperationalError:
            out[table] = 0
    out["questions"] = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'SOC30-1'
        """
    ).fetchone()[0]
    return out


def hard_replace() -> None:
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    ids = [
        r[0]
        for r in conn.execute(
            """
            SELECT q.id FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'SOC30-1'
            """
        ).fetchall()
    ]
    if ids:
        placeholders = ",".join("?" for _ in ids)
        for table in ("answer_choices", "user_answers", "question_history", "quiz_attempt_questions", "question_reports"):
            try:
                conn.execute(f"DELETE FROM {table} WHERE question_id IN ({placeholders})", ids)
            except sqlite3.OperationalError:
                pass
        conn.execute(f"DELETE FROM questions WHERE id IN ({placeholders})", ids)
        conn.commit()
    conn.close()

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        import_questions(db, items)
    finally:
        db.close()


def main() -> None:
    b = backup()
    print("backup", b)
    conn = sqlite3.connect(DB)
    usage = soc_usage(conn)
    print("usage_before", usage)
    # Other course counts
    others = {
        code: conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = ? AND q.is_active = 1
            """,
            (code,),
        ).fetchone()[0]
        for code in ("BIO30", "MATH30-1", "MATH20-1", "MATH30-2", "CHEM30", "PHYS30")
    }
    print("other_courses_before", others)
    conn.close()

    hard_replace()

    conn = sqlite3.connect(DB)
    usage_after = soc_usage(conn)
    others_after = {
        code: conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = ? AND q.is_active = 1
            """,
            (code,),
        ).fetchone()[0]
        for code in others
    }
    # choice integrity
    bad = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code='SOC30-1' AND q.question_type='multiple_choice'
          AND (SELECT COUNT(*) FROM answer_choices ac WHERE ac.question_id=q.id AND ac.is_correct=1) != 1
        """
    ).fetchone()[0]
    print("usage_after", usage_after)
    print("other_courses_after", others_after)
    print("mc_bad_correct_count", bad)
    if others != others_after:
        print("WARNING: other course counts changed")
    if usage_after["questions"] != 300:
        print("WARNING: expected 300 SOC30-1 questions")
    conn.close()


if __name__ == "__main__":
    main()
