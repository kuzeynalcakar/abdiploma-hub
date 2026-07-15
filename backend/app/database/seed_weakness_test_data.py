"""Seed a test student with known answer history for weakness map verification.

Usage, from the backend directory:

    python -m app.database.seed_weakness_test_data
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models import Course, Question, QuizAttempt, Topic, User, UserAnswer
from app.services.weakness_analysis import analyze_course_weakness

TEST_EMAIL = "weakness.test@example.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Weakness Test Student"
COURSE_CODE = "MATH30-1"

# topic_name -> (correct, wrong) for auto-graded answers
TOPIC_PATTERNS: dict[str, tuple[int, int]] = {
    "Trigonometric Identities": (8, 12),
    "Exponential Functions": (18, 2),
    "Polynomial Functions": (15, 5),
}


def _get_or_create_user(db: Session) -> User:
    user = db.query(User).filter(User.email == TEST_EMAIL).first()
    if user is None:
        user = User(
            name=TEST_NAME,
            email=TEST_EMAIL,
            password_hash=hash_password(TEST_PASSWORD),
        )
        db.add(user)
        db.flush()
    return user


def _pick_questions(db: Session, topic_id: int, count: int) -> list[Question]:
    return (
        db.query(Question)
        .options(selectinload(Question.choices))
        .filter(Question.topic_id == topic_id, Question.is_active.is_(True))
        .order_by(Question.id)
        .limit(count)
        .all()
    )


def _clear_test_history(db: Session, user_id: int, course_id: int) -> None:
    attempt_ids = [
        row[0]
        for row in db.query(QuizAttempt.id)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.course_id == course_id,
        )
        .all()
    ]
    if attempt_ids:
        db.query(UserAnswer).filter(
            UserAnswer.quiz_attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)
        db.query(QuizAttempt).filter(QuizAttempt.id.in_(attempt_ids)).delete(
            synchronize_session=False
        )


def seed_weakness_test_data(db: Session) -> dict:
    course = db.query(Course).filter(Course.code == COURSE_CODE).first()
    if course is None:
        raise RuntimeError(f"Course {COURSE_CODE} not found.")

    user = _get_or_create_user(db)
    _clear_test_history(db, user.id, course.id)

    topics = {
        topic.name: topic
        for topic in db.query(Topic).filter(Topic.course_id == course.id).all()
    }

    attempt = QuizAttempt(
        user_id=user.id,
        course_id=course.id,
        mode="quiz",
        questions_total=sum(
            correct + wrong for correct, wrong in TOPIC_PATTERNS.values()
        ),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.flush()

    answered_at = datetime.now(timezone.utc)
    created = 0

    for topic_name, (correct_count, wrong_count) in TOPIC_PATTERNS.items():
        topic = topics.get(topic_name)
        if topic is None:
            continue

        needed = correct_count + wrong_count
        questions = _pick_questions(db, topic.id, needed)
        if len(questions) < needed:
            raise RuntimeError(
                f"Not enough questions in {topic_name}: need {needed}, "
                f"found {len(questions)}"
            )

        if topic_name == "Trigonometric Identities":
            # Most-recent answers are listed first: 8 recent misses in last 12.
            outcomes = [False] * 8 + [True] * 4 + [False] * 4 + [True] * 4
        else:
            outcomes = [False] * wrong_count + [True] * correct_count
        if len(outcomes) < needed:
            outcomes.extend([True] * (needed - len(outcomes)))

        for index, question in enumerate(questions):
            should_be_correct = outcomes[index]
            choice_id = None
            if question.question_type == "multiple_choice":
                correct_choice = next(
                    (choice for choice in question.choices if choice.is_correct),
                    None,
                )
                incorrect_choice = next(
                    (choice for choice in question.choices if not choice.is_correct),
                    None,
                )
                if correct_choice is None or incorrect_choice is None:
                    continue
                choice_id = (
                    correct_choice.id
                    if should_be_correct
                    else incorrect_choice.id
                )

            db.add(
                UserAnswer(
                    quiz_attempt_id=attempt.id,
                    question_id=question.id,
                    answer_choice_id=choice_id,
                    response_text=None,
                    auto_graded=True,
                    is_correct=should_be_correct,
                    answered_at=answered_at - timedelta(minutes=created),
                )
            )
            created += 1

    db.commit()

    analysis = analyze_course_weakness(db, user.id, course.id)
    identities = next(
        (
            item
            for item in analysis["needs_practice"]
            if item.topic_name == "Trigonometric Identities"
        ),
        None,
    )

    return {
        "user_email": TEST_EMAIL,
        "user_password": TEST_PASSWORD,
        "answers_created": created,
        "identities_accuracy": identities.accuracy if identities else None,
        "identities_score": identities.weakness_score if identities else None,
        "strong_topics": [item.topic_name for item in analysis["strong_topics"]],
        "needs_practice": [item.topic_name for item in analysis["needs_practice"]],
    }


def main() -> None:
    db = SessionLocal()
    try:
        result = seed_weakness_test_data(db)
        print("Seeded weakness test student:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
