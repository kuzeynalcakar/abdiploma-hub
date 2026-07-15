"""Backup, sync, and verify BIO30 production database."""
from __future__ import annotations

import json
import random
import shutil
import sqlite3
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database.update_bio30_questions import JSON_PATH, update_bio30_from_json

BACKEND = Path(__file__).resolve().parents[1]
PROD_DB = BACKEND / "albertaprep.db"
BACKUP_DIR = BACKEND / "backups"
BASE_API = "http://127.0.0.1:8000/api/v1"

CRITICAL_STEMS = [
    ("Order light pathway", "2413"),
    ("auditory pathway structures in the order", "2143"),
    ("insulin response to high blood glucose", "3124"),
    ("Order implantation events", "2413"),
    ("cross Pp × Pp show the dominant phenotype", "0.75"),
    ("cross Aa × Aa show the dominant phenotype", "0.75"),
]


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_bio30_sync_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    return dest


def count_boilerplate(conn: sqlite3.Connection) -> int:
    return conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'BIO30' AND q.explanation LIKE 'The correct answer is%'
        """
    ).fetchone()[0]


def verify_orphans(conn: sqlite3.Connection) -> list[str]:
    issues = []
    checks = [
        (
            "orphan user_answers",
            """
            SELECT COUNT(*) FROM user_answers ua
            LEFT JOIN questions q ON ua.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
        (
            "orphan answer_choices",
            """
            SELECT COUNT(*) FROM answer_choices ac
            LEFT JOIN questions q ON ac.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
        (
            "orphan question_history",
            """
            SELECT COUNT(*) FROM question_history qh
            LEFT JOIN questions q ON qh.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
    ]
    for label, sql in checks:
        n = conn.execute(sql).fetchone()[0]
        if n:
            issues.append(f"{label}: {n}")
    return issues


def verify_critical(conn: sqlite3.Connection, items: list[dict]) -> list[str]:
    issues = []
    json_by_stem = {item["question_text"]: item for item in items if item.get("course_code") == "BIO30"}
    for fragment, expected in CRITICAL_STEMS:
        row = conn.execute(
            """
            SELECT q.id, q.answer, q.explanation, q.question_text
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'BIO30' AND q.question_text LIKE ?
            """,
            (f"%{fragment}%",),
        ).fetchone()
        if not row:
            issues.append(f"Missing stem fragment: {fragment}")
            continue
        if str(row[1]) != expected:
            issues.append(f"Q{row[0]} answer {row[1]!r} != expected {expected!r}")
        json_item = next((v for k, v in json_by_stem.items() if fragment.lower() in k.lower()), None)
        if json_item and str(json_item.get("answer")) != expected:
            issues.append(f"JSON mismatch for {fragment}: {json_item.get('answer')!r}")
        if row[2] and row[2].startswith("The correct answer is"):
            issues.append(f"Q{row[0]} still has boilerplate explanation")
    return issues


def verify_quiz_api() -> list[str]:
    issues = []
    try:
        email = f"sync.verify.{random.randint(100000, 999999)}@example.com"
        token = json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    BASE_API + "/auth/register",
                    data=json.dumps(
                        {"name": "Sync Verify", "email": email, "password": "testpass123"}
                    ).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=10,
            ).read()
        )["token"]
        headers = {"Authorization": f"Bearer {token}"}
        bio = next(
            c
            for c in json.loads(
                urllib.request.urlopen(
                    urllib.request.Request(BASE_API + "/courses", headers=headers), timeout=10
                ).read()
            )["courses"]
            if c["code"] == "BIO30"
        )
        quiz = json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    BASE_API + f"/quiz/questions?course_id={bio['id']}&count=5", headers=headers
                ),
                timeout=10,
            ).read()
        )
        if not quiz.get("questions"):
            issues.append("Quiz API returned no questions")
    except Exception as exc:
        issues.append(f"Quiz API check skipped/unavailable: {exc}")
    return issues


def verify_quiz_attempts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    row = conn.execute(
        """
        SELECT COUNT(*) FROM quiz_attempts qa
        LEFT JOIN courses c ON qa.course_id = c.id
        WHERE qa.course_id IS NOT NULL AND c.id IS NULL
        """
    ).fetchone()[0]
    if row:
        issues.append(f"quiz_attempts with missing course: {row}")
    attempts = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    answers = conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0]
    if attempts == 0 and answers == 0:
        return issues
    sample = conn.execute(
        """
        SELECT qa.id, qa.user_id, qa.course_id, qa.completed_at IS NOT NULL
        FROM quiz_attempts qa
        ORDER BY qa.id DESC
        LIMIT 5
        """
    ).fetchall()
    for attempt_id, user_id, course_id, completed in sample:
        if user_id and conn.execute(
            "SELECT 1 FROM users WHERE id = ?", (user_id,)
        ).fetchone() is None:
            issues.append(f"attempt {attempt_id} references missing user {user_id}")
        if course_id and conn.execute(
            "SELECT 1 FROM courses WHERE id = ?", (course_id,)
        ).fetchone() is None:
            issues.append(f"attempt {attempt_id} references missing course {course_id}")
    return issues


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    boiler_before = count_boilerplate(sqlite3.connect(PROD_DB))

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")

    engine = create_engine(f"sqlite:///{PROD_DB.as_posix()}")
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        result = update_bio30_from_json(db, items)
    finally:
        db.close()

    conn = sqlite3.connect(PROD_DB)
    bio_count = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'BIO30' AND q.is_active = 1
        """
    ).fetchone()[0]
    boiler_after = count_boilerplate(conn)
    orphan_issues = verify_orphans(conn)
    critical_issues = verify_critical(conn, items)
    attempt_issues = verify_quiz_attempts(conn)
    api_issues = verify_quiz_api()
    conn.close()

    print("\n=== SYNC RESULT ===")
    print(f"Rows updated: {result['updated']}")
    print(f"Rows unchanged: {result['skipped']}")
    print(f"Not found in DB: {result['not_found']}")
    print(f"Updated question IDs: {result['updated_question_ids']}")
    print(f"BIO30 count: {bio_count}")
    print(f"Boilerplate explanations: {boiler_before} -> {boiler_after}")
    print(f"Question IDs preserved: {result['ids_preserved']}")
    print(f"User progress preserved: {result['progress_preserved']}")
    print(f"user_answers: {result['before']['user_answers']} -> {result['after']['user_answers']}")
    print(f"question_history: {result['before']['question_history']} -> {result['after']['question_history']}")
    print(f"quiz_attempts: {result['before']['quiz_attempts']} -> {result['after']['quiz_attempts']}")
    print(f"JSON verify failures: {result['verify_failures']}")
    print(f"Duplicate stems: {result['duplicate_stems']}")

    all_issues = orphan_issues + critical_issues + attempt_issues + api_issues
    if result["errors"]:
        all_issues.extend(result["errors"])
    if bio_count < 300:
        all_issues.append(f"BIO30 count {bio_count} < 300")
    if not result["ids_preserved"]:
        all_issues.append("Question IDs changed")
    if not result["progress_preserved"]:
        all_issues.append("User progress counts changed")
    if result["verify_failures"]:
        all_issues.append(f"{result['verify_failures']} post-sync field mismatches")

    print("\n=== VALIDATION ===")
    if all_issues:
        for issue in all_issues:
            print(f"FAIL: {issue}")
        return 1

    print("All validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
