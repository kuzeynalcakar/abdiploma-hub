"""Import CHEM30 production bank with backup, safety checks, and verification."""

from __future__ import annotations

import json
import random
import shutil
import sqlite3
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.curriculum_seed import seed_curriculum
from app.database.question_import import import_questions
from app.database.session import SessionLocal
from app.models import Course, Question, QuestionHistory, QuizAttempt, Topic, TopicPerformance, UserAnswer

BACKEND = Path(__file__).resolve().parents[1]
PROD_DB = BACKEND / "albertaprep.db"
BACKUP_DIR = BACKEND / "backups"
JSON_PATH = BACKEND.parent / "questions.json" / "chemistry30_questions_final.json"
BASE_API = "http://127.0.0.1:8000/api/v1"

CHEM30_TOPIC_TARGETS = {
    "Thermochemical Changes": 70,
    "Electrochemical Changes": 83,
    "Chemical Changes of Organic Compounds": 70,
    "Chemical Equilibrium Focusing on Acid-Base Systems": 77,
}
CHEM30_TOTAL = 300


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_chem30_import_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    return dest


def snapshot_existing(conn: sqlite3.Connection) -> dict:
    existing_ids = {
        row[0]
        for row in conn.execute(
            """
            SELECT q.id FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code IN ('BIO30', 'MATH30-1') AND q.is_active = 1
            """
        ).fetchall()
    }
    return {
        "existing_question_ids": existing_ids,
        "user_answers": conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0],
        "question_history": conn.execute("SELECT COUNT(*) FROM question_history").fetchone()[0],
        "quiz_attempts": conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0],
        "bio30_count": conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'BIO30' AND q.is_active = 1
            """
        ).fetchone()[0],
        "math_count": conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'MATH30-1' AND q.is_active = 1
            """
        ).fetchone()[0],
        "chem30_count": conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'CHEM30' AND q.is_active = 1
            """
        ).fetchone()[0],
    }


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


def verify_existing_ids_preserved(before: dict, after: dict) -> list[str]:
    issues = []
    if before["existing_question_ids"] != after["existing_question_ids"]:
        missing = before["existing_question_ids"] - after["existing_question_ids"]
        added = after["existing_question_ids"] - before["existing_question_ids"]
        if missing:
            issues.append(f"Existing question IDs removed: {sorted(missing)[:10]}")
        if added:
            issues.append(f"Unexpected changes to existing ID set (+{len(added)})")
    if before["user_answers"] != after["user_answers"]:
        issues.append(
            f"user_answers changed: {before['user_answers']} -> {after['user_answers']}"
        )
    if before["question_history"] != after["question_history"]:
        issues.append(
            f"question_history changed: {before['question_history']} -> {after['question_history']}"
        )
    if before["quiz_attempts"] != after["quiz_attempts"]:
        issues.append(
            f"quiz_attempts changed: {before['quiz_attempts']} -> {after['quiz_attempts']}"
        )
    if before["bio30_count"] != after["bio30_count"]:
        issues.append(
            f"BIO30 count changed: {before['bio30_count']} -> {after['bio30_count']}"
        )
    if before["math_count"] != after["math_count"]:
        issues.append(
            f"MATH30-1 count changed: {before['math_count']} -> {after['math_count']}"
        )
    return issues


CHEM30_LEGACY_TOPICS = ("Chemical Equilibrium and Acid-Base Systems",)


def cleanup_legacy_chem30_topics(db) -> int:
    """Remove empty legacy CHEM30 demo topics that predate curriculum_seed rename."""
    course = db.query(Course).filter(Course.code == "CHEM30").first()
    if course is None:
        return 0
    removed = 0
    for name in CHEM30_LEGACY_TOPICS:
        topic = (
            db.query(Topic)
            .filter(Topic.course_id == course.id, Topic.name == name)
            .first()
        )
        if topic is None:
            continue
        if db.query(Question).filter(Question.topic_id == topic.id).count():
            continue
        if (
            db.query(QuizAttempt).filter(QuizAttempt.topic_id == topic.id).count()
            + db.query(TopicPerformance).filter(TopicPerformance.topic_id == topic.id).count()
        ):
            continue
        db.delete(topic)
        removed += 1
    if removed:
        db.commit()
    return removed


def verify_chem30_counts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    total = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'CHEM30' AND q.is_active = 1
        """
    ).fetchone()[0]
    if total != CHEM30_TOTAL:
        issues.append(f"CHEM30 total {total} != {CHEM30_TOTAL}")

    rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'CHEM30'
        GROUP BY t.name
        ORDER BY t.name
        """
    ).fetchall()
    for name, count in rows:
        if count == 0:
            continue
        expected = CHEM30_TOPIC_TARGETS.get(name)
        if expected is None:
            issues.append(f"Unexpected CHEM30 topic with questions: {name} ({count})")
        elif count != expected:
            issues.append(f"Topic {name}: {count} != expected {expected}")

    dupes = conn.execute(
        """
        SELECT q.question_text, COUNT(*) n
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'CHEM30' AND q.is_active = 1
        GROUP BY q.question_text
        HAVING n > 1
        """
    ).fetchall()
    if dupes:
        issues.append(f"{len(dupes)} duplicate CHEM30 stems in DB")

    return issues


def api_request(path: str, *, method: str = "GET", data: dict | None = None, token: str | None = None):
    headers = {}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(BASE_API + path, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def verify_api_endpoints(conn: sqlite3.Connection) -> list[str]:
    issues = []
    try:
        email = f"chem30.import.{random.randint(100000, 999999)}@example.com"
        token = api_request(
            "/auth/register",
            method="POST",
            data={"name": "Chem30 Import Verify", "email": email, "password": "testpass123"},
        )["access_token"]
        headers_token = token

        courses = api_request("/courses", token=headers_token)["courses"]
        chem = next((c for c in courses if c["code"] == "CHEM30"), None)
        if chem is None:
            issues.append("CHEM30 not listed in /courses")
            return issues

        if chem.get("question_count", 0) < CHEM30_TOTAL:
            issues.append(
                f"/courses CHEM30 question_count {chem.get('question_count')} < {CHEM30_TOTAL}"
            )

        topics = api_request(f"/courses/{chem['id']}/topics", token=headers_token)["topics"]
        if len(topics) != 4:
            issues.append(f"/courses/{{id}}/topics returned {len(topics)} topics, expected 4")

        try:
            available = api_request(
                f"/quiz/available-count?course_id={chem['id']}", token=headers_token
            )
            if available.get("available_count", 0) < 10:
                issues.append(
                    f"/quiz/available-count too low: {available.get('available_count')}"
                )
        except Exception as exc:
            issues.append(f"/quiz/available-count failed: {exc}")

        try:
            quiz = api_request(
                f"/quiz/questions?course_id={chem['id']}&count=10", token=headers_token
            )
            if len(quiz.get("questions", [])) < 10:
                issues.append(f"/quiz/questions returned {len(quiz.get('questions', []))} questions")
        except Exception as exc:
            issues.append(f"/quiz/questions failed: {exc}")

        try:
            progress = api_request("/progress", token=headers_token)
            if "courses" not in progress:
                issues.append("/progress missing courses field")
            if "practice_streak" not in progress:
                issues.append("/progress missing practice_streak field")
        except Exception as exc:
            issues.append(f"/progress failed: {exc}")

        try:
            daily = api_request(f"/daily-practice?course_id={chem['id']}", token=headers_token)
            for field in ("is_completed", "is_started", "total_questions", "topics_included"):
                if field not in daily:
                    issues.append(f"/daily-practice missing {field}")
        except Exception as exc:
            issues.append(f"/daily-practice failed: {exc}")

        try:
            daily_start = api_request(
                f"/daily-practice/start?course_id={chem['id']}",
                method="POST",
                token=headers_token,
            )
            if not daily_start.get("questions"):
                issues.append("/daily-practice/start returned no questions")
        except Exception as exc:
            issues.append(f"/daily-practice/start failed: {exc}")

        try:
            weakness = api_request(f"/weakness-map?course_id={chem['id']}", token=headers_token)
            if "topics" not in weakness:
                issues.append("/weakness-map missing topics field")
            elif len(weakness.get("topics", [])) != 4:
                issues.append(
                    f"/weakness-map returned {len(weakness.get('topics', []))} topics, expected 4"
                )
        except Exception as exc:
            issues.append(f"/weakness-map failed: {exc}")

        sample_mc = conn.execute(
            """
            SELECT q.id, ac.id
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            JOIN answer_choices ac ON ac.question_id = q.id AND ac.is_correct = 1
            WHERE c.code = 'CHEM30' AND q.question_type = 'multiple_choice'
            LIMIT 1
            """
        ).fetchone()
        if sample_mc:
            try:
                grade = api_request(
                    "/quiz/guest/grade",
                    method="POST",
                    data={"question_id": sample_mc[0], "answer_choice_id": sample_mc[1]},
                )
                if not grade.get("is_correct"):
                    issues.append(f"Guest grade failed for MC Q{sample_mc[0]}")
            except Exception as exc:
                issues.append(f"Guest MC grade failed: {exc}")

        sample_nr = conn.execute(
            """
            SELECT q.id, q.answer FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'CHEM30' AND q.question_type = 'numerical_response'
            LIMIT 1
            """
        ).fetchone()
        if sample_nr:
            try:
                grade = api_request(
                    "/quiz/guest/grade",
                    method="POST",
                    data={"question_id": sample_nr[0], "response_text": str(sample_nr[1])},
                )
                if not grade.get("is_correct"):
                    issues.append(f"Guest grade failed for NR Q{sample_nr[0]}")
            except Exception as exc:
                issues.append(f"Guest NR grade failed: {exc}")

    except urllib.error.URLError as exc:
        issues.append(f"API verification skipped (server unavailable): {exc}")
    except Exception as exc:
        issues.append(f"API verification error: {exc}")

    return issues


def run_import(items: list[dict]) -> None:
    db = SessionLocal()
    try:
        seed_curriculum(db)
        import_questions(db, items)
        removed = cleanup_legacy_chem30_topics(db)
        if removed:
            print(f"Removed {removed} legacy empty CHEM30 topic(s)")
    finally:
        db.close()


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")
    if not JSON_PATH.is_file():
        raise SystemExit(f"JSON bank not found: {JSON_PATH}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    chem_items = [i for i in items if i.get("course_code") == "CHEM30"]
    if len(chem_items) != CHEM30_TOTAL:
        raise SystemExit(f"Expected {CHEM30_TOTAL} CHEM30 items, got {len(chem_items)}")

    conn = sqlite3.connect(PROD_DB)
    before = snapshot_existing(conn)
    conn.close()

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")
    print(f"Before import — BIO30: {before['bio30_count']}, MATH30-1: {before['math_count']}, "
          f"CHEM30: {before['chem30_count']}")
    print(f"Before import — user_answers: {before['user_answers']}, "
          f"question_history: {before['question_history']}, quiz_attempts: {before['quiz_attempts']}")

    if before["chem30_count"] == 0:
        print("Importing CHEM30 production bank...")
        run_import(items)
    elif before["chem30_count"] == CHEM30_TOTAL:
        print("CHEM30 already imported (300 questions). Re-running import for duplicate-skip check only.")
        run_import(items)
        conn = sqlite3.connect(PROD_DB)
        skipped_only = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'CHEM30' AND q.is_active = 1
            """
        ).fetchone()[0]
        conn.close()
        if skipped_only != CHEM30_TOTAL:
            raise SystemExit("Duplicate import changed CHEM30 question count")
        print("Duplicate import check: 0 new rows (all 300 skipped as expected)")
    else:
        raise SystemExit(
            f"Partial CHEM30 import detected ({before['chem30_count']} questions). "
            "Restore from backup before retrying."
        )

    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues = []
    issues.extend(verify_existing_ids_preserved(before, after))
    issues.extend(verify_orphans(conn))
    issues.extend(verify_chem30_counts(conn))
    issues.extend(verify_api_endpoints(conn))
    conn.close()

    print("\n=== IMPORT RESULT ===")
    print(f"CHEM30 count: {before['chem30_count']} -> {after['chem30_count']}")
    print(f"BIO30 count: {before['bio30_count']} -> {after['bio30_count']}")
    print(f"MATH30-1 count: {before['math_count']} -> {after['math_count']}")
    print(f"user_answers: {before['user_answers']} -> {after['user_answers']}")
    print(f"question_history: {before['question_history']} -> {after['question_history']}")
    print(f"quiz_attempts: {before['quiz_attempts']} -> {after['quiz_attempts']}")
    print(f"Existing production IDs preserved: "
          f"{before['existing_question_ids'] == after['existing_question_ids']}")

    print("\n=== VALIDATION ===")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        return 1

    print("All import and verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
