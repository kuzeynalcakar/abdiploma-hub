"""Compute real learning impact metrics from stored answer history."""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models import QuizAttempt, TopicPerformance, UserAnswer


def _accuracy_for_answers(answers: list[UserAnswer]) -> float | None:
    graded = [answer for answer in answers if answer.auto_graded]
    if not graded:
        return None
    correct = sum(1 for answer in graded if answer.is_correct is True)
    return round(correct / len(graded) * 100, 1)


def compute_learning_impact(db: Session, user_id: int) -> dict:
    """Build aggregate impact metrics for dashboard display."""
    performances = (
        db.query(TopicPerformance)
        .filter(
            TopicPerformance.user_id == user_id,
            TopicPerformance.questions_attempted > 0,
        )
        .options(joinedload(TopicPerformance.topic))
        .all()
    )

    answers = (
        db.query(UserAnswer)
        .join(QuizAttempt, UserAnswer.quiz_attempt_id == QuizAttempt.id)
        .filter(
            QuizAttempt.user_id == user_id,
            UserAnswer.auto_graded.is_(True),
        )
        .order_by(UserAnswer.answered_at.asc())
        .all()
    )

    if performances:
        total_questions = sum(item.questions_attempted for item in performances)
        total_correct = sum(item.questions_correct for item in performances)
    else:
        total_questions = len(answers)
        total_correct = sum(1 for answer in answers if answer.is_correct is True)

    overall_accuracy = (
        round(total_correct / total_questions * 100, 1) if total_questions else 0.0
    )

    completed_attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.completed_at.isnot(None),
        )
        .all()
    )

    practice_sessions = len(completed_attempts)
    daily_practice_sessions = sum(
        1 for attempt in completed_attempts if attempt.mode == "daily_practice"
    )

    strong_topics_count = sum(
        1
        for item in performances
        if item.questions_attempted >= 3 and item.accuracy >= 75.0
    )

    weaknesses_identified = sum(
        1
        for item in performances
        if item.questions_attempted >= 1 and item.accuracy < 75.0
    )

    topics_improved = strong_topics_count

    targeted_questions_completed = (
        db.query(UserAnswer)
        .join(QuizAttempt, UserAnswer.quiz_attempt_id == QuizAttempt.id)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.mode == "daily_practice",
        )
        .count()
    )

    practiced_course_ids = {
        performance.topic.course_id
        for performance in performances
        if performance.questions_attempted > 0
    }
    practiced_course_ids.update(
        attempt.course_id
        for attempt in completed_attempts
        if attempt.completed_at is not None
    )
    subjects_practiced = len(practiced_course_ids)

    early_accuracy = None
    recent_accuracy = None
    accuracy_change = None

    if len(answers) >= 10:
        midpoint = len(answers) // 2
        early_accuracy = _accuracy_for_answers(answers[:midpoint])
        recent_accuracy = _accuracy_for_answers(answers[midpoint:])
        if early_accuracy is not None and recent_accuracy is not None:
            accuracy_change = round(recent_accuracy - early_accuracy, 1)

    return {
        "questions_completed": total_questions,
        "practice_sessions": practice_sessions,
        "subjects_practiced": subjects_practiced,
        "daily_practice_sessions": daily_practice_sessions,
        "overall_accuracy": overall_accuracy,
        "strong_topics_count": strong_topics_count,
        "topics_improved": topics_improved,
        "weaknesses_identified": weaknesses_identified,
        "targeted_questions_completed": targeted_questions_completed,
        "early_accuracy": early_accuracy,
        "recent_accuracy": recent_accuracy,
        "accuracy_change": accuracy_change,
    }
