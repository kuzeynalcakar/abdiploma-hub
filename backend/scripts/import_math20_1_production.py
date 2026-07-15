"""Import MATH20-1 production bank with backup, safety checks, and verification."""

from __future__ import annotations

import json
import random
import shutil
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.curriculum_seed import seed_curriculum
from app.database.question_import import import_questions
from app.database.session import SessionLocal

BACKEND = Path(__file__).resolve().parents[1]
PROD_DB = BACKEND / "albertaprep.db"
BACKUP_DIR = BACKEND / "backups"
JSON_PATH = BACKEND.parent / "questions.json" / "math20-1_questions_final.json"
REPORT_PATH = BACKEND.parent / "questions.json" / "math20-1_production_readiness_report.json"
MD_REPORT_PATH = BACKEND.parent / "questions.json" / "MATH20-1_PRODUCTION_READINESS_REPORT.md"
BASE_API = "http://127.0.0.1:8000/api/v1"

MATH20_1_TOPIC_TARGETS = {
    "Quadratic Equations": 52,
    "Rational Expressions and Equations": 45,
    "Trigonometry": 45,
    "Quadratic Functions": 36,
    "Absolute Value and Reciprocal Functions": 36,
    "Radical Expressions and Equations": 30,
    "Sequences and Series": 23,
    "Linear and Quadratic Inequalities": 18,
    "Systems of Equations": 15,
}
MATH20_1_TOTAL = 300
MATH20_1_MC = 139
MATH20_1_NR = 161
PRESERVE_COURSES = ("BIO30", "MATH30-1", "CHEM30", "PHYS30")


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_math20_1_import_{stamp}.db"
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
        "math30_1_count": course_count(conn, "MATH30-1"),
        "chem30_count": course_count(conn, "CHEM30"),
        "phys30_count": course_count(conn, "PHYS30"),
        "math20_1_count": course_count(conn, "MATH20-1"),
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
        ("MATH30-1", "math30_1_count"),
        ("CHEM30", "chem30_count"),
        ("PHYS30", "phys30_count"),
    ):
        if before[key] != after[key]:
            issues.append(f"{code} count changed: {before[key]} -> {after[key]}")
    return issues


def verify_math20_1_counts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    total = course_count(conn, "MATH20-1")
    if total != MATH20_1_TOTAL:
        issues.append(f"MATH20-1 total {total} != {MATH20_1_TOTAL}")

    rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'MATH20-1'
        GROUP BY t.name
        ORDER BY t.name
        """
    ).fetchall()
    for name, count in rows:
        if count == 0:
            continue
        expected = MATH20_1_TOPIC_TARGETS.get(name)
        if expected is None:
            issues.append(f"Unexpected MATH20-1 topic with questions: {name} ({count})")
        elif count != expected:
            issues.append(f"Topic {name}: {count} != expected {expected}")

    dupes = conn.execute(
        """
        SELECT q.question_text, COUNT(*) n
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'MATH20-1' AND q.is_active = 1
        GROUP BY q.question_text
        HAVING n > 1
        """
    ).fetchall()
    if dupes:
        issues.append(f"{len(dupes)} duplicate MATH20-1 stems in DB")

    type_rows = conn.execute(
        """
        SELECT q.question_type, COUNT(*)
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'MATH20-1' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()
    type_counts = dict(type_rows)
    if type_counts.get("multiple_choice", 0) != MATH20_1_MC:
        issues.append(
            f"MATH20-1 MC count {type_counts.get('multiple_choice', 0)} != {MATH20_1_MC}"
        )
    if type_counts.get("numerical_response", 0) != MATH20_1_NR:
        issues.append(
            f"MATH20-1 NR count {type_counts.get('numerical_response', 0)} != {MATH20_1_NR}"
        )

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
        email = f"math20_1.import.{random.randint(100000, 999999)}@example.com"
        token = api_request(
            "/auth/register",
            method="POST",
            data={"name": "Math20-1 Import Verify", "email": email, "password": "testpass123"},
        )["access_token"]

        courses = api_request("/courses", token=token)["courses"]
        math20 = next((c for c in courses if c["code"] == "MATH20-1"), None)
        details["courses_listed"] = math20 is not None
        if math20 is None:
            issues.append("MATH20-1 not listed in /courses")
            return issues, details

        details["course_question_count"] = math20.get("question_count", 0)
        if math20.get("question_count", 0) < MATH20_1_TOTAL:
            issues.append(
                f"/courses MATH20-1 question_count {math20.get('question_count')} < {MATH20_1_TOTAL}"
            )

        topics = api_request(f"/courses/{math20['id']}/topics", token=token)["topics"]
        details["topic_count"] = len(topics)
        if len(topics) != 9:
            issues.append(f"/courses/{{id}}/topics returned {len(topics)} topics, expected 9")

        available = api_request(
            f"/quiz/available-count?course_id={math20['id']}", token=token
        )
        details["quiz_available_count"] = available.get("available_count", 0)
        if available.get("available_count", 0) < 10:
            issues.append(f"/quiz/available-count too low: {available.get('available_count')}")

        quiz = api_request(
            f"/quiz/questions?course_id={math20['id']}&count=10", token=token
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
        details["progress_has_practice_streak"] = "practice_streak" in progress

        daily = api_request(f"/daily-practice?course_id={math20['id']}", token=token)
        for field in ("is_completed", "is_started", "total_questions", "topics_included"):
            if field not in daily:
                issues.append(f"/daily-practice missing {field}")
        details["daily_practice_total"] = daily.get("total_questions")

        daily_start = api_request(
            f"/daily-practice/start?course_id={math20['id']}",
            method="POST",
            token=token,
        )
        details["daily_practice_started"] = len(daily_start.get("questions", []))
        if not daily_start.get("questions"):
            issues.append("/daily-practice/start returned no questions")

        weakness = api_request(f"/weakness-map?course_id={math20['id']}", token=token)
        details["weakness_map_topics"] = len(weakness.get("topics", []))
        if "topics" not in weakness:
            issues.append("/weakness-map missing topics field")
        elif len(weakness.get("topics", [])) != 9:
            issues.append(
                f"/weakness-map returned {len(weakness.get('topics', []))} topics, expected 9"
            )

        sample_mc = conn.execute(
            """
            SELECT q.id, ac.id
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            JOIN answer_choices ac ON ac.question_id = q.id AND ac.is_correct = 1
            WHERE c.code = 'MATH20-1' AND q.question_type = 'multiple_choice'
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
            WHERE c.code = 'MATH20-1' AND q.question_type = 'numerical_response'
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
        before = course_count(sqlite3.connect(PROD_DB), "MATH20-1")
        import_questions(db, items)
        after = course_count(sqlite3.connect(PROD_DB), "MATH20-1")
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
        WHERE c.code = 'MATH20-1'
        GROUP BY t.name
        ORDER BY t.sort_order
        """
    ).fetchall()

    type_rows = sqlite3.connect(PROD_DB).execute(
        """
        SELECT q.question_type, COUNT(*)
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'MATH20-1' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY" if not issues else "BLOCKED",
        "backup": str(backup_path),
        "json_source": str(JSON_PATH),
        "import_summary": {
            "math20_1_before": before["math20_1_count"],
            "math20_1_after": after["math20_1_count"],
            "imported_new": after["math20_1_count"] - before["math20_1_count"],
        },
        "data_preservation": {
            "production_ids_preserved": before["existing_question_ids"] == after["existing_question_ids"],
            "preserved_courses": list(PRESERVE_COURSES),
            "user_answers": {"before": before["user_answers"], "after": after["user_answers"]},
            "question_history": {"before": before["question_history"], "after": after["question_history"]},
            "quiz_attempts": {"before": before["quiz_attempts"], "after": after["quiz_attempts"]},
            "topic_performance": {"before": before["topic_performance"], "after": after["topic_performance"]},
            "bio30_count": {"before": before["bio30_count"], "after": after["bio30_count"]},
            "math30_1_count": {"before": before["math30_1_count"], "after": after["math30_1_count"]},
            "chem30_count": {"before": before["chem30_count"], "after": after["chem30_count"]},
            "phys30_count": {"before": before["phys30_count"], "after": after["phys30_count"]},
        },
        "math20_1_counts": {
            "total": after["math20_1_count"],
            "target": MATH20_1_TOTAL,
            "by_topic": {name: count for name, count in topic_rows},
            "topic_targets": MATH20_1_TOPIC_TARGETS,
            "by_type": {name: count for name, count in type_rows},
            "type_targets": {"multiple_choice": MATH20_1_MC, "numerical_response": MATH20_1_NR},
        },
        "api_verification": api_details,
        "issues": issues,
    }


def write_md_report(report: dict) -> None:
    ds = report["data_preservation"]
    mc = report["math20_1_counts"]
    api = report.get("api_verification", {})
    lines = [
        "# Mathematics 20-1 Production Readiness Report",
        "",
        f"**Date (UTC):** {report['timestamp_utc'][:10]}",
        f"**Status:** {report['status']}",
        "**Database:** `backend/albertaprep.db`",
        "",
        "---",
        "",
        "## Import Summary",
        "",
        "| Item | Result |",
        "|------|--------|",
        f"| Source JSON | `{Path(report['json_source']).name}` |",
        f"| Questions imported | **{report['import_summary']['imported_new']}** |",
        f"| MATH20-1 total after import | **{report['import_summary']['math20_1_after']}** |",
        f"| Pre-import backup | `{report['backup']}` |",
        "",
        "---",
        "",
        "## Data Preservation",
        "",
        "| Asset | Before | After | Preserved |",
        "|-------|--------|-------|-----------|",
        f"| BIO30 questions | {ds['bio30_count']['before']} | {ds['bio30_count']['after']} | {'Yes' if ds['bio30_count']['before'] == ds['bio30_count']['after'] else 'No'} |",
        f"| MATH30-1 questions | {ds['math30_1_count']['before']} | {ds['math30_1_count']['after']} | {'Yes' if ds['math30_1_count']['before'] == ds['math30_1_count']['after'] else 'No'} |",
        f"| CHEM30 questions | {ds['chem30_count']['before']} | {ds['chem30_count']['after']} | {'Yes' if ds['chem30_count']['before'] == ds['chem30_count']['after'] else 'No'} |",
        f"| PHYS30 questions | {ds['phys30_count']['before']} | {ds['phys30_count']['after']} | {'Yes' if ds['phys30_count']['before'] == ds['phys30_count']['after'] else 'No'} |",
        f"| User answers | {ds['user_answers']['before']} | {ds['user_answers']['after']} | {'Yes' if ds['user_answers']['before'] == ds['user_answers']['after'] else 'No'} |",
        f"| Question history | {ds['question_history']['before']} | {ds['question_history']['after']} | {'Yes' if ds['question_history']['before'] == ds['question_history']['after'] else 'No'} |",
        f"| Quiz attempts | {ds['quiz_attempts']['before']} | {ds['quiz_attempts']['after']} | {'Yes' if ds['quiz_attempts']['before'] == ds['quiz_attempts']['after'] else 'No'} |",
        f"| Topic performance | {ds['topic_performance']['before']} | {ds['topic_performance']['after']} | {'Yes' if ds['topic_performance']['before'] == ds['topic_performance']['after'] else 'No'} |",
        "",
        f"**Production IDs preserved:** {ds['production_ids_preserved']}",
        "",
        "---",
        "",
        "## Course & Topic Counts",
        "",
        f"### MATH20-1 total: {mc['total']} (target {mc['target']})",
        "",
        "| Topic | Count | Target |",
        "|-------|-------|--------|",
    ]
    for topic, target in MATH20_1_TOPIC_TARGETS.items():
        count = mc["by_topic"].get(topic, 0)
        lines.append(f"| {topic} | {count} | {target} |")

    lines.extend([
        "",
        "### By question type",
        "",
        "| Type | Count | Target |",
        "|------|-------|--------|",
        f"| Multiple Choice | {mc['by_type'].get('multiple_choice', 0)} | {MATH20_1_MC} |",
        f"| Numerical Response | {mc['by_type'].get('numerical_response', 0)} | {MATH20_1_NR} |",
        "",
        "---",
        "",
        "## API Verification",
        "",
    ])
    if api.get("api_available"):
        lines.extend([
            "| Endpoint | Result |",
            "|----------|--------|",
            f"| `GET /courses` | MATH20-1 listed, count={api.get('course_question_count')} |",
            f"| `GET /courses/{{id}}/topics` | {api.get('topic_count')} topics |",
            f"| `GET /quiz/available-count` | {api.get('quiz_available_count')} available |",
            f"| `GET /quiz/questions?count=10` | {api.get('quiz_questions_returned')} returned |",
            f"| `GET /progress` | {api.get('progress_courses')} courses, streak={api.get('progress_has_practice_streak')} |",
            f"| `GET /daily-practice` | {api.get('daily_practice_total')} configured |",
            f"| `POST /daily-practice/start` | {api.get('daily_practice_started')} returned |",
            f"| `GET /weakness-map` | {api.get('weakness_map_topics')} topics |",
            f"| `POST /quiz/guest/grade` (MC) | {api.get('guest_mc_grade')} |",
            f"| `POST /quiz/guest/grade` (NR) | {api.get('guest_nr_grade')} |",
        ])
    else:
        lines.append("API server was unavailable during import verification.")

    if report["issues"]:
        lines.extend(["", "---", "", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- {issue}")

    lines.extend([
        "",
        "---",
        "",
        "## Artifacts",
        "",
        "| File | Purpose |",
        "|------|---------|",
        "| `questions.json/math20-1_questions_final.json` | Production question bank |",
        "| `questions.json/course_questions_final.json` | Alias copy |",
        "| `questions.json/math20-1_production_validation_report.json` | Pre-import JSON validation |",
        "| `questions.json/math20-1_production_readiness_report.json` | Machine-readable import report |",
        "| `backend/scripts/import_math20_1_production.py` | Import + verify script |",
    ])
    MD_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")
    if not JSON_PATH.is_file():
        raise SystemExit(f"JSON bank not found: {JSON_PATH}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    math_items = [i for i in items if i.get("course_code") == "MATH20-1"]
    if len(math_items) != MATH20_1_TOTAL:
        raise SystemExit(f"Expected {MATH20_1_TOTAL} MATH20-1 items, got {len(math_items)}")

    conn = sqlite3.connect(PROD_DB)
    before = snapshot_existing(conn)
    conn.close()

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")
    print(
        f"Before import — BIO30: {before['bio30_count']}, MATH30-1: {before['math30_1_count']}, "
        f"CHEM30: {before['chem30_count']}, PHYS30: {before['phys30_count']}, "
        f"MATH20-1: {before['math20_1_count']}"
    )
    print(
        f"Before import — user_answers: {before['user_answers']}, "
        f"question_history: {before['question_history']}, quiz_attempts: {before['quiz_attempts']}"
    )

    if before["math20_1_count"] == 0:
        print("Importing MATH20-1 production bank...")
        run_import(items)
    elif before["math20_1_count"] == MATH20_1_TOTAL:
        print("MATH20-1 already imported (300 questions). Re-running import for duplicate-skip check only.")
        run_import(items)
        conn = sqlite3.connect(PROD_DB)
        count = course_count(conn, "MATH20-1")
        conn.close()
        if count != MATH20_1_TOTAL:
            raise SystemExit("Duplicate import changed MATH20-1 question count")
        print("Duplicate import check: 0 new rows (all 300 skipped as expected)")
    else:
        raise SystemExit(
            f"Partial MATH20-1 import detected ({before['math20_1_count']} questions). "
            "Restore from backup before retrying."
        )

    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues = []
    issues.extend(verify_existing_ids_preserved(before, after))
    issues.extend(verify_orphans(conn))
    issues.extend(verify_math20_1_counts(conn))
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
    write_md_report(report)

    print("\n=== IMPORT RESULT ===")
    print(f"MATH20-1 count: {before['math20_1_count']} -> {after['math20_1_count']}")
    print(f"BIO30 count: {before['bio30_count']} -> {after['bio30_count']}")
    print(f"MATH30-1 count: {before['math30_1_count']} -> {after['math30_1_count']}")
    print(f"CHEM30 count: {before['chem30_count']} -> {after['chem30_count']}")
    print(f"PHYS30 count: {before['phys30_count']} -> {after['phys30_count']}")
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
        print(f"Markdown report: {MD_REPORT_PATH}")
        return 1

    print("All import and verification checks passed.")
    print(f"Report written: {REPORT_PATH}")
    print(f"Markdown report: {MD_REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
