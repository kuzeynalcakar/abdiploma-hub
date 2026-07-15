"""Database integrity audits for admin / DR checks.

Reports orphaned FKs, missing content links, and broken relationships.
Does not modify data.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def _count(db: Session, sql: str) -> int:
    return int(db.execute(text(sql)).scalar() or 0)


def run_integrity_audit(db: Session) -> dict[str, Any]:
    """Return structured integrity findings (no PII)."""
    checks: list[dict[str, Any]] = []

    orphan_specs = [
        (
            "user_answers_missing_question",
            "User answers whose question was deleted",
            """
            SELECT COUNT(*) FROM user_answers ua
            LEFT JOIN questions q ON ua.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
        (
            "user_answers_missing_attempt",
            "User answers whose quiz attempt was deleted",
            """
            SELECT COUNT(*) FROM user_answers ua
            LEFT JOIN quiz_attempts qa ON ua.quiz_attempt_id = qa.id
            WHERE qa.id IS NULL
            """,
        ),
        (
            "answer_choices_orphan",
            "Answer choices without a question",
            """
            SELECT COUNT(*) FROM answer_choices ac
            LEFT JOIN questions q ON ac.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
        (
            "questions_missing_topic",
            "Questions without a topic",
            """
            SELECT COUNT(*) FROM questions q
            LEFT JOIN topics t ON q.topic_id = t.id
            WHERE t.id IS NULL
            """,
        ),
        (
            "topics_missing_course",
            "Topics without a course",
            """
            SELECT COUNT(*) FROM topics t
            LEFT JOIN courses c ON t.course_id = c.id
            WHERE c.id IS NULL
            """,
        ),
        (
            "quiz_attempts_missing_user",
            "Quiz attempts without a user",
            """
            SELECT COUNT(*) FROM quiz_attempts qa
            LEFT JOIN users u ON qa.user_id = u.id
            WHERE u.id IS NULL
            """,
        ),
        (
            "quiz_attempts_missing_course",
            "Quiz attempts without a course",
            """
            SELECT COUNT(*) FROM quiz_attempts qa
            LEFT JOIN courses c ON qa.course_id = c.id
            WHERE c.id IS NULL
            """,
        ),
        (
            "question_reports_orphan",
            "Reports referencing missing questions",
            """
            SELECT COUNT(*) FROM question_reports r
            LEFT JOIN questions q ON r.question_id = q.id
            WHERE q.id IS NULL
            """,
        ),
        (
            "quiz_feedback_orphan_course",
            "Feedback referencing missing courses",
            """
            SELECT COUNT(*) FROM quiz_feedback f
            LEFT JOIN courses c ON f.course_id = c.id
            WHERE c.id IS NULL
            """,
        ),
        (
            "quiz_attempt_questions_orphan",
            "Daily-practice links with missing question or attempt",
            """
            SELECT COUNT(*) FROM quiz_attempt_questions qaq
            LEFT JOIN quiz_attempts qa ON qaq.quiz_attempt_id = qa.id
            LEFT JOIN questions q ON qaq.question_id = q.id
            WHERE qa.id IS NULL OR q.id IS NULL
            """,
        ),
        (
            "question_history_orphan",
            "Question history rows with missing user or question",
            """
            SELECT COUNT(*) FROM question_history qh
            LEFT JOIN users u ON qh.user_id = u.id
            LEFT JOIN questions q ON qh.question_id = q.id
            WHERE u.id IS NULL OR q.id IS NULL
            """,
        ),
        (
            "sessions_orphan_user",
            "Sessions without a user",
            """
            SELECT COUNT(*) FROM user_sessions s
            LEFT JOIN users u ON s.user_id = u.id
            WHERE u.id IS NULL
            """,
        ),
    ]

    total_issues = 0
    for key, label, sql in orphan_specs:
        try:
            count = _count(db, sql)
        except Exception:
            checks.append(
                {
                    "key": key,
                    "label": label,
                    "count": -1,
                    "ok": False,
                    "detail": "Check failed (table may be missing).",
                }
            )
            total_issues += 1
            continue
        ok = count == 0
        if not ok:
            total_issues += count
        checks.append(
            {
                "key": key,
                "label": label,
                "count": count,
                "ok": ok,
                "detail": None if ok else f"{count} orphaned or broken row(s).",
            }
        )

    # Active courses should have at least some questions (content integrity).
    empty_courses = _count(
        db,
        """
        SELECT COUNT(*) FROM courses c
        WHERE c.is_active = 1
        AND NOT EXISTS (
            SELECT 1 FROM topics t
            JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
            WHERE t.course_id = c.id
        )
        """,
    )
    checks.append(
        {
            "key": "active_courses_without_questions",
            "label": "Active courses with no active questions",
            "count": empty_courses,
            "ok": empty_courses == 0,
            "detail": None
            if empty_courses == 0
            else f"{empty_courses} active course(s) have an empty question bank.",
        }
    )
    if empty_courses:
        total_issues += empty_courses

    # MC questions should have choices.
    mc_missing_choices = _count(
        db,
        """
        SELECT COUNT(*) FROM questions q
        WHERE q.is_active = 1 AND q.question_type = 'multiple_choice'
        AND NOT EXISTS (
            SELECT 1 FROM answer_choices ac WHERE ac.question_id = q.id
        )
        """,
    )
    checks.append(
        {
            "key": "mc_missing_choices",
            "label": "Active multiple-choice questions with no choices",
            "count": mc_missing_choices,
            "ok": mc_missing_choices == 0,
            "detail": None
            if mc_missing_choices == 0
            else f"{mc_missing_choices} MC question(s) missing choices.",
        }
    )
    if mc_missing_choices:
        total_issues += mc_missing_choices

    return {
        "ok": total_issues == 0,
        "issue_count": int(total_issues),
        "checks": checks,
    }

