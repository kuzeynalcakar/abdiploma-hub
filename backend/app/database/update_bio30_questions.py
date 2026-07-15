"""Update existing BIO30 questions in production DB from corrected JSON.

Matches by exact question_text. Preserves question IDs and all user data.
Does not delete or insert questions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.question_validator import normalize_question_type
from app.database.session import SessionLocal
from app.models import Course, Question, QuestionHistory, QuizAttempt, Topic, UserAnswer

JSON_PATH = (
    Path(__file__).resolve().parents[3]
    / "questions.json"
    / "biology30_questions_final.json"
)

UPDATE_FIELDS = ("answer", "explanation", "common_mistake", "unit", "outcome_code", "skill_tested")


def _norm(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _snapshot_bio30(db: Session, course_id: int) -> dict:
    q_ids = [
        r[0]
        for r in db.query(Question.id)
        .join(Topic)
        .filter(Topic.course_id == course_id, Question.is_active.is_(True))
        .all()
    ]
    return {
        "question_count": len(q_ids),
        "question_ids": set(q_ids),
        "user_answers": db.query(UserAnswer)
        .filter(UserAnswer.question_id.in_(q_ids))
        .count()
        if q_ids
        else 0,
        "question_history": db.query(QuestionHistory)
        .filter(QuestionHistory.question_id.in_(q_ids))
        .count()
        if q_ids
        else 0,
        "quiz_attempts": db.query(QuizAttempt).count(),
    }


def update_bio30_from_json(db: Session, items: list[dict]) -> dict:
    course = db.query(Course).filter(Course.code == "BIO30").first()
    if course is None:
        raise RuntimeError("BIO30 course not found in database")

    before = _snapshot_bio30(db, course.id)

    topic_cache: dict[str, Topic] = {
        t.name: t
        for t in db.query(Topic).filter(Topic.course_id == course.id).all()
    }

    updated = 0
    skipped = 0
    not_found: list[int] = []
    errors: list[str] = []
    updated_ids: list[int] = []

    bio_items = [item for item in items if item.get("course_code") == "BIO30"]
    if len(bio_items) != 300:
        errors.append(f"Expected 300 BIO30 JSON items, got {len(bio_items)}")

    for index, item in enumerate(bio_items):
        question = (
            db.query(Question)
            .join(Topic)
            .filter(
                Topic.course_id == course.id,
                Question.question_text == item["question_text"],
            )
            .first()
        )
        if question is None:
            not_found.append(index)
            continue

        topic_name = item["topic"]
        topic = topic_cache.get(topic_name)
        if topic is None:
            errors.append(f"item {index}: topic '{topic_name}' not found")
            continue

        changes: dict = {}
        if question.topic_id != topic.id:
            changes["topic_id"] = topic.id

        for field in UPDATE_FIELDS:
            json_val = item.get(field)
            if field in ("answer",):
                json_val = _norm(json_val) if json_val is not None else None
            db_val = getattr(question, field)
            if _norm(db_val) != _norm(json_val):
                changes[field] = json_val

        if not changes:
            skipped += 1
            continue

        for field, value in changes.items():
            setattr(question, field, value)
        updated += 1
        updated_ids.append(question.id)

    if not_found:
        errors.append(f"{len(not_found)} JSON items not matched in DB")

    db.commit()

    after = _snapshot_bio30(db, course.id)

    # Verify JSON match for updated rows
    verify_failures = []
    for index, item in enumerate(bio_items):
        question = (
            db.query(Question)
            .join(Topic)
            .filter(
                Topic.course_id == course.id,
                Question.question_text == item["question_text"],
            )
            .first()
        )
        if question is None:
            continue
        for field in UPDATE_FIELDS:
            if _norm(getattr(question, field)) != _norm(item.get(field)):
                verify_failures.append(
                    (question.id, field, getattr(question, field), item.get(field))
                )
        if question.topic.name != item["topic"]:
            verify_failures.append(
                (question.id, "topic", question.topic.name, item["topic"])
            )

    # Duplicate question_text check within BIO30
    from sqlalchemy import func

    dupes = (
        db.query(Question.question_text, func.count(Question.id))
        .join(Topic)
        .filter(Topic.course_id == course.id, Question.is_active.is_(True))
        .group_by(Question.question_text)
        .having(func.count(Question.id) > 1)
        .all()
    )

    return {
        "updated": updated,
        "skipped": skipped,
        "not_found": len(not_found),
        "updated_question_ids": updated_ids,
        "errors": errors,
        "before": before,
        "after": after,
        "verify_failures": len(verify_failures),
        "duplicate_stems": len(dupes),
        "ids_preserved": before["question_ids"] == after["question_ids"],
        "progress_preserved": (
            before["user_answers"] == after["user_answers"]
            and before["question_history"] == after["question_history"]
            and before["quiz_attempts"] == after["quiz_attempts"]
        ),
    }


def main() -> None:
    items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        result = update_bio30_from_json(db, items)
    finally:
        db.close()

    print("=== BIO30 Production Update ===")
    print(f"Rows updated: {result['updated']}")
    print(f"Skipped (already matched): {result['skipped']}")
    print(f"Not found: {result['not_found']}")
    print(f"BIO30 count before/after: {result['before']['question_count']} / {result['after']['question_count']}")
    print(f"Duplicate stems: {result['duplicate_stems']}")
    print(f"JSON field verify failures: {result['verify_failures']}")
    print(f"Question IDs preserved: {result['ids_preserved']}")
    print(f"User progress preserved: {result['progress_preserved']}")
    print(f"user_answers: {result['before']['user_answers']} -> {result['after']['user_answers']}")
    print(f"question_history: {result['before']['question_history']} -> {result['after']['question_history']}")
    print(f"quiz_attempts: {result['before']['quiz_attempts']} -> {result['after']['quiz_attempts']}")
    if result["errors"]:
        print("Errors:")
        for e in result["errors"]:
            print(f"  - {e}")
    if result["verify_failures"] or result["not_found"] or not result["ids_preserved"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
