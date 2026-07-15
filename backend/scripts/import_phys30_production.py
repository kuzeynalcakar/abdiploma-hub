"""Import PHYS30 production bank with backup, safety checks, and verification."""

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

from app.database.curriculum_seed import seed_curriculum
from app.database.question_import import import_questions
from app.database.session import SessionLocal

BACKEND = Path(__file__).resolve().parents[1]
PROD_DB = BACKEND / "albertaprep.db"
BACKUP_DIR = BACKEND / "backups"
JSON_PATH = BACKEND.parent / "questions.json" / "physics30_questions_final.json"
REPORT_PATH = BACKEND.parent / "questions.json" / "phys30_production_readiness_report.json"
BASE_API = "http://127.0.0.1:8000/api/v1"

PHYS30_TOPIC_TARGETS = {
    "Momentum and Impulse": 44,
    "Forces and Fields": 90,
    "Electromagnetic Radiation": 90,
    "Atomic Physics": 76,
}
PHYS30_TOTAL = 300
PRESERVE_COURSES = ("BIO30", "MATH30-1", "CHEM30")


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_phys30_import_{stamp}.db"
    shutil.copy2(PROD_DB, dest)
    return dest


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


def snapshot_existing(conn: sqlite3.Connection) -> dict:
    placeholders = ",".join("?" for _ in PRESERVE_COURSES)
    existing_ids = {
        row[0]
        for row in conn.execute(
            f"""
            SELECT q.id FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code IN ({placeholders}) AND q.is_active = 1
            """,
            PRESERVE_COURSES,
        ).fetchall()
    }
    return {
        "existing_question_ids": existing_ids,
        "user_answers": conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0],
        "question_history": conn.execute("SELECT COUNT(*) FROM question_history").fetchone()[0],
        "quiz_attempts": conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0],
        "topic_performance": conn.execute("SELECT COUNT(*) FROM topic_performance").fetchone()[0],
        "bio30_count": course_count(conn, "BIO30"),
        "math_count": course_count(conn, "MATH30-1"),
        "chem30_count": course_count(conn, "CHEM30"),
        "phys30_count": course_count(conn, "PHYS30"),
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
        if missing:
            issues.append(f"Existing question IDs removed: {sorted(missing)[:10]}")
    for field in ("user_answers", "question_history", "quiz_attempts", "topic_performance"):
        if before[field] != after[field]:
            issues.append(f"{field} changed: {before[field]} -> {after[field]}")
    for code, key in (
        ("BIO30", "bio30_count"),
        ("MATH30-1", "math_count"),
        ("CHEM30", "chem30_count"),
    ):
        if before[key] != after[key]:
            issues.append(f"{code} count changed: {before[key]} -> {after[key]}")
    return issues


def verify_phys30_counts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    total = course_count(conn, "PHYS30")
    if total != PHYS30_TOTAL:
        issues.append(f"PHYS30 total {total} != {PHYS30_TOTAL}")

    rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'PHYS30'
        GROUP BY t.name
        ORDER BY t.name
        """
    ).fetchall()
    for name, count in rows:
        if count == 0:
            continue
        expected = PHYS30_TOPIC_TARGETS.get(name)
        if expected is None:
            issues.append(f"Unexpected PHYS30 topic with questions: {name} ({count})")
        elif count != expected:
            issues.append(f"Topic {name}: {count} != expected {expected}")

    dupes = conn.execute(
        """
        SELECT q.question_text, COUNT(*) n
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'PHYS30' AND q.is_active = 1
        GROUP BY q.question_text
        HAVING n > 1
        """
    ).fetchall()
    if dupes:
        issues.append(f"{len(dupes)} duplicate PHYS30 stems in DB")

    type_rows = conn.execute(
        """
        SELECT q.question_type, COUNT(*)
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'PHYS30' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()
    type_counts = dict(type_rows)
    if type_counts.get("multiple_choice", 0) != 222:
        issues.append(f"PHYS30 MC count {type_counts.get('multiple_choice', 0)} != 222")
    if type_counts.get("numerical_response", 0) != 78:
        issues.append(f"PHYS30 NR count {type_counts.get('numerical_response', 0)} != 78")

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


def verify_api_endpoints(conn: sqlite3.Connection) -> tuple[list[str], dict]:
    issues = []
    details: dict = {}
    try:
        email = f"phys30.import.{random.randint(100000, 999999)}@example.com"
        token = api_request(
            "/auth/register",
            method="POST",
            data={"name": "Phys30 Import Verify", "email": email, "password": "testpass123"},
        )["access_token"]

        courses = api_request("/courses", token=token)["courses"]
        phys = next((c for c in courses if c["code"] == "PHYS30"), None)
        details["courses_listed"] = phys is not None
        if phys is None:
            issues.append("PHYS30 not listed in /courses")
            return issues, details

        details["course_question_count"] = phys.get("question_count", 0)
        if phys.get("question_count", 0) < PHYS30_TOTAL:
            issues.append(
                f"/courses PHYS30 question_count {phys.get('question_count')} < {PHYS30_TOTAL}"
            )

        topics = api_request(f"/courses/{phys['id']}/topics", token=token)["topics"]
        details["topic_count"] = len(topics)
        if len(topics) != 4:
            issues.append(f"/courses/{{id}}/topics returned {len(topics)} topics, expected 4")

        available = api_request(
            f"/quiz/available-count?course_id={phys['id']}", token=token
        )
        details["quiz_available_count"] = available.get("available_count", 0)
        if available.get("available_count", 0) < 10:
            issues.append(f"/quiz/available-count too low: {available.get('available_count')}")

        quiz = api_request(
            f"/quiz/questions?course_id={phys['id']}&count=10", token=token
        )
        details["quiz_questions_returned"] = len(quiz.get("questions", []))
        if len(quiz.get("questions", [])) < 10:
            issues.append(f"/quiz/questions returned {len(quiz.get('questions', []))} questions")

        progress = api_request("/progress", token=token)
        details["progress_courses"] = len(progress.get("courses", []))
        if "courses" not in progress:
            issues.append("/progress missing courses field")
        if "practice_streak" not in progress:
            issues.append("/progress missing practice_streak field")
        # New users have no TopicPerformance yet; PHYS30 appears after first practice.
        details["progress_has_practice_streak"] = "practice_streak" in progress

        daily = api_request(f"/daily-practice?course_id={phys['id']}", token=token)
        for field in ("is_completed", "is_started", "total_questions", "topics_included"):
            if field not in daily:
                issues.append(f"/daily-practice missing {field}")
        details["daily_practice_total"] = daily.get("total_questions")

        daily_start = api_request(
            f"/daily-practice/start?course_id={phys['id']}",
            method="POST",
            token=token,
        )
        details["daily_practice_started"] = len(daily_start.get("questions", []))
        if not daily_start.get("questions"):
            issues.append("/daily-practice/start returned no questions")

        weakness = api_request(f"/weakness-map?course_id={phys['id']}", token=token)
        details["weakness_map_topics"] = len(weakness.get("topics", []))
        if "topics" not in weakness:
            issues.append("/weakness-map missing topics field")
        elif len(weakness.get("topics", [])) != 4:
            issues.append(
                f"/weakness-map returned {len(weakness.get('topics', []))} topics, expected 4"
            )

        sample_mc = conn.execute(
            """
            SELECT q.id, ac.id
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            JOIN answer_choices ac ON ac.question_id = q.id AND ac.is_correct = 1
            WHERE c.code = 'PHYS30' AND q.question_type = 'multiple_choice'
            LIMIT 1
            """
        ).fetchone()
        if sample_mc:
            grade = api_request(
                "/quiz/guest/grade",
                method="POST",
                data={"question_id": sample_mc[0], "answer_choice_id": sample_mc[1]},
            )
            details["guest_mc_grade"] = grade.get("is_correct")
            if not grade.get("is_correct"):
                issues.append(f"Guest grade failed for MC Q{sample_mc[0]}")

        sample_nr = conn.execute(
            """
            SELECT q.id, q.answer FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'PHYS30' AND q.question_type = 'numerical_response'
            LIMIT 1
            """
        ).fetchone()
        if sample_nr:
            grade = api_request(
                "/quiz/guest/grade",
                method="POST",
                data={"question_id": sample_nr[0], "response_text": str(sample_nr[1])},
            )
            details["guest_nr_grade"] = grade.get("is_correct")
            if not grade.get("is_correct"):
                issues.append(f"Guest grade failed for NR Q{sample_nr[0]}")

    except urllib.error.URLError as exc:
        issues.append(f"API verification skipped (server unavailable): {exc}")
        details["api_available"] = False
    except Exception as exc:
        issues.append(f"API verification error: {exc}")
        details["api_available"] = False
    else:
        details["api_available"] = True

    return issues, details


def run_import(items: list[dict]) -> tuple[int, int]:
    db = SessionLocal()
    try:
        seed_curriculum(db)
        before = course_count(sqlite3.connect(PROD_DB), "PHYS30")
        import_questions(db, items)
        after = course_count(sqlite3.connect(PROD_DB), "PHYS30")
        return before, after
    finally:
        db.close()


def build_report(
    *,
    backup_path: Path,
    before: dict,
    after: dict,
    issues: list[str],
    api_details: dict,
) -> dict:
    topic_rows = sqlite3.connect(PROD_DB).execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'PHYS30'
        GROUP BY t.name
        ORDER BY t.sort_order
        """
    ).fetchall()

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY" if not issues else "BLOCKED",
        "backup": str(backup_path),
        "json_source": str(JSON_PATH),
        "import_summary": {
            "phys30_before": before["phys30_count"],
            "phys30_after": after["phys30_count"],
            "imported_new": after["phys30_count"] - before["phys30_count"],
        },
        "data_preservation": {
            "production_ids_preserved": before["existing_question_ids"] == after["existing_question_ids"],
            "preserved_courses": list(PRESERVE_COURSES),
            "user_answers": {"before": before["user_answers"], "after": after["user_answers"]},
            "question_history": {"before": before["question_history"], "after": after["question_history"]},
            "quiz_attempts": {"before": before["quiz_attempts"], "after": after["quiz_attempts"]},
            "topic_performance": {"before": before["topic_performance"], "after": after["topic_performance"]},
            "bio30_count": {"before": before["bio30_count"], "after": after["bio30_count"]},
            "math30_1_count": {"before": before["math_count"], "after": after["math_count"]},
            "chem30_count": {"before": before["chem30_count"], "after": after["chem30_count"]},
        },
        "phys30_counts": {
            "total": after["phys30_count"],
            "target": PHYS30_TOTAL,
            "by_topic": {name: count for name, count in topic_rows},
            "topic_targets": PHYS30_TOPIC_TARGETS,
        },
        "api_verification": api_details,
        "issues": issues,
    }


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")
    if not JSON_PATH.is_file():
        raise SystemExit(f"JSON bank not found: {JSON_PATH}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    phys_items = [i for i in items if i.get("course_code") == "PHYS30"]
    if len(phys_items) != PHYS30_TOTAL:
        raise SystemExit(f"Expected {PHYS30_TOTAL} PHYS30 items, got {len(phys_items)}")

    conn = sqlite3.connect(PROD_DB)
    before = snapshot_existing(conn)
    conn.close()

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")
    print(
        f"Before import — BIO30: {before['bio30_count']}, MATH30-1: {before['math_count']}, "
        f"CHEM30: {before['chem30_count']}, PHYS30: {before['phys30_count']}"
    )
    print(
        f"Before import — user_answers: {before['user_answers']}, "
        f"question_history: {before['question_history']}, quiz_attempts: {before['quiz_attempts']}"
    )

    if before["phys30_count"] == 0:
        print("Importing PHYS30 production bank...")
        run_import(items)
    elif before["phys30_count"] == PHYS30_TOTAL:
        print("PHYS30 already imported (300 questions). Re-running import for duplicate-skip check only.")
        run_import(items)
        conn = sqlite3.connect(PROD_DB)
        count = course_count(conn, "PHYS30")
        conn.close()
        if count != PHYS30_TOTAL:
            raise SystemExit("Duplicate import changed PHYS30 question count")
        print("Duplicate import check: 0 new rows (all 300 skipped as expected)")
    else:
        raise SystemExit(
            f"Partial PHYS30 import detected ({before['phys30_count']} questions). "
            "Restore from backup before retrying."
        )

    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues = []
    issues.extend(verify_existing_ids_preserved(before, after))
    issues.extend(verify_orphans(conn))
    issues.extend(verify_phys30_counts(conn))
    api_issues, api_details = verify_api_endpoints(conn)
    issues.extend(api_issues)
    conn.close()

    report = build_report(
        backup_path=backup_path,
        before=before,
        after=after,
        issues=issues,
        api_details=api_details,
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== IMPORT RESULT ===")
    print(f"PHYS30 count: {before['phys30_count']} -> {after['phys30_count']}")
    print(f"BIO30 count: {before['bio30_count']} -> {after['bio30_count']}")
    print(f"MATH30-1 count: {before['math_count']} -> {after['math_count']}")
    print(f"CHEM30 count: {before['chem30_count']} -> {after['chem30_count']}")
    print(f"user_answers: {before['user_answers']} -> {after['user_answers']}")
    print(f"question_history: {before['question_history']} -> {after['question_history']}")
    print(f"quiz_attempts: {before['quiz_attempts']} -> {after['quiz_attempts']}")
    print(
        f"Existing production IDs preserved: "
        f"{before['existing_question_ids'] == after['existing_question_ids']}"
    )

    print("\n=== VALIDATION ===")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        print(f"\nReport written: {REPORT_PATH}")
        return 1

    print("All import and verification checks passed.")
    print(f"Report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
