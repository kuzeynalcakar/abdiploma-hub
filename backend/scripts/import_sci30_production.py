"""Import SCI30 production bank with backup, safety checks, and verification."""

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
JSON_PATH = BACKEND.parent / "questions.json" / "science30_questions_final.json"
JSON_ALIAS = BACKEND.parent / "questions.json" / "course_questions_final.json"
REPORT_JSON = BACKEND.parent / "questions.json" / "sci30_production_readiness_report.json"
REPORT_MD = BACKEND.parent / "questions.json" / "SCI30_PRODUCTION_READINESS_REPORT.md"
BASE_API = "http://127.0.0.1:8000/api/v1"

SCI30_TOPIC_TARGETS = {
    "Circulatory and Immune Systems": 38,
    "Genetics and Molecular Biology": 38,
    "Environmental Chemistry": 75,
    "Field Theory and Electrical Energy": 46,
    "Electromagnetic Spectrum": 29,
    "Energy and the Environment": 74,
}
SCI30_TOTAL = 300
SCI30_MC = 211
SCI30_NR = 89
PRESERVE_COURSES = ("BIO30", "MATH30-1", "CHEM30", "PHYS30", "MATH30-2", "MATH20-1")


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_sci30_import_{stamp}.db"
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
    snap = {
        "existing_question_ids": existing_ids,
        "user_answers": conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0],
        "question_history": conn.execute("SELECT COUNT(*) FROM question_history").fetchone()[0],
        "quiz_attempts": conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0],
        "topic_performance": conn.execute("SELECT COUNT(*) FROM topic_performance").fetchone()[0],
        "sci30_count": course_count(conn, "SCI30"),
    }
    for code in PRESERVE_COURSES:
        snap[f"{code.lower().replace('-', '_')}_count"] = course_count(conn, code)
    return snap


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
    for code in PRESERVE_COURSES:
        key = f"{code.lower().replace('-', '_')}_count"
        if before[key] != after[key]:
            issues.append(f"{code} count changed: {before[key]} -> {after[key]}")
    return issues


def verify_sci30_counts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    total = course_count(conn, "SCI30")
    if total != SCI30_TOTAL:
        issues.append(f"SCI30 total {total} != {SCI30_TOTAL}")

    rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'SCI30'
        GROUP BY t.name
        ORDER BY t.name
        """
    ).fetchall()
    for name, count in rows:
        if count == 0:
            continue
        expected = SCI30_TOPIC_TARGETS.get(name)
        if expected is None:
            issues.append(f"Unexpected SCI30 topic with questions: {name} ({count})")
        elif count != expected:
            issues.append(f"Topic {name}: {count} != expected {expected}")

    dupes = conn.execute(
        """
        SELECT q.question_text, COUNT(*) n
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'SCI30' AND q.is_active = 1
        GROUP BY q.question_text
        HAVING n > 1
        """
    ).fetchall()
    if dupes:
        issues.append(f"{len(dupes)} duplicate SCI30 stems in DB")

    type_rows = conn.execute(
        """
        SELECT q.question_type, COUNT(*)
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'SCI30' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()
    type_counts = dict(type_rows)
    if type_counts.get("multiple_choice", 0) != SCI30_MC:
        issues.append(
            f"SCI30 MC count {type_counts.get('multiple_choice', 0)} != {SCI30_MC}"
        )
    if type_counts.get("numerical_response", 0) != SCI30_NR:
        issues.append(
            f"SCI30 NR count {type_counts.get('numerical_response', 0)} != {SCI30_NR}"
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
        email = f"sci30.import.{random.randint(100000, 999999)}@example.com"
        token = api_request(
            "/auth/register",
            method="POST",
            data={"name": "SCI30 Import Verify", "email": email, "password": "testpass123"},
        )["access_token"]

        courses = api_request("/courses", token=token)["courses"]
        sci = next((c for c in courses if c["code"] == "SCI30"), None)
        details["courses_listed"] = sci is not None
        if sci is None:
            issues.append("SCI30 not listed in /courses")
            return issues, details

        details["course_question_count"] = sci.get("question_count", 0)
        if sci.get("question_count", 0) < SCI30_TOTAL:
            issues.append(
                f"/courses SCI30 question_count {sci.get('question_count')} < {SCI30_TOTAL}"
            )

        topics = api_request(f"/courses/{sci['id']}/topics", token=token)["topics"]
        details["topic_count"] = len(topics)
        if len(topics) != 6:
            issues.append(f"/courses/{{id}}/topics returned {len(topics)} topics, expected 6")

        available = api_request(
            f"/quiz/available-count?course_id={sci['id']}", token=token
        )
        details["quiz_available_count"] = available.get("available_count", 0)
        if available.get("available_count", 0) < 10:
            issues.append(f"/quiz/available-count too low: {available.get('available_count')}")

        quiz = api_request(
            f"/quiz/questions?course_id={sci['id']}&count=10", token=token
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

        daily = api_request(f"/daily-practice?course_id={sci['id']}", token=token)
        for field in ("is_completed", "is_started", "total_questions", "topics_included"):
            if field not in daily:
                issues.append(f"/daily-practice missing {field}")
        details["daily_practice_total"] = daily.get("total_questions")

        daily_start = api_request(
            f"/daily-practice/start?course_id={sci['id']}",
            method="POST",
            token=token,
        )
        details["daily_practice_started"] = len(daily_start.get("questions", []))
        if not daily_start.get("questions"):
            issues.append("/daily-practice/start returned no questions")

        weakness = api_request(f"/weakness-map?course_id={sci['id']}", token=token)
        details["weakness_map_topics"] = len(weakness.get("topics", []))
        if "topics" not in weakness:
            issues.append("/weakness-map missing topics field")
        elif len(weakness.get("topics", [])) != 6:
            issues.append(
                f"/weakness-map returned {len(weakness.get('topics', []))} topics, expected 6"
            )

        sample_mc = conn.execute(
            """
            SELECT q.id, ac.id
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            JOIN answer_choices ac ON ac.question_id = q.id AND ac.is_correct = 1
            WHERE c.code = 'SCI30' AND q.question_type = 'multiple_choice'
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
            WHERE c.code = 'SCI30' AND q.question_type = 'numerical_response'
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


def run_import(items: list[dict]) -> None:
    db = SessionLocal()
    try:
        seed_curriculum(db)
        import_questions(db, items)
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
        WHERE c.code = 'SCI30'
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
        WHERE c.code = 'SCI30' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY" if not issues else "BLOCKED",
        "backup": str(backup_path),
        "json_source": str(JSON_PATH),
        "import_summary": {
            "sci30_before": before["sci30_count"],
            "sci30_after": after["sci30_count"],
            "imported_new": after["sci30_count"] - before["sci30_count"],
        },
        "data_preservation": {
            "production_ids_preserved": before["existing_question_ids"] == after["existing_question_ids"],
            "preserved_courses": list(PRESERVE_COURSES),
            "user_answers": {"before": before["user_answers"], "after": after["user_answers"]},
            "question_history": {"before": before["question_history"], "after": after["question_history"]},
            "quiz_attempts": {"before": before["quiz_attempts"], "after": after["quiz_attempts"]},
            "topic_performance": {"before": before["topic_performance"], "after": after["topic_performance"]},
            "course_counts": {
                code: {
                    "before": before[f"{code.lower().replace('-', '_')}_count"],
                    "after": after[f"{code.lower().replace('-', '_')}_count"],
                }
                for code in PRESERVE_COURSES
            },
        },
        "sci30_counts": {
            "total": after["sci30_count"],
            "target": SCI30_TOTAL,
            "by_topic": {name: count for name, count in topic_rows},
            "topic_targets": SCI30_TOPIC_TARGETS,
            "by_type": dict(type_rows),
            "type_targets": {"multiple_choice": SCI30_MC, "numerical_response": SCI30_NR},
        },
        "api_verification": api_details,
        "issues": issues,
    }


def write_markdown_report(report: dict) -> None:
    status = report["status"]
    lines = [
        "# Science 30 Production Readiness Report",
        "",
        f"**Date (UTC):** {report['timestamp_utc'][:10]}",
        f"**Status:** {status}",
        "**Database:** `backend/albertaprep.db`",
        "",
        "---",
        "",
        "## Import Summary",
        "",
        "| Item | Result |",
        "|------|--------|",
        f"| Source JSON | `{report['json_source']}` |",
        f"| Questions imported | **{report['import_summary']['imported_new']}** new (total **{report['import_summary']['sci30_after']}**) |",
        f"| Pre-import backup | `{report['backup']}` |",
        "",
        "---",
        "",
        "## Data Preservation",
        "",
        "| Asset | Before | After | Preserved |",
        "|-------|--------|-------|-----------|",
    ]

    dp = report["data_preservation"]
    lines.append(
        f"| User answers | {dp['user_answers']['before']} | {dp['user_answers']['after']} | "
        f"{'Yes' if dp['user_answers']['before'] == dp['user_answers']['after'] else 'No'} |"
    )
    lines.append(
        f"| Question history | {dp['question_history']['before']} | {dp['question_history']['after']} | "
        f"{'Yes' if dp['question_history']['before'] == dp['question_history']['after'] else 'No'} |"
    )
    lines.append(
        f"| Quiz attempts | {dp['quiz_attempts']['before']} | {dp['quiz_attempts']['after']} | "
        f"{'Yes' if dp['quiz_attempts']['before'] == dp['quiz_attempts']['after'] else 'No'} |"
    )
    lines.append(
        f"| Topic performance | {dp['topic_performance']['before']} | {dp['topic_performance']['after']} | "
        f"{'Yes' if dp['topic_performance']['before'] == dp['topic_performance']['after'] else 'No'} |"
    )
    lines.append(
        f"| Production IDs preserved | — | — | "
        f"{'Yes' if dp['production_ids_preserved'] else 'No'} |"
    )

    for code, counts in dp["course_counts"].items():
        lines.append(
            f"| {code} questions | {counts['before']} | {counts['after']} | "
            f"{'Yes' if counts['before'] == counts['after'] else 'No'} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## Science 30 Course & Topic Counts",
        "",
        f"**Total:** {report['sci30_counts']['total']} / {report['sci30_counts']['target']}",
        "",
        "| Topic | Count | Target |",
        "|-------|-------|--------|",
    ])
    for topic, target in report["sci30_counts"]["topic_targets"].items():
        count = report["sci30_counts"]["by_topic"].get(topic, 0)
        lines.append(f"| {topic} | {count} | {target} |")

    lines.extend([
        "",
        "### Question types",
        "",
        "| Type | Count | Target |",
        "|------|-------|--------|",
    ])
    for qtype, target in report["sci30_counts"]["type_targets"].items():
        count = report["sci30_counts"]["by_type"].get(qtype, 0)
        lines.append(f"| {qtype} | {count} | {target} |")

    api = report.get("api_verification", {})
    lines.extend([
        "",
        "---",
        "",
        "## API Verification",
        "",
        f"| Endpoint | Result |",
        "|----------|--------|",
        f"| Server available | {api.get('api_available', False)} |",
        f"| GET /courses (SCI30 listed) | {api.get('courses_listed', 'N/A')} |",
        f"| Course question_count | {api.get('course_question_count', 'N/A')} |",
        f"| GET /courses/{{id}}/topics | {api.get('topic_count', 'N/A')} topics |",
        f"| GET /quiz/available-count | {api.get('quiz_available_count', 'N/A')} |",
        f"| GET /quiz/questions (10) | {api.get('quiz_questions_returned', 'N/A')} returned |",
        f"| GET /progress | {api.get('progress_courses', 'N/A')} courses |",
        f"| GET /daily-practice | {api.get('daily_practice_total', 'N/A')} questions |",
        f"| POST /daily-practice/start | {api.get('daily_practice_started', 'N/A')} questions |",
        f"| GET /weakness-map | {api.get('weakness_map_topics', 'N/A')} topics |",
        f"| POST /quiz/guest/grade (MC) | {api.get('guest_mc_grade', 'N/A')} |",
        f"| POST /quiz/guest/grade (NR) | {api.get('guest_nr_grade', 'N/A')} |",
    ])

    if report["issues"]:
        lines.extend(["", "---", "", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.extend([
            "",
            "---",
            "",
            "## Verdict",
            "",
            "**Science 30 is production-ready.** All 300 questions imported, existing user data preserved, "
            "duplicate imports blocked, and API surfaces operational for quiz generation, dashboard, "
            "daily practice, and weakness mapping.",
        ])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")
    if not JSON_PATH.is_file():
        if JSON_ALIAS.is_file():
            shutil.copy2(JSON_ALIAS, JSON_PATH)
        else:
            raise SystemExit(f"JSON bank not found: {JSON_PATH}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    sci_items = [i for i in items if i.get("course_code") == "SCI30"]
    if len(sci_items) != SCI30_TOTAL:
        raise SystemExit(f"Expected {SCI30_TOTAL} SCI30 items, got {len(sci_items)}")

    conn = sqlite3.connect(PROD_DB)
    before = snapshot_existing(conn)
    conn.close()

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")
    print(f"Before import — SCI30: {before['sci30_count']}")
    for code in PRESERVE_COURSES:
        key = f"{code.lower().replace('-', '_')}_count"
        print(f"  {code}: {before[key]}")
    print(
        f"Before import — user_answers: {before['user_answers']}, "
        f"question_history: {before['question_history']}, quiz_attempts: {before['quiz_attempts']}"
    )

    if before["sci30_count"] == 0:
        print("Importing SCI30 production bank...")
        run_import(items)
    elif before["sci30_count"] == SCI30_TOTAL:
        print("SCI30 already imported (300 questions). Re-running import for duplicate-skip check only.")
        run_import(items)
        conn = sqlite3.connect(PROD_DB)
        count = course_count(conn, "SCI30")
        conn.close()
        if count != SCI30_TOTAL:
            raise SystemExit("Duplicate import changed SCI30 question count")
        print("Duplicate import check: 0 new rows (all 300 skipped as expected)")
    else:
        raise SystemExit(
            f"Partial SCI30 import detected ({before['sci30_count']} questions). "
            "Restore from backup before retrying."
        )

    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues = []
    issues.extend(verify_existing_ids_preserved(before, after))
    issues.extend(verify_orphans(conn))
    issues.extend(verify_sci30_counts(conn))
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
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown_report(report)

    print("\n=== IMPORT RESULT ===")
    print(f"SCI30 count: {before['sci30_count']} -> {after['sci30_count']}")
    for code in PRESERVE_COURSES:
        key = f"{code.lower().replace('-', '_')}_count"
        print(f"{code} count: {before[key]} -> {after[key]}")
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
        print(f"\nReport written: {REPORT_MD}")
        return 1

    print("All import and verification checks passed.")
    print(f"Report written: {REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
