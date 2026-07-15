"""Validate generated question JSON files before importing.

Pure local validation: no database access, no API calls. Run this on a
generated file first, then import it with app.database.question_import.

Supports the three Alberta diploma exam question formats:

- multiple_choice   ("Multiple Choice")   — 4 choices, exactly 1 correct
- numerical_response ("Numerical Response") — no choices, numeric answer
- written_response  ("Written Response")  — no choices, explanation is the
                                            solution guide / rubric

Usage, from the backend directory:

    python -m app.database.question_validator questions.json
"""

import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("course_code", "topic", "question_text")

VALID_DIFFICULTIES = ("easy", "medium", "hard")

MULTIPLE_CHOICE = "multiple_choice"
NUMERICAL_RESPONSE = "numerical_response"
WRITTEN_RESPONSE = "written_response"

VALID_QUESTION_TYPES = (MULTIPLE_CHOICE, NUMERICAL_RESPONSE, WRITTEN_RESPONSE)

# Accept both database-canonical values and human-readable JSON values.
_QUESTION_TYPE_ALIASES = {
    "multiple_choice": MULTIPLE_CHOICE,
    "multiple choice": MULTIPLE_CHOICE,
    "numerical_response": NUMERICAL_RESPONSE,
    "numerical response": NUMERICAL_RESPONSE,
    "written_response": WRITTEN_RESPONSE,
    "written response": WRITTEN_RESPONSE,
}

MULTIPLE_CHOICE_COUNT = 4

MIN_QUESTION_LENGTH = 10


def _normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def normalize_question_type(value) -> str | None:
    """Map a question_type value to its canonical form, or None if invalid."""
    if not isinstance(value, str):
        return None
    return _QUESTION_TYPE_ALIASES.get(_normalize(value))


def normalize_difficulty(value) -> str | None:
    """Map a difficulty value to its canonical form, or None if invalid."""
    if not isinstance(value, str):
        return None
    normalized = _normalize(value)
    return normalized if normalized in VALID_DIFFICULTIES else None


def is_numerical_answer(value) -> bool:
    """True if the answer represents a single numeric value.

    Accepts ints/floats directly, and strings such as "480", "-12" or
    "$2.5$" (surrounding LaTeX dollar delimiters are tolerated).
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    if not isinstance(value, str):
        return False
    text = value.strip().strip("$").strip()
    if not text:
        return False
    try:
        float(text)
    except ValueError:
        return False
    return True


def _validate_choices(choices, reasons: list[str]) -> None:
    """Multiple choice rules: 4 unique choices, exactly one correct."""
    if len(choices) != MULTIPLE_CHOICE_COUNT:
        reasons.append(
            f"multiple choice questions need exactly "
            f"{MULTIPLE_CHOICE_COUNT} choices, got {len(choices)}"
        )

    texts = []
    correct_count = 0
    for choice_index, choice in enumerate(choices):
        if not isinstance(choice, dict):
            reasons.append(f"choice {choice_index} is not a JSON object")
            continue
        text = choice.get("text")
        if not isinstance(text, str) or not text.strip():
            reasons.append(f"choice {choice_index} has empty text")
        else:
            texts.append(_normalize(text))
        if choice.get("is_correct") is True:
            correct_count += 1

    if len(texts) != len(set(texts)):
        reasons.append("duplicate choice text")

    if correct_count != 1:
        reasons.append(
            f"exactly one choice must have is_correct=true "
            f"(found {correct_count})"
        )


def validate_question(item: dict, index: int) -> list[str]:
    """Return reasons this item is invalid (empty list = valid)."""
    reasons = []

    if not isinstance(item, dict):
        return ["not a JSON object"]

    for field in REQUIRED_FIELDS:
        if not item.get(field):
            reasons.append(f"missing required field '{field}'")
    if reasons:
        return reasons

    question_type = normalize_question_type(
        item.get("question_type", MULTIPLE_CHOICE)
    )
    if question_type is None:
        reasons.append(
            f"question_type must be one of {'/'.join(VALID_QUESTION_TYPES)}, "
            f"got '{item.get('question_type')}'"
        )
        return reasons

    question_text = item["question_text"]
    if not isinstance(question_text, str) or len(question_text.strip()) < MIN_QUESTION_LENGTH:
        reasons.append(
            f"question_text must be at least {MIN_QUESTION_LENGTH} characters"
        )

    explanation = item.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip():
        if question_type == WRITTEN_RESPONSE:
            reasons.append(
                "explanation is required (it is the solution guide/rubric "
                "for written response questions)"
            )
        else:
            reasons.append("explanation is required")

    difficulty = normalize_difficulty(item.get("difficulty"))
    if difficulty is None:
        reasons.append(
            f"difficulty must be one of {'/'.join(VALID_DIFFICULTIES)}, "
            f"got '{item.get('difficulty')}'"
        )

    choices = item.get("choices", [])
    if not isinstance(choices, list):
        reasons.append("'choices' must be a list")
        return reasons

    if question_type == MULTIPLE_CHOICE:
        if not choices:
            reasons.append("multiple choice questions require 'choices'")
        else:
            _validate_choices(choices, reasons)
    else:
        # Numerical and written response questions have no answer choices.
        if choices:
            reasons.append(
                f"{question_type} questions must have empty 'choices', "
                f"got {len(choices)}"
            )
        answer = item.get("answer")
        if question_type == NUMERICAL_RESPONSE:
            # Auto short-answer: numeric canonical OR short non-empty text.
            if not isinstance(answer, str) or not answer.strip():
                reasons.append(
                    "numerical / short-answer questions need a non-empty 'answer'"
                )
            elif not is_numerical_answer(answer) and len(answer.strip()) > 80:
                reasons.append(
                    "non-numeric short answers must be brief "
                    f"(got {len(answer.strip())} characters)"
                )
            accepted = item.get("accepted_answers")
            if accepted is not None and not isinstance(accepted, list):
                reasons.append("'accepted_answers' must be a list when provided")
        elif not isinstance(answer, str) or not answer.strip():
            reasons.append(
                "written response questions need a non-empty 'answer' "
                "(the model solution)"
            )

    return reasons


def validate_file(items: list) -> tuple[int, list[tuple[int, str]]]:
    """Validate all items. Returns (valid_count, [(index, reason), ...])."""
    invalid: list[tuple[int, str]] = []
    seen_questions: set[tuple[str, str, str]] = set()
    valid_count = 0

    for index, item in enumerate(items):
        reasons = validate_question(item, index)

        if not reasons:
            key = (
                _normalize(item["course_code"]),
                _normalize(item["topic"]),
                _normalize(item["question_text"]),
            )
            if key in seen_questions:
                reasons.append("duplicate of an earlier question in this file")
            else:
                seen_questions.add(key)

        if reasons:
            for reason in reasons:
                invalid.append((index, reason))
        else:
            valid_count += 1

    return valid_count, invalid


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m app.database.question_validator <questions.json>")
        raise SystemExit(1)

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}")
        raise SystemExit(1)

    try:
        with path.open(encoding="utf-8") as f:
            items = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}")
        raise SystemExit(1)

    if not isinstance(items, list):
        print("The JSON file must contain a list of question objects.")
        raise SystemExit(1)

    valid_count, invalid = validate_file(items)
    invalid_indexes = {index for index, _ in invalid}

    print(f"Valid questions: {valid_count}")
    print(f"Invalid questions: {len(invalid_indexes)}")
    for index, reason in invalid:
        print(f"  - item {index}: {reason}")

    if invalid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
