"""Aggregate real database metrics for the admin dashboard."""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import String, case, func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models import (
    Course,
    Question,
    QuestionReport,
    QuizAttempt,
    QuizFeedback,
    Topic,
    TopicPerformance,
    User,
    UserAnswer,
)
from app.services.mastery import MASTERED_LEVELS, WEAK_LEVELS, mastery_level_for

VALID_REPORT_REASONS = (
    "incorrect_answer",
    "confusing_wording",
    "wrong_explanation",
    "other",
)


def _mask_email(email: str | None) -> str:
    if not email or "@" not in email:
        return "—"
    local, _, domain = email.partition("@")
    if not local:
        return f"***@{domain}"
    return f"{local[0]}***@{domain}"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


_STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "for",
    "is",
    "it",
    "was",
    "were",
    "be",
    "this",
    "that",
    "with",
    "as",
    "at",
    "by",
    "from",
    "i",
    "my",
    "me",
    "we",
    "you",
    "your",
    "not",
    "no",
    "yes",
    "very",
    "so",
    "too",
    "just",
    "can",
    "could",
    "would",
    "should",
    "have",
    "has",
    "had",
    "do",
    "did",
    "does",
    "are",
    "been",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _active_users_since(db: Session, since: datetime) -> int:
    attempt_users = {
        row[0]
        for row in db.query(QuizAttempt.user_id)
        .filter(QuizAttempt.started_at >= since)
        .distinct()
        .all()
    }
    new_users = {
        row[0]
        for row in db.query(User.id).filter(User.created_at >= since).all()
    }
    return len(attempt_users | new_users)


def _average_accuracy(db: Session) -> float | None:
    graded = (
        db.query(func.count(UserAnswer.id))
        .filter(UserAnswer.is_correct.isnot(None))
        .scalar()
        or 0
    )
    if graded == 0:
        return None
    correct = (
        db.query(func.count(UserAnswer.id))
        .filter(UserAnswer.is_correct.is_(True))
        .scalar()
        or 0
    )
    return round(100.0 * correct / graded, 1)


def _db_file_size() -> tuple[int | None, str | None]:
    url = settings.database_url
    if not url.startswith("sqlite:///"):
        return None, "Size available for SQLite only"
    path = Path(url.removeprefix("sqlite:///"))
    if not path.exists():
        return None, "Database file not found"
    size = path.stat().st_size
    if size < 1024:
        label = f"{size} B"
    elif size < 1024 * 1024:
        label = f"{size / 1024:.1f} KB"
    else:
        label = f"{size / (1024 * 1024):.2f} MB"
    return size, label


def compute_overview(db: Session) -> dict:
    now = _utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    registered_users = db.query(func.count(User.id)).scalar() or 0
    quiz_attempts = db.query(func.count(QuizAttempt.id)).scalar() or 0
    questions_answered = db.query(func.count(UserAnswer.id)).scalar() or 0
    daily_practice_sessions = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.mode == "daily_practice")
        .scalar()
        or 0
    )
    courses_available = (
        db.query(func.count(Course.id)).filter(Course.is_active.is_(True)).scalar()
        or 0
    )
    total_questions = (
        db.query(func.count(Question.id))
        .filter(Question.is_active.is_(True))
        .scalar()
        or 0
    )

    streak_avg = db.query(func.avg(User.practice_streak)).scalar()
    practice_streak_average = (
        round(float(streak_avg), 2) if streak_avg is not None else None
    )

    recent_users = (
        db.query(User).order_by(User.created_at.desc()).limit(8).all()
    )
    recent_attempts = (
        db.query(QuizAttempt)
        .options(joinedload(QuizAttempt.course))
        .order_by(QuizAttempt.started_at.desc())
        .limit(8)
        .all()
    )
    recent_feedback_rows = (
        db.query(QuizFeedback)
        .options(joinedload(QuizFeedback.course))
        .order_by(QuizFeedback.created_at.desc())
        .limit(8)
        .all()
    )
    recent_report_rows = (
        db.query(QuestionReport)
        .order_by(QuestionReport.created_at.desc())
        .limit(8)
        .all()
    )

    return {
        "registered_users": int(registered_users),
        "guest_quiz_sessions": None,
        "guest_quiz_sessions_note": (
            "Guest quizzes are graded ephemerally and are not stored in the "
            "database. Track via Google Analytics event guest_quiz."
        ),
        "quiz_attempts": int(quiz_attempts),
        "questions_answered": int(questions_answered),
        "daily_practice_sessions": int(daily_practice_sessions),
        "average_accuracy": _average_accuracy(db),
        "practice_streak_average": practice_streak_average,
        "courses_available": int(courses_available),
        "total_questions": int(total_questions),
        "daily_active_users": _active_users_since(db, day_ago),
        "weekly_active_users": _active_users_since(db, week_ago),
        "monthly_active_users": _active_users_since(db, month_ago),
        "recent_registrations": [
            {
                "id": u.id,
                "name": u.name,
                "email_masked": _mask_email(u.email),
                "created_at": u.created_at,
            }
            for u in recent_users
        ],
        "recent_quiz_attempts": [
            {
                "id": a.id,
                "user_id": a.user_id,
                "course_name": a.course.name if a.course else None,
                "mode": a.mode,
                "questions_total": a.questions_total,
                "questions_correct": a.questions_correct,
                "started_at": a.started_at,
                "completed_at": a.completed_at,
            }
            for a in recent_attempts
        ],
        "recent_feedback": [
            {
                "id": f.id,
                "rating": f.rating,
                "message": f.message,
                "course_name": f.course.name if f.course else None,
                "created_at": f.created_at,
                "is_anonymous": f.user_id is None,
                "is_unread": getattr(f, "admin_reviewed_at", None) is None,
            }
            for f in recent_feedback_rows
        ],
        "recent_reports": [
            {
                "id": r.id,
                "question_id": r.question_id,
                "reason": r.reason,
                "status": getattr(r, "status", None) or "pending",
                "created_at": r.created_at,
            }
            for r in recent_report_rows
        ],
    }


def _report_count_map(db: Session, question_ids: list[int]) -> dict[int, int]:
    if not question_ids:
        return {}
    rows = (
        db.query(QuestionReport.question_id, func.count(QuestionReport.id))
        .filter(QuestionReport.question_id.in_(question_ids))
        .group_by(QuestionReport.question_id)
        .all()
    )
    return {qid: int(count) for qid, count in rows}


def _serialize_report(row: QuestionReport, report_counts: dict[int, int]) -> dict:
    question = row.question
    topic = question.topic if question else None
    course = topic.course if topic else None
    text = (question.question_text if question else "") or ""
    preview = text.strip().replace("\n", " ")
    if len(preview) > 120:
        preview = preview[:117] + "…"
    return {
        "id": row.id,
        "course_code": course.code if course else None,
        "course_name": course.name if course else None,
        "question_id": row.question_id,
        "question_preview": preview,
        "reason": row.reason,
        "comment": row.comment,
        "reported_at": row.created_at,
        "status": getattr(row, "status", None) or "pending",
        "status_changed_at": getattr(row, "status_changed_at", None),
        "admin_note": getattr(row, "admin_note", None),
        "report_count_for_question": report_counts.get(row.question_id, 1),
        "has_reporter": row.user_id is not None,
    }


def list_reports(
    db: Session,
    *,
    status: str | None = None,
    reason: str | None = None,
    search: str | None = None,
    sort: str = "newest",
    limit: int = 100,
    offset: int = 0,
) -> dict:
    query = db.query(QuestionReport).options(
        joinedload(QuestionReport.question)
        .joinedload(Question.topic)
        .joinedload(Topic.course)
    )

    if status and status != "all":
        if status == "pending":
            query = query.filter(
                or_(
                    QuestionReport.status == "pending",
                    QuestionReport.status.is_(None),
                )
            )
        else:
            query = query.filter(QuestionReport.status == status)

    if reason and reason != "all":
        query = query.filter(QuestionReport.reason == reason)

    if search:
        term = f"%{search.strip()}%"
        query = (
            query.join(Question, Question.id == QuestionReport.question_id)
            .join(Topic, Topic.id == Question.topic_id)
            .join(Course, Course.id == Topic.course_id)
            .filter(
                or_(
                    Question.question_text.ilike(term),
                    QuestionReport.comment.ilike(term),
                    QuestionReport.reason.ilike(term),
                    QuestionReport.admin_note.ilike(term),
                    Course.code.ilike(term),
                    Course.name.ilike(term),
                    func.cast(QuestionReport.question_id, String).ilike(term),
                )
            )
        )

    total = query.count()

    if sort == "oldest":
        query = query.order_by(QuestionReport.created_at.asc())
    elif sort == "question_id":
        query = query.order_by(QuestionReport.question_id.asc())
    elif sort == "status":
        query = query.order_by(
            QuestionReport.status.asc(), QuestionReport.created_at.desc()
        )
    else:
        query = query.order_by(QuestionReport.created_at.desc())

    rows = query.offset(offset).limit(min(limit, 200)).all()
    counts = _report_count_map(db, [r.question_id for r in rows])
    return {
        "items": [_serialize_report(r, counts) for r in rows],
        "total": int(total),
    }


def get_question_detail(db: Session, question_id: int) -> dict | None:
    question = (
        db.query(Question)
        .options(
            joinedload(Question.choices),
            joinedload(Question.topic).joinedload(Topic.course),
        )
        .filter(Question.id == question_id)
        .first()
    )
    if question is None:
        return None

    reports = (
        db.query(QuestionReport)
        .options(
            joinedload(QuestionReport.question)
            .joinedload(Question.topic)
            .joinedload(Topic.course)
        )
        .filter(QuestionReport.question_id == question_id)
        .order_by(QuestionReport.created_at.desc())
        .all()
    )
    counts = {question_id: len(reports)}
    topic = question.topic
    course = topic.course if topic else None
    return {
        "id": question.id,
        "question_text": question.question_text,
        "explanation": question.explanation,
        "question_type": question.question_type,
        "difficulty": question.difficulty,
        "answer": question.answer,
        "course_code": course.code if course else None,
        "course_name": course.name if course else None,
        "topic_name": topic.name if topic else None,
        "choices": [
            {
                "id": c.id,
                "choice_text": c.choice_text,
                "is_correct": c.is_correct,
                "sort_order": c.sort_order,
            }
            for c in (question.choices or [])
        ],
        "report_count": len(reports),
        "reports": [_serialize_report(r, counts) for r in reports],
    }


def _common_words(messages: list[str], top_n: int = 12) -> list[dict]:
    counter: Counter[str] = Counter()
    for message in messages:
        if not message:
            continue
        for word in re.findall(r"[a-zA-Z']{3,}", message.lower()):
            if word in _STOP_WORDS:
                continue
            counter[word] += 1
    return [{"word": w, "count": c} for w, c in counter.most_common(top_n)]


def _serialize_feedback(row: QuizFeedback) -> dict:
    reviewed = getattr(row, "admin_reviewed_at", None)
    return {
        "id": row.id,
        "rating": row.rating,
        "message": row.message,
        "created_at": row.created_at,
        "course_code": row.course.code if row.course else None,
        "course_name": row.course.name if row.course else None,
        "is_anonymous": row.user_id is None,
        "is_unread": reviewed is None,
        "admin_reviewed_at": reviewed,
    }


def compute_feedback_summary(
    db: Session,
    *,
    limit: int = 100,
    rating: str | None = None,
    unread_only: bool = False,
    since: datetime | None = None,
    until: datetime | None = None,
) -> dict:
    base = db.query(QuizFeedback)
    if rating in ("positive", "negative"):
        base = base.filter(QuizFeedback.rating == rating)
    if unread_only:
        base = base.filter(QuizFeedback.admin_reviewed_at.is_(None))
    if since is not None:
        base = base.filter(QuizFeedback.created_at >= since)
    if until is not None:
        base = base.filter(QuizFeedback.created_at <= until)

    total_all = db.query(func.count(QuizFeedback.id)).scalar() or 0
    unread_count = (
        db.query(func.count(QuizFeedback.id))
        .filter(QuizFeedback.admin_reviewed_at.is_(None))
        .scalar()
        or 0
    )
    positive = (
        db.query(func.count(QuizFeedback.id))
        .filter(QuizFeedback.rating == "positive")
        .scalar()
        or 0
    )
    negative = (
        db.query(func.count(QuizFeedback.id))
        .filter(QuizFeedback.rating == "negative")
        .scalar()
        or 0
    )
    rated = positive + negative

    rows = (
        base.options(joinedload(QuizFeedback.course))
        .order_by(QuizFeedback.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )
    items = [_serialize_feedback(f) for f in rows]
    filtered_total = base.count()

    return {
        "total": int(filtered_total if (rating or unread_only or since or until) else total_all),
        "unread_count": int(unread_count),
        "positive_count": int(positive),
        "negative_count": int(negative),
        "positive_percent": round(100.0 * positive / rated, 1) if rated else None,
        "negative_percent": round(100.0 * negative / rated, 1) if rated else None,
        "most_common_words": _common_words(
            [f.message for f in rows if f.message]
        ),
        "newest": items[:8],
        "items": items,
        "by_sentiment": {
            "positive": int(positive),
            "negative": int(negative),
            "other": int(max(0, total_all - rated)),
        },
    }


def mark_feedback_reviewed(db: Session, feedback_id: int) -> QuizFeedback | None:
    row = db.get(QuizFeedback, feedback_id)
    if row is None:
        return None
    if row.admin_reviewed_at is None:
        row.admin_reviewed_at = _utcnow()
    return row


def _topic_accuracy_rows(db: Session, *, order: str, limit: int = 10) -> list[dict]:
    min_attempts = 5
    agg = (
        db.query(
            Topic.id.label("topic_id"),
            Topic.name.label("topic_name"),
            Course.code.label("course_code"),
            func.sum(TopicPerformance.questions_attempted).label("attempted"),
            func.sum(TopicPerformance.questions_correct).label("correct"),
        )
        .join(TopicPerformance, TopicPerformance.topic_id == Topic.id)
        .join(Course, Course.id == Topic.course_id)
        .group_by(Topic.id, Topic.name, Course.code)
        .having(func.sum(TopicPerformance.questions_attempted) >= min_attempts)
        .all()
    )
    scored = []
    for row in agg:
        attempted = int(row.attempted or 0)
        correct = int(row.correct or 0)
        if attempted == 0:
            continue
        accuracy = round(100.0 * correct / attempted, 1)
        scored.append(
            {
                "topic_id": row.topic_id,
                "topic_name": row.topic_name,
                "course_code": row.course_code,
                "accuracy": accuracy,
                "questions_attempted": attempted,
            }
        )
    reverse = order == "desc"
    scored.sort(key=lambda item: item["accuracy"], reverse=reverse)
    return scored[:limit]


def compute_analytics(db: Session) -> dict:
    course_rows = (
        db.query(
            Course.id,
            Course.code,
            Course.name,
            func.count(QuizAttempt.id).label("attempts"),
        )
        .outerjoin(QuizAttempt, QuizAttempt.course_id == Course.id)
        .group_by(Course.id, Course.code, Course.name)
        .order_by(func.count(QuizAttempt.id).desc())
        .limit(10)
        .all()
    )

    completed = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.completed_at.isnot(None),
            QuizAttempt.questions_total > 0,
            QuizAttempt.questions_correct.isnot(None),
        )
        .all()
    )
    avg_score = None
    avg_duration = None
    avg_questions = None
    if completed:
        scores = [
            100.0 * a.questions_correct / a.questions_total
            for a in completed
            if a.questions_total
        ]
        if scores:
            avg_score = round(sum(scores) / len(scores), 1)
        durations = []
        for a in completed:
            if a.started_at and a.completed_at:
                start = a.started_at
                end = a.completed_at
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                seconds = (end - start).total_seconds()
                if 0 < seconds < 86400:
                    durations.append(seconds)
        if durations:
            avg_duration = round(sum(durations) / len(durations), 1)
        avg_questions = round(
            sum(a.questions_total for a in completed) / len(completed), 1
        )

    dp_total = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.mode == "daily_practice")
        .scalar()
        or 0
    )
    dp_completed = (
        db.query(func.count(QuizAttempt.id))
        .filter(
            QuizAttempt.mode == "daily_practice",
            QuizAttempt.completed_at.isnot(None),
        )
        .scalar()
        or 0
    )
    dp_completion = (
        round(100.0 * dp_completed / dp_total, 1) if dp_total else None
    )

    weakness_users = (
        db.query(func.count(func.distinct(TopicPerformance.user_id))).scalar()
        or 0
    )

    registered_attempts = db.query(func.count(QuizAttempt.id)).scalar() or 0
    registered_answers = db.query(func.count(UserAnswer.id)).scalar() or 0
    guest_feedback = (
        db.query(func.count(QuizFeedback.id))
        .filter(QuizFeedback.user_id.is_(None))
        .scalar()
        or 0
    )

    lowest = _topic_accuracy_rows(db, order="asc", limit=10)
    highest = _topic_accuracy_rows(db, order="desc", limit=10)

    return {
        "most_attempted_courses": [
            {
                "course_id": r.id,
                "course_code": r.code,
                "course_name": r.name,
                "attempts": int(r.attempts or 0),
            }
            for r in course_rows
        ],
        "most_difficult_topics": lowest,
        "highest_accuracy_topics": highest,
        "lowest_accuracy_topics": lowest,
        "average_quiz_score": avg_score,
        "average_quiz_duration_seconds": avg_duration,
        "average_questions_per_session": avg_questions,
        "daily_practice_completion_percent": dp_completion,
        "weakness_map_users": int(weakness_users),
        "weakness_map_note": (
            "Users with stored topic performance (eligible for Weakness Map)."
        ),
        "guest_vs_registered": {
            "registered_quiz_attempts": int(registered_attempts),
            "registered_answers": int(registered_answers),
            "guest_feedback_submissions": int(guest_feedback),
            "guest_quiz_sessions_persisted": None,
            "note": (
                "Guest quiz sessions are not persisted. Registered usage is "
                "from quiz_attempts / user_answers. Guest feedback count is "
                "anonymous quiz_feedback rows."
            ),
        },
        "top_searched_topics": None,
        "top_searched_topics_note": (
            "Topic search is not implemented; no search telemetry available."
        ),
    }


def compute_db_health(db: Session) -> dict:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_attempts = db.query(func.count(QuizAttempt.id)).scalar() or 0
    total_answers = db.query(func.count(UserAnswer.id)).scalar() or 0
    total_questions = (
        db.query(func.count(Question.id))
        .filter(Question.is_active.is_(True))
        .scalar()
        or 0
    )
    by_course = (
        db.query(
            Course.code,
            Course.name,
            func.count(Question.id).label("question_count"),
        )
        .outerjoin(Topic, Topic.course_id == Course.id)
        .outerjoin(
            Question,
            (Question.topic_id == Topic.id) & (Question.is_active.is_(True)),
        )
        .group_by(Course.id, Course.code, Course.name)
        .order_by(Course.code.asc())
        .all()
    )
    reports_waiting = (
        db.query(func.count(QuestionReport.id))
        .filter(
            or_(
                QuestionReport.status == "pending",
                QuestionReport.status.is_(None),
            )
        )
        .scalar()
        or 0
    )
    size_bytes, size_label = _db_file_size()

    from app.services.backup import latest_backup_info

    backup_meta = latest_backup_info()

    health_status = "ok"
    database_status = "connected"
    try:
        db.query(User.id).limit(1).first()
    except Exception:
        health_status = "degraded"
        database_status = "unavailable"

    return {
        "total_users": int(total_users),
        "total_attempts": int(total_attempts),
        "total_answers": int(total_answers),
        "total_questions": int(total_questions),
        "questions_by_course": [
            {
                "course_code": r.code,
                "course_name": r.name,
                "question_count": int(r.question_count or 0),
            }
            for r in by_course
        ],
        "reports_waiting": int(reports_waiting),
        "database_size_bytes": size_bytes,
        "database_size_label": size_label,
        "last_backup": backup_meta["last_backup"],
        "last_backup_note": backup_meta["last_backup_note"],
        "health_status": health_status,
        "database_status": database_status,
    }


def _average_improvement(db: Session) -> tuple[float | None, str | None]:
    """Compare early vs late accuracy per user with multiple completed quizzes."""
    improvements: list[float] = []
    users = db.query(User.id).all()
    for (user_id,) in users:
        attempts = (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.completed_at.isnot(None),
                QuizAttempt.questions_total > 0,
                QuizAttempt.questions_correct.isnot(None),
            )
            .order_by(QuizAttempt.completed_at.asc())
            .all()
        )
        if len(attempts) < 2:
            continue
        mid = len(attempts) // 2
        early = attempts[:mid]
        late = attempts[mid:]
        early_score = sum(
            a.questions_correct / a.questions_total for a in early
        ) / len(early)
        late_score = sum(
            a.questions_correct / a.questions_total for a in late
        ) / len(late)
        improvements.append(100.0 * (late_score - early_score))

    if not improvements:
        return None, (
            "Needs users with at least two completed quiz sessions to measure."
        )
    return round(sum(improvements) / len(improvements), 1), None


def compute_impact(db: Session) -> dict:
    from app.services.platform_stats import compute_platform_stats

    base = compute_platform_stats(db)
    week_ago = _utcnow() - timedelta(days=7)

    registered_users = db.query(func.count(User.id)).scalar() or 0
    quiz_attempts = db.query(func.count(QuizAttempt.id)).scalar() or 0
    courses_practiced = (
        db.query(func.count(func.distinct(QuizAttempt.course_id)))
        .filter(QuizAttempt.course_id.isnot(None))
        .scalar()
        or 0
    )
    users_last_7_days = (
        db.query(func.count(User.id))
        .filter(User.created_at >= week_ago)
        .scalar()
        or 0
    )
    quizzes_last_7_days = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.started_at >= week_ago)
        .scalar()
        or 0
    )

    daily_completed = (
        db.query(func.count(QuizAttempt.id))
        .filter(
            QuizAttempt.mode == "daily_practice",
            QuizAttempt.completed_at.isnot(None),
        )
        .scalar()
        or 0
    )
    strong = 0
    weak = 0
    for row in db.query(TopicPerformance).all():
        level = mastery_level_for(row.accuracy, row.questions_attempted)
        if level in MASTERED_LEVELS:
            strong += 1
        if level in WEAK_LEVELS:
            weak += 1

    avg_improve, improve_note = _average_improvement(db)
    questions_reported = db.query(func.count(QuestionReport.id)).scalar() or 0
    questions_fixed = (
        db.query(func.count(func.distinct(QuestionReport.question_id)))
        .filter(QuestionReport.status == "resolved")
        .scalar()
        or 0
    )
    feedback_received = db.query(func.count(QuizFeedback.id)).scalar() or 0

    return {
        "registered_users": int(registered_users),
        "quiz_attempts": int(quiz_attempts),
        "questions_answered": base["questions_completed"],
        "courses_practiced": int(courses_practiced),
        "feedback_submitted": int(feedback_received),
        "reports_submitted": int(questions_reported),
        "students_helped": base["students_helped"],
        "practice_sessions_completed": base["practice_sessions"],
        "daily_practices_completed": int(daily_completed),
        "average_improvement": avg_improve,
        "average_improvement_note": improve_note,
        "strong_topics_mastered": strong,
        "weaknesses_identified": weak,
        "questions_reported": int(questions_reported),
        "questions_fixed": int(questions_fixed),
        "feedback_received": int(feedback_received),
        "users_last_7_days": int(users_last_7_days),
        "quizzes_last_7_days": int(quizzes_last_7_days),
    }


def compute_question_quality(db: Session, *, limit: int = 15) -> dict:
    """Most-reported questions and triage backlog — real counts only."""
    unanswered = (
        db.query(func.count(QuestionReport.id))
        .filter(
            or_(
                QuestionReport.status == "pending",
                QuestionReport.status.is_(None),
            )
        )
        .scalar()
        or 0
    )

    multi_rows = (
        db.query(QuestionReport.question_id)
        .group_by(QuestionReport.question_id)
        .having(func.count(QuestionReport.id) >= 2)
        .all()
    )
    multi = len(multi_rows)

    ranked = (
        db.query(
            QuestionReport.question_id,
            func.count(QuestionReport.id).label("report_count"),
            func.sum(
                case(
                    (
                        or_(
                            QuestionReport.status == "pending",
                            QuestionReport.status.is_(None),
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("pending_count"),
        )
        .group_by(QuestionReport.question_id)
        .order_by(func.count(QuestionReport.id).desc())
        .limit(min(limit, 50))
        .all()
    )

    most: list[dict] = []
    for qid, report_count, pending_count in ranked:
        question = (
            db.query(Question)
            .options(joinedload(Question.topic).joinedload(Topic.course))
            .filter(Question.id == qid)
            .first()
        )
        text = (question.question_text if question else "") or ""
        preview = text.strip().replace("\n", " ")
        if len(preview) > 100:
            preview = preview[:97] + "…"
        course = question.topic.course if question and question.topic else None
        most.append(
            {
                "question_id": int(qid),
                "report_count": int(report_count),
                "pending_count": int(pending_count or 0),
                "course_code": course.code if course else None,
                "question_preview": preview,
            }
        )

    return {
        "unanswered_reports_count": int(unanswered),
        "questions_with_multiple_reports": int(multi),
        "most_reported_questions": most,
    }

def compute_reliability(db: Session) -> dict:
    """Aggregate reliability metrics without exposing PII."""
    import time

    from app.core.config import settings
    from app.core.error_buffer import recent_errors
    from app.routes import health as health_route

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_quizzes = db.query(func.count(QuizAttempt.id)).scalar() or 0
    feedback_count = db.query(func.count(QuizFeedback.id)).scalar() or 0
    reported_questions = db.query(func.count(QuestionReport.id)).scalar() or 0
    pending_reports = (
        db.query(func.count(QuestionReport.id))
        .filter(
            or_(
                QuestionReport.status == "pending",
                QuestionReport.status.is_(None),
            )
        )
        .scalar()
        or 0
    )
    dsn = (settings.sentry_dsn or "").strip()
    sentry_configured = bool(dsn) and settings.environment == "production"

    return {
        "total_users": int(total_users),
        "total_quizzes": int(total_quizzes),
        "feedback_count": int(feedback_count),
        "reported_questions": int(reported_questions),
        "pending_reports": int(pending_reports),
        "sentry_configured": sentry_configured,
        "environment": settings.environment,
        "version": settings.app_version,
        "uptime_seconds": int(time.time() - health_route._STARTED_AT),
        "recent_errors": recent_errors(20),
    }

