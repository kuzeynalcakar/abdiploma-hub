"""Grade student answers for all Alberta question formats."""

from __future__ import annotations

from dataclasses import dataclass

from app.database.question_validator import is_numerical_answer
from app.models import AnswerChoice, Question
from app.services.short_answers import (
    coalesce_accepted_answers,
    normalize_short_answer,
)

MULTIPLE_CHOICE = "multiple_choice"
NUMERICAL_RESPONSE = "numerical_response"
WRITTEN_RESPONSE = "written_response"

NUMERICAL_TOLERANCE = 1e-4


@dataclass
class GradeResult:
    is_correct: bool | None
    auto_graded: bool
    requires_review: bool
    correct_choice_id: int | None = None
    expected_answer: str | None = None


def parse_numerical_value(value) -> float | None:
    """Parse a stored or submitted numeric answer."""
    if is_numerical_answer(value):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        text = str(value).strip().strip("$").strip()
        try:
            return float(text)
        except ValueError:
            return None
    return None


def numerical_values_match(submitted, expected) -> bool:
    submitted_value = parse_numerical_value(submitted)
    expected_value = parse_numerical_value(expected)
    if submitted_value is None or expected_value is None:
        return False
    if expected_value == 0:
        return abs(submitted_value - expected_value) <= NUMERICAL_TOLERANCE
    return (
        abs(submitted_value - expected_value)
        <= max(NUMERICAL_TOLERANCE, abs(expected_value) * 0.001)
    )


def expects_numeric_response(question: Question) -> bool:
    """True when every accepted answer is parseable as a number."""
    accepted = coalesce_accepted_answers(
        question.answer, getattr(question, "accepted_answers", None)
    )
    if not accepted:
        return True
    return all(parse_numerical_value(a) is not None for a in accepted)


def short_answers_match(submitted: str, expected: str) -> bool:
    if numerical_values_match(submitted, expected):
        return True
    return normalize_short_answer(submitted) == normalize_short_answer(expected)


def grade_multiple_choice(choice: AnswerChoice) -> GradeResult:
    return GradeResult(
        is_correct=choice.is_correct,
        auto_graded=True,
        requires_review=False,
        correct_choice_id=None,
    )


def grade_numerical_response(question: Question, response_text: str) -> GradeResult:
    if not response_text or not response_text.strip():
        raise ValueError("Short-answer response is required.")

    accepted = coalesce_accepted_answers(
        question.answer, getattr(question, "accepted_answers", None)
    )
    if not accepted:
        raise ValueError("Question has no expected answer configured.")

    numeric_only = expects_numeric_response(question)
    if numeric_only and not is_numerical_answer(response_text):
        raise ValueError("Numerical response must be a valid number.")

    is_correct = any(
        short_answers_match(response_text, expected) for expected in accepted
    )
    return GradeResult(
        is_correct=is_correct,
        auto_graded=True,
        requires_review=False,
        expected_answer=accepted[0],
    )


def grade_written_response(question: Question, response_text: str) -> GradeResult:
    """Legacy path — WR items should be converted to auto short-answer NR."""
    if not response_text or not response_text.strip():
        raise ValueError("Written response answer is required.")

    # If accepted answers exist (migration in progress), auto-grade as short answer.
    accepted = coalesce_accepted_answers(
        question.answer, getattr(question, "accepted_answers", None)
    )
    if accepted and len(accepted[0]) < 80 and "\n" not in accepted[0]:
        is_correct = any(
            short_answers_match(response_text, expected) for expected in accepted
        )
        return GradeResult(
            is_correct=is_correct,
            auto_graded=True,
            requires_review=False,
            expected_answer=accepted[0],
        )

    return GradeResult(
        is_correct=None,
        auto_graded=False,
        requires_review=True,
        expected_answer=question.answer,
    )


def grade_answer(
    question: Question,
    *,
    answer_choice: AnswerChoice | None = None,
    response_text: str | None = None,
) -> GradeResult:
    """Grade one submission for the question's format."""
    if question.question_type == MULTIPLE_CHOICE:
        if answer_choice is None:
            raise ValueError("Multiple choice questions require answer_choice_id.")
        if answer_choice.question_id != question.id:
            raise ValueError("Answer choice does not belong to this question.")
        result = grade_multiple_choice(answer_choice)
        correct_choice = next(
            (choice for choice in question.choices if choice.is_correct),
            None,
        )
        result.correct_choice_id = correct_choice.id if correct_choice else None
        return result

    if question.question_type == NUMERICAL_RESPONSE:
        return grade_numerical_response(question, response_text or "")

    if question.question_type == WRITTEN_RESPONSE:
        return grade_written_response(question, response_text or "")

    raise ValueError(f"Unsupported question type: {question.question_type}")
