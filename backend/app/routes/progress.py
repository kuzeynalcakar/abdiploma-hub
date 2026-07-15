from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models import Course, QuizAttempt, TopicPerformance, User
from app.schemas.progress import LearningImpact, ProgressResponse
from app.services.progress_impact import compute_learning_impact

router = APIRouter(prefix="/progress", tags=["progress"])

STRONG_ACCURACY_THRESHOLD = 75


@router.get("", response_model=ProgressResponse)
def get_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Per-course practice statistics for the logged-in student,
    aggregated from stored topic performance and quiz attempts."""
    performances = (
        db.query(TopicPerformance)
        .filter(TopicPerformance.user_id == current_user.id)
        .options(selectinload(TopicPerformance.topic))
        .all()
    )

    by_course: dict[int, list[TopicPerformance]] = {}
    for performance in performances:
        by_course.setdefault(performance.topic.course_id, []).append(
            performance
        )

    completed_counts = dict(
        db.query(QuizAttempt.course_id, func.count(QuizAttempt.id))
        .filter(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.completed_at.isnot(None),
        )
        .group_by(QuizAttempt.course_id)
        .all()
    )

    courses = []
    for course_id, course_performances in by_course.items():
        course = db.get(Course, course_id)
        answered = sum(p.questions_attempted for p in course_performances)
        correct = sum(p.questions_correct for p in course_performances)
        accuracy = round(correct / answered * 100, 1) if answered else 0.0

        topics = sorted(
            (
                {
                    "topic_id": p.topic_id,
                    "topic_name": p.topic.name,
                    "questions_attempted": p.questions_attempted,
                    "questions_correct": p.questions_correct,
                    "accuracy": round(p.accuracy, 1),
                }
                for p in course_performances
            ),
            key=lambda t: t["accuracy"],
        )

        courses.append(
            {
                "course_id": course_id,
                "course_code": course.code,
                "course_name": course.name,
                "quizzes_completed": completed_counts.get(course_id, 0),
                "questions_answered": answered,
                "correct_answers": correct,
                "accuracy_percent": accuracy,
                "strong_topics": [
                    t for t in topics
                    if t["accuracy"] >= STRONG_ACCURACY_THRESHOLD
                ],
                "weak_topics": [
                    t for t in topics
                    if t["accuracy"] < STRONG_ACCURACY_THRESHOLD
                ],
            }
        )

    courses.sort(key=lambda c: c["course_code"])
    impact = compute_learning_impact(db, current_user.id)
    return {
        "courses": courses,
        "practice_streak": current_user.practice_streak or 0,
        "last_practice_date": (
            current_user.last_practice_date.isoformat()
            if current_user.last_practice_date
            else None
        ),
        "impact": LearningImpact(**impact),
    }
