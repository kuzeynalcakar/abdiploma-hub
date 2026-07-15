"""Aggregate real platform metrics for public display."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import QuizAttempt, TopicPerformance, User, UserAnswer


def compute_platform_stats(db: Session) -> dict:
    students_helped = (
        db.query(func.count(func.distinct(QuizAttempt.user_id)))
        .filter(QuizAttempt.completed_at.isnot(None))
        .scalar()
        or 0
    )

    questions_completed = (
        db.query(func.coalesce(func.sum(TopicPerformance.questions_attempted), 0))
        .scalar()
        or 0
    )
    if questions_completed == 0:
        questions_completed = db.query(func.count(UserAnswer.id)).scalar() or 0

    practice_sessions = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.completed_at.isnot(None))
        .scalar()
        or 0
    )

    return {
        "students_helped": int(students_helped),
        "questions_completed": int(questions_completed),
        "practice_sessions": int(practice_sessions),
    }
