"""Import SOC30-1 production bank with backup, safety checks, and verification."""

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
JSON_PATH = BACKEND.parent / "questions.json" / "soc30-1_questions_final.json"
JSON_ALIAS = BACKEND.parent / "questions.json" / "course_questions_final.json"
REPORT_PATH = BACKEND.parent / "questions.json" / "soc30-1_production_readiness_report.json"
MD_REPORT_PATH = BACKEND.parent / "questions.json" / "SOC30-1_PRODUCTION_READINESS_REPORT.md"
BASE_API = "http://127.0.0.1:8000/api/v1"

SOC30_1_TOPIC_TARGETS = {
    "Ideology and Identity": 48,
    "Origins of Liberalism": 50,
    "Resistance to Liberalism": 70,
    "The Viability of Contemporary Liberalism": 92,
    "Citizenship and Ideology": 40,
}
SOC30_1_TOTAL = 300
SOC30_1_MC = 277
SOC30_1_NR = 23
SOC30_1_TOPIC_COUNT = 5

PRESERVE_COURSES = (
    "BIO30",
    "MATH30-1",
    "MATH20-1",
    "MATH30-2",
    "CHEM30",
    "PHYS30",
    "SCI10",
    "SCI30",
)


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_soc30_1_import_{stamp}.db"
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
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "soc30_1_count": course_count(conn, "SOC30-1"),
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
    for field in (
        "user_answers",
        "question_history",
        "quiz_attempts",
        "topic_performance",
        "users",
    ):
        if before[field] != after[field]:
            issues.append(f"{field} changed: {before[field]} -> {after[field]}")
    for code in PRESERVE_COURSES:
        key = f"{code.lower().replace('-', '_')}_count"
        if before[key] != after[key]:
            issues.append(f"{code} count changed: {before[key]} -> {after[key]}")
    return issues


def verify_soc30_1_counts(conn: sqlite3.Connection) -> list[str]:
    issues = []
    total = course_count(conn, "SOC30-1")
    if total != SOC30_1_TOTAL:
        issues.append(f"SOC30-1 total {total} != {SOC30_1_TOTAL}")

    rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'SOC30-1'
        GROUP BY t.name
        ORDER BY t.sort_order, t.name
        """
    ).fetchall()
    for name, count in rows:
        if count == 0:
            continue
        expected = SOC30_1_TOPIC_TARGETS.get(name)
        if expected is None:
            issues.append(f"Unexpected SOC30-1 topic with questions: {name} ({count})")
        elif count != expected:
            issues.append(f"Topic {name}: {count} != expected {expected}")

    missing_topics = [
        name
        for name, expected in SOC30_1_TOPIC_TARGETS.items()
        if not any(row[0] == name and row[1] == expected for row in rows)
    ]
    for name in missing_topics:
        actual = next((c for n, c in rows if n == name), 0)
        if actual != SOC30_1_TOPIC_TARGETS[name]:
            issues.append(
                f"Topic {name}: {actual} != expected {SOC30_1_TOPIC_TARGETS[name]}"
            )

    dupes = conn.execute(
        """
        SELECT q.question_text, COUNT(*) n
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'SOC30-1' AND q.is_active = 1
        GROUP BY q.question_text
        HAVING n > 1
        """
    ).fetchall()
    if dupes:
        issues.append(f"{len(dupes)} duplicate SOC30-1 stems in DB")

    type_rows = dict(
        conn.execute(
            """
            SELECT q.question_type, COUNT(*)
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = 'SOC30-1' AND q.is_active = 1
            GROUP BY q.question_type
            """
        ).fetchall()
    )
    if type_rows.get("multiple_choice", 0) != SOC30_1_MC:
        issues.append(
            f"MC count {type_rows.get('multiple_choice', 0)} != {SOC30_1_MC}"
        )
    if type_rows.get("numerical_response", 0) != SOC30_1_NR:
        issues.append(
            f"NR count {type_rows.get('numerical_response', 0)} != {SOC30_1_NR}"
        )

    return issues


class _ApiClient:
    """urllib client with optional bearer token + cookie jar (guest quiz)."""

    def __init__(self, token: str | None = None):
        import http.cookiejar

        self.token = token
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        data: dict | None = None,
        use_token: bool = True,
    ):
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if use_token and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(
            BASE_API + path, data=body, headers=headers, method=method
        )
        with self.opener.open(req, timeout=20) as resp:
            return json.loads(resp.read())


def api_request(path: str, *, method: str = "GET", data: dict | None = None, token: str | None = None):
    return _ApiClient(token).request(path, method=method, data=data)


def verify_api_endpoints(conn: sqlite3.Connection) -> tuple[list[str], dict]:
    issues: list[str] = []
    details: dict = {"api_available": False}

    try:
        email = f"soc30.import.{random.randint(100000, 999999)}@example.com"
        client = _ApiClient()
        token = client.request(
            "/auth/register",
            method="POST",
            data={
                "name": "SOC30-1 Import Verify",
                "email": email,
                "password": "testpass123",
            },
            use_token=False,
        )["token"]
        client.token = token
        details["api_available"] = True

        courses = client.request("/courses")["courses"]
        soc = next((c for c in courses if c["code"] == "SOC30-1"), None)
        if soc is None:
            issues.append("SOC30-1 not listed in /courses")
            return issues, details

        details["course_question_count"] = soc.get("question_count", 0)
        if soc.get("question_count", 0) < SOC30_1_TOTAL:
            issues.append(
                f"/courses SOC30-1 question_count {soc.get('question_count')} < {SOC30_1_TOTAL}"
            )

        topics = client.request(f"/courses/{soc['id']}/topics")["topics"]
        details["topic_count"] = len(topics)
        if len(topics) != SOC30_1_TOPIC_COUNT:
            issues.append(
                f"/courses/{{id}}/topics returned {len(topics)} topics, expected {SOC30_1_TOPIC_COUNT}"
            )

        listed_nonzero = [c for c in courses if (c.get("question_count") or 0) > 0]
        details["dashboard_courses_with_questions"] = len(listed_nonzero)
        if not any(c["code"] == "SOC30-1" for c in listed_nonzero):
            issues.append("SOC30-1 missing from dashboard course list with questions")

        try:
            available = client.request(f"/quiz/available-count?course_id={soc['id']}")
            details["quiz_available_count"] = available.get("available_count", 0)
            if available.get("available_count", 0) < 10:
                issues.append(
                    f"/quiz/available-count too low: {available.get('available_count')}"
                )
        except Exception as exc:
            issues.append(f"/quiz/available-count failed: {exc}")

        try:
            quiz = client.request(f"/quiz/questions?course_id={soc['id']}&count=10")
            details["quiz_questions_returned"] = len(quiz.get("questions", []))
            if len(quiz.get("questions", [])) < 10:
                issues.append(
                    f"/quiz/questions returned {len(quiz.get('questions', []))} questions"
                )
        except Exception as exc:
            issues.append(f"/quiz/questions failed: {exc}")

        try:
            progress = client.request("/progress")
            details["progress_courses"] = len(progress.get("courses", []))
            details["progress_has_practice_streak"] = "practice_streak" in progress
            if "courses" not in progress:
                issues.append("/progress missing courses field")
            if "practice_streak" not in progress:
                issues.append("/progress missing practice_streak field")
        except Exception as exc:
            issues.append(f"/progress failed: {exc}")

        try:
            daily = client.request(f"/daily-practice?course_id={soc['id']}")
            details["daily_practice_total"] = daily.get("total_questions")
            for field in ("is_completed", "is_started", "total_questions", "topics_included"):
                if field not in daily:
                    issues.append(f"/daily-practice missing {field}")
        except Exception as exc:
            issues.append(f"/daily-practice failed: {exc}")

        try:
            daily_start = client.request(
                f"/daily-practice/start?course_id={soc['id']}",
                method="POST",
            )
            details["daily_practice_started"] = len(daily_start.get("questions", []))
            if not daily_start.get("questions"):
                issues.append("/daily-practice/start returned no questions")
        except Exception as exc:
            issues.append(f"/daily-practice/start failed: {exc}")

        try:
            weakness = client.request(f"/weakness-map?course_id={soc['id']}")
            details["weakness_map_topics"] = len(weakness.get("topics", []))
            if "topics" not in weakness:
                issues.append("/weakness-map missing topics field")
            elif len(weakness.get("topics", [])) != SOC30_1_TOPIC_COUNT:
                issues.append(
                    f"/weakness-map returned {len(weakness.get('topics', []))} topics, "
                    f"expected {SOC30_1_TOPIC_COUNT}"
                )
        except Exception as exc:
            issues.append(f"/weakness-map failed: {exc}")

        # Guest grade requires cookie from /quiz/guest/questions
        try:
            details["guest_mc_grade"] = None
            details["guest_nr_grade"] = None
            for attempt in range(8):
                guest = _ApiClient()
                guest_quiz = guest.request(
                    f"/quiz/guest/questions?course_id={soc['id']}&count=50",
                    use_token=False,
                )
                guest_qs = guest_quiz.get("questions", [])
                details["guest_questions_returned"] = len(guest_qs)
                if not guest_qs:
                    continue
                guest_ids = {q["id"] for q in guest_qs}

                if details["guest_mc_grade"] is None:
                    sample_mc = conn.execute(
                        """
                        SELECT q.id, ac.id
                        FROM questions q
                        JOIN answer_choices ac
                          ON ac.question_id = q.id AND ac.is_correct = 1
                        WHERE q.id IN (%s) AND q.question_type = 'multiple_choice'
                        LIMIT 1
                        """
                        % ",".join("?" for _ in guest_ids),
                        tuple(guest_ids),
                    ).fetchone()
                    if sample_mc:
                        grade = guest.request(
                            "/quiz/guest/grade",
                            method="POST",
                            data={
                                "question_id": sample_mc[0],
                                "answer_choice_id": sample_mc[1],
                            },
                            use_token=False,
                        )
                        details["guest_mc_grade"] = bool(grade.get("is_correct"))
                        if not grade.get("is_correct"):
                            issues.append(f"Guest grade failed for MC Q{sample_mc[0]}")

                if details["guest_nr_grade"] is None:
                    sample_nr = conn.execute(
                        """
                        SELECT q.id, q.answer FROM questions q
                        WHERE q.id IN (%s) AND q.question_type = 'numerical_response'
                        LIMIT 1
                        """
                        % ",".join("?" for _ in guest_ids),
                        tuple(guest_ids),
                    ).fetchone()
                    if sample_nr:
                        grade = guest.request(
                            "/quiz/guest/grade",
                            method="POST",
                            data={
                                "question_id": sample_nr[0],
                                "response_text": str(sample_nr[1]),
                            },
                            use_token=False,
                        )
                        details["guest_nr_grade"] = bool(grade.get("is_correct"))
                        if not grade.get("is_correct"):
                            issues.append(f"Guest grade failed for NR Q{sample_nr[0]}")

                if details["guest_mc_grade"] is not None and details["guest_nr_grade"] is not None:
                    break

            if details["guest_mc_grade"] is None:
                issues.append("Guest MC grade not verified (no MC sampled in guest sets)")
            if details["guest_nr_grade"] is None:
                issues.append("Guest NR grade not verified (no NR sampled in guest sets)")
        except Exception as exc:
            issues.append(f"Guest quiz/grade failed: {exc}")
            details["guest_mc_grade"] = details.get("guest_mc_grade", False)
            details["guest_nr_grade"] = details.get("guest_nr_grade", False)

    except urllib.error.URLError as exc:
        issues.append(f"API verification skipped (server unavailable): {exc}")
        details["api_available"] = False
    except Exception as exc:
        issues.append(f"API verification error: {exc}")
        details["api_available"] = False

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
    conn = sqlite3.connect(PROD_DB)
    topic_rows = conn.execute(
        """
        SELECT t.name, COUNT(q.id)
        FROM topics t
        JOIN courses c ON t.course_id = c.id
        LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
        WHERE c.code = 'SOC30-1'
        GROUP BY t.name
        ORDER BY t.sort_order, t.name
        """
    ).fetchall()
    type_rows = conn.execute(
        """
        SELECT q.question_type, COUNT(*)
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'SOC30-1' AND q.is_active = 1
        GROUP BY q.question_type
        """
    ).fetchall()
    conn.close()

    preserved = {
        code: {
            "before": before[f"{code.lower().replace('-', '_')}_count"],
            "after": after[f"{code.lower().replace('-', '_')}_count"],
        }
        for code in PRESERVE_COURSES
    }

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY" if not issues else "BLOCKED",
        "backup": str(backup_path),
        "json_source": str(JSON_PATH),
        "import_summary": {
            "soc30_1_before": before["soc30_1_count"],
            "soc30_1_after": after["soc30_1_count"],
            "imported_new": after["soc30_1_count"] - before["soc30_1_count"],
        },
        "data_preservation": {
            "production_ids_preserved": before["existing_question_ids"]
            == after["existing_question_ids"],
            "preserved_courses": list(PRESERVE_COURSES),
            "users": {"before": before["users"], "after": after["users"]},
            "user_answers": {
                "before": before["user_answers"],
                "after": after["user_answers"],
            },
            "question_history": {
                "before": before["question_history"],
                "after": after["question_history"],
            },
            "quiz_attempts": {
                "before": before["quiz_attempts"],
                "after": after["quiz_attempts"],
            },
            "topic_performance": {
                "before": before["topic_performance"],
                "after": after["topic_performance"],
            },
            "course_counts": preserved,
        },
        "soc30_1_counts": {
            "total": after["soc30_1_count"],
            "target": SOC30_1_TOTAL,
            "by_topic": {name: count for name, count in topic_rows},
            "topic_targets": SOC30_1_TOPIC_TARGETS,
            "by_type": {name: count for name, count in type_rows},
            "type_targets": {
                "multiple_choice": SOC30_1_MC,
                "numerical_response": SOC30_1_NR,
            },
        },
        "api_verification": api_details,
        "issues": issues,
    }


def write_md_report(report: dict) -> None:
    ds = report["data_preservation"]
    sc = report["soc30_1_counts"]
    api = report.get("api_verification", {})
    lines = [
        "# Social Studies 30-1 Production Readiness Report",
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
        f"| SOC30-1 total after import | **{report['import_summary']['soc30_1_after']}** |",
        f"| Pre-import backup | `{report['backup']}` |",
        "",
        "---",
        "",
        "## Data Preservation",
        "",
        "| Asset | Before | After | Preserved |",
        "|-------|--------|-------|-----------|",
    ]
    for code in PRESERVE_COURSES:
        pair = ds["course_counts"][code]
        ok = "Yes" if pair["before"] == pair["after"] else "No"
        lines.append(f"| {code} questions | {pair['before']} | {pair['after']} | {ok} |")
    for label, key in (
        ("Users", "users"),
        ("User answers", "user_answers"),
        ("Question history", "question_history"),
        ("Quiz attempts", "quiz_attempts"),
        ("Topic performance", "topic_performance"),
    ):
        pair = ds[key]
        ok = "Yes" if pair["before"] == pair["after"] else "No"
        lines.append(f"| {label} | {pair['before']} | {pair['after']} | {ok} |")

    lines.extend(
        [
            "",
            f"**Production IDs preserved:** {ds['production_ids_preserved']}",
            "",
            "---",
            "",
            "## Course & Topic Counts",
            "",
            f"### SOC30-1 total: {sc['total']} (target {sc['target']})",
            "",
            "| Topic | Count | Target |",
            "|-------|-------|--------|",
        ]
    )
    for topic, target in SOC30_1_TOPIC_TARGETS.items():
        count = sc["by_topic"].get(topic, 0)
        lines.append(f"| {topic} | {count} | {target} |")

    lines.extend(
        [
            "",
            "### By question type",
            "",
            "| Type | Count | Target |",
            "|------|-------|--------|",
            f"| Multiple Choice | {sc['by_type'].get('multiple_choice', 0)} | {SOC30_1_MC} |",
            f"| Numerical Response | {sc['by_type'].get('numerical_response', 0)} | {SOC30_1_NR} |",
            "",
            "---",
            "",
            "## API Verification",
            "",
        ]
    )
    if api.get("api_available"):
        lines.extend(
            [
                "| Endpoint | Result |",
                "|----------|--------|",
                f"| `GET /courses` (dashboard counts) | SOC30-1 listed, count={api.get('course_question_count')}; courses_with_questions={api.get('dashboard_courses_with_questions')} |",
                f"| `GET /courses/{{id}}/topics` | {api.get('topic_count')} topics |",
                f"| `GET /quiz/available-count` | {api.get('quiz_available_count')} available |",
                f"| `GET /quiz/questions?count=10` | {api.get('quiz_questions_returned')} returned |",
                f"| `GET /progress` | {api.get('progress_courses')} courses, streak={api.get('progress_has_practice_streak')} |",
                f"| `GET /daily-practice` | {api.get('daily_practice_total')} configured |",
                f"| `POST /daily-practice/start` | {api.get('daily_practice_started')} returned |",
                f"| `GET /weakness-map` | {api.get('weakness_map_topics')} topics |",
                f"| `POST /quiz/guest/grade` (MC) | {api.get('guest_mc_grade')} |",
                f"| `POST /quiz/guest/grade` (NR) | {api.get('guest_nr_grade')} |",
            ]
        )
    else:
        lines.append("API server was unavailable during import verification.")

    if report["issues"]:
        lines.extend(["", "---", "", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- {issue}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Artifacts",
            "",
            "| File | Purpose |",
            "|------|---------|",
            "| `questions.json/soc30-1_questions_final.json` | Production question bank |",
            "| `questions.json/course_questions_final.json` | Alias copy |",
            "| `questions.json/SOC30-1_PRODUCTION_VALIDATION.md` | Pre-import JSON validation |",
            "| `questions.json/soc30-1_production_readiness_report.json` | Machine-readable import report |",
            "| `questions.json/SOC30-1_PRODUCTION_READINESS_REPORT.md` | This report |",
            "| `backend/scripts/import_soc30_1_production.py` | Import + verify script |",
            "",
        ]
    )
    MD_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PROD_DB.exists():
        raise SystemExit(f"Production DB not found: {PROD_DB}")
    if not JSON_PATH.is_file():
        raise SystemExit(f"JSON bank not found: {JSON_PATH}")

    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    soc_items = [i for i in items if i.get("course_code") == "SOC30-1"]
    if len(soc_items) != SOC30_1_TOTAL:
        raise SystemExit(f"Expected {SOC30_1_TOTAL} SOC30-1 items, got {len(soc_items)}")

    # Keep alias aligned with the imported bank
    if JSON_ALIAS.is_file():
        alias_items = json.loads(JSON_ALIAS.read_text(encoding="utf-8"))
        if alias_items != items:
            JSON_ALIAS.write_text(
                json.dumps(items, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print("Synced course_questions_final.json to soc30-1_questions_final.json")

    conn = sqlite3.connect(PROD_DB)
    before = snapshot_existing(conn)
    conn.close()

    backup_path = backup_db()
    print(f"Backup created: {backup_path}")
    print(
        f"Before import — SOC30-1: {before['soc30_1_count']}, "
        f"users: {before['users']}, user_answers: {before['user_answers']}, "
        f"question_history: {before['question_history']}, quiz_attempts: {before['quiz_attempts']}"
    )

    if before["soc30_1_count"] == 0:
        print("Importing SOC30-1 production bank...")
        run_import(items)
    elif before["soc30_1_count"] == SOC30_1_TOTAL:
        print(
            "SOC30-1 already imported (300 questions). "
            "Re-running import for duplicate-skip check only."
        )
        run_import(items)
        conn = sqlite3.connect(PROD_DB)
        after_count = course_count(conn, "SOC30-1")
        conn.close()
        if after_count != SOC30_1_TOTAL:
            raise SystemExit("Duplicate import changed SOC30-1 question count")
        print("Duplicate import check: 0 new rows (all 300 skipped as expected)")
    else:
        raise SystemExit(
            f"Partial SOC30-1 import detected ({before['soc30_1_count']} questions). "
            "Restore from backup before retrying."
        )

    conn = sqlite3.connect(PROD_DB)
    after = snapshot_existing(conn)
    issues: list[str] = []
    issues.extend(verify_existing_ids_preserved(before, after))
    issues.extend(verify_orphans(conn))
    issues.extend(verify_soc30_1_counts(conn))
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
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_md_report(report)

    print("\n=== IMPORT RESULT ===")
    print(f"SOC30-1 count: {before['soc30_1_count']} -> {after['soc30_1_count']}")
    for code in PRESERVE_COURSES:
        key = f"{code.lower().replace('-', '_')}_count"
        print(f"{code}: {before[key]} -> {after[key]}")
    print(f"users: {before['users']} -> {after['users']}")
    print(f"user_answers: {before['user_answers']} -> {after['user_answers']}")
    print(f"question_history: {before['question_history']} -> {after['question_history']}")
    print(f"quiz_attempts: {before['quiz_attempts']} -> {after['quiz_attempts']}")
    print(
        "Existing production IDs preserved: "
        f"{before['existing_question_ids'] == after['existing_question_ids']}"
    )
    print(f"\nReports: {MD_REPORT_PATH}")
    print(f"          {REPORT_PATH}")

    print("\n=== VALIDATION ===")
    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        return 1

    print("All import and verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
