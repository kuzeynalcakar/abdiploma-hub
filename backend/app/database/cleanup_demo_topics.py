"""Remove the old demo topics created by seed.py.

Deletes only the four demo topics, scoped to the courses seed.py put
them in — "Trigonometry" in MATH10C or MATH20-1 is real curriculum and
is never touched. Topics are kept if any questions are attached, or if
quiz attempts / topic performance rows reference them (deleting those
would break history or foreign keys).

Usage, from the backend directory:

    python -m app.database.cleanup_demo_topics
"""

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models import Course, Question, QuizAttempt, Topic, TopicPerformance

# Course code -> demo topic names, exactly as created by seed.py.
DEMO_TOPICS = {
    "MATH30-1": ["Functions", "Logarithms", "Trigonometry"],
    "BIO30": ["Cell Biology"],
}


def cleanup_demo_topics(db: Session) -> None:
    deleted = 0
    skipped: list[str] = []

    for course_code, topic_names in DEMO_TOPICS.items():
        course = db.query(Course).filter(Course.code == course_code).first()
        if course is None:
            continue

        for topic_name in topic_names:
            topic = (
                db.query(Topic)
                .filter(Topic.course_id == course.id, Topic.name == topic_name)
                .first()
            )
            if topic is None:
                continue

            label = f"{course_code} / {topic_name}"

            question_count = (
                db.query(Question)
                .filter(Question.topic_id == topic.id)
                .count()
            )
            if question_count > 0:
                skipped.append(f"{label} ({question_count} questions attached)")
                continue

            referenced = (
                db.query(QuizAttempt)
                .filter(QuizAttempt.topic_id == topic.id)
                .count()
                + db.query(TopicPerformance)
                .filter(TopicPerformance.topic_id == topic.id)
                .count()
            )
            if referenced > 0:
                skipped.append(f"{label} (referenced by attempts/performance)")
                continue

            db.delete(topic)
            deleted += 1

    db.commit()

    print(f"Deleted topics: {deleted}")
    if skipped:
        print("Skipped:")
        for entry in skipped:
            print(f"  - {entry}")


if __name__ == "__main__":
    session = SessionLocal()
    try:
        cleanup_demo_topics(session)
    finally:
        session.close()
