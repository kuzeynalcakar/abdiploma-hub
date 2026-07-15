"""Shared question filtering for quiz and guest quiz endpoints."""

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models import Course, Question, Topic

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def _validate_course(db: Session, course_id: int) -> Course:
    from fastapi import HTTPException

    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_active.is_(True))
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course


def _validate_topics(
    db: Session, course_id: int, topic_ids: list[int] | None
) -> list[int] | None:
    from fastapi import HTTPException

    if not topic_ids:
        return None

    topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
    if len(topics) != len(set(topic_ids)):
        raise HTTPException(status_code=404, detail="One or more topics not found.")

    for topic in topics:
        if topic.course_id != course_id:
            raise HTTPException(
                status_code=400,
                detail="Topic does not belong to the selected course.",
            )

    return list(dict.fromkeys(topic_ids))


def fetch_quiz_questions(
    db: Session,
    course_id: int,
    *,
    topic_id: int | None = None,
    topic_ids: list[int] | None = None,
    difficulty: str | None = None,
    count: int = 10,
) -> tuple[Course, list[Question], dict]:
    """Return a random sample of active questions across all formats."""
    from fastapi import HTTPException

    course = _validate_course(db, course_id)

    selected_topic_ids = topic_ids
    if topic_id is not None:
        _validate_topics(db, course_id, [topic_id])
        selected_topic_ids = [topic_id]
    elif topic_ids:
        selected_topic_ids = _validate_topics(db, course_id, topic_ids)

    if difficulty is not None and difficulty.lower() not in VALID_DIFFICULTIES:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be easy, medium, or hard.",
        )

    query = (
        db.query(Question)
        .join(Topic, Question.topic_id == Topic.id)
        .filter(
            Topic.course_id == course_id,
            Question.is_active.is_(True),
        )
        .options(selectinload(Question.choices), selectinload(Question.topic))
    )

    if selected_topic_ids:
        query = query.filter(Question.topic_id.in_(selected_topic_ids))

    if difficulty is not None:
        query = query.filter(
            func.lower(Question.difficulty) == difficulty.lower()
        )

    available_count = count_matching_questions(
        db,
        course_id,
        topic_id=topic_id,
        topic_ids=topic_ids,
        difficulty=difficulty,
    )
    questions = query.order_by(func.random()).limit(count).all()

    if not questions:
        raise HTTPException(
            status_code=404,
            detail="No questions available for the selected filters.",
        )

    return course, questions, {
        "requested_count": count,
        "question_count": len(questions),
        "available_count": available_count,
    }


def count_matching_questions(
    db: Session,
    course_id: int,
    *,
    topic_id: int | None = None,
    topic_ids: list[int] | None = None,
    difficulty: str | None = None,
) -> int:
    """Count active questions for the given filters."""
    from fastapi import HTTPException

    _validate_course(db, course_id)

    selected_topic_ids = topic_ids
    if topic_id is not None:
        _validate_topics(db, course_id, [topic_id])
        selected_topic_ids = [topic_id]
    elif topic_ids:
        selected_topic_ids = _validate_topics(db, course_id, topic_ids)

    if difficulty is not None and difficulty.lower() not in VALID_DIFFICULTIES:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be easy, medium, or hard.",
        )

    query = (
        db.query(Question)
        .join(Topic, Question.topic_id == Topic.id)
        .filter(
            Topic.course_id == course_id,
            Question.is_active.is_(True),
        )
    )

    if selected_topic_ids:
        query = query.filter(Question.topic_id.in_(selected_topic_ids))

    if difficulty is not None:
        query = query.filter(
            func.lower(Question.difficulty) == difficulty.lower()
        )

    return query.count()