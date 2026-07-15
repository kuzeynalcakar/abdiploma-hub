"""Import pre-generated questions from a local JSON file.

Questions are generated beforehand (by LLM or manual authoring) and
imported here — no API calls or LLM code ever run in this pipeline.

Supports all three Alberta diploma exam question formats:
multiple_choice, numerical_response and written_response. Human-readable
type and difficulty values ("Multiple Choice", "Easy") are normalized to
their canonical database forms ("multiple_choice", "easy").

Usage, from the backend directory:

    python -m app.database.question_import path/to/questions.json

See import_questions.json.example for the expected format. Courses and
topics must already exist; the pipeline never creates curriculum rows.
"""

import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.question_validator import (
    normalize_difficulty,
    normalize_question_type,
    validate_question,
)
from app.database.session import SessionLocal
from app.models import AnswerChoice, Course, Question, Topic
from question_tools import assert_mc_position_balanced, format_position_report
from app.services.short_answers import dump_accepted_answers


VALID_SOURCES = ("manual", "ai")


def _accepted_answers_json(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return dump_accepted_answers([str(v) for v in value])
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def validate_item(item: dict, index: int) -> list[str]:
    """Return a list of problems for one JSON item (empty list = valid)."""
    label = f"item {index}"
    errors = [
        f"{label}: {reason}" for reason in validate_question(item, index)
    ]

    source = item.get("source", "ai")
    if source not in VALID_SOURCES:
        errors.append(
            f"{label}: source must be one of {VALID_SOURCES}, got '{source}'"
        )

    return errors


def _optional_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value) -> str | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def import_questions(db: Session, items: list[dict]) -> None:
    imported = 0
    skipped = 0
    errors: list[str] = []

    for index, item in enumerate(items):
        item_errors = validate_item(item, index)
        if item_errors:
            errors.extend(item_errors)
            continue

        course = (
            db.query(Course)
            .filter(Course.code == item["course_code"])
            .first()
        )
        if course is None:
            errors.append(
                f"item {index}: course '{item['course_code']}' not found"
            )
            continue

        topic = (
            db.query(Topic)
            .filter(Topic.course_id == course.id, Topic.name == item["topic"])
            .first()
        )
        if topic is None:
            errors.append(
                f"item {index}: topic '{item['topic']}' not found in course "
                f"'{course.code}'"
            )
            continue

        duplicate = (
            db.query(Question)
            .filter(
                Question.topic_id == topic.id,
                Question.question_text == item["question_text"],
            )
            .first()
        )
        if duplicate is not None:
            skipped += 1
            continue

        question = Question(
            topic=topic,
            question_text=item["question_text"],
            question_type=normalize_question_type(
                item.get("question_type", "multiple_choice")
            ),
            difficulty=normalize_difficulty(item.get("difficulty")),
            source=item.get("source", "ai"),
            explanation=item.get("explanation"),
            unit=_optional_str(item.get("unit")),
            outcome_code=_optional_str(item.get("outcome_code")),
            skill_tested=_optional_str(item.get("skill_tested")),
            estimated_time_seconds=_optional_int(
                item.get("estimated_time_seconds")
            ),
            answer=_optional_str(item.get("answer")),
            accepted_answers=_accepted_answers_json(item.get("accepted_answers")),
            common_mistake=_optional_str(item.get("common_mistake")),
        )
        db.add(question)
        # Only multiple choice questions carry choices; the validator has
        # already guaranteed the list is empty for the other formats.
        for sort_order, choice in enumerate(item.get("choices", [])):
            db.add(
                AnswerChoice(
                    question=question,
                    choice_text=choice["text"],
                    is_correct=choice.get("is_correct", False),
                    sort_order=sort_order,
                )
            )
        imported += 1

    db.commit()

    print(f"Imported: {imported}")
    print(f"Skipped duplicates: {skipped}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m app.database.question_import <questions.json>")
        raise SystemExit(1)

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}")
        raise SystemExit(1)

    with path.open(encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        print("The JSON file must contain a list of question objects.")
        raise SystemExit(1)

    try:
        mc_pos = assert_mc_position_balanced(items, label=str(path.name))
        print(
            "MC correct-position distribution:",
            format_position_report(mc_pos),
        )
    except ValueError as exc:
        print(f"IMPORT BLOCKED (MC position bias): {exc}")
        raise SystemExit(1) from exc

    db = SessionLocal()
    try:
        import_questions(db, items)
    finally:
        db.close()


if __name__ == "__main__":
    main()
