"""Serialize questions for quiz clients without leaking answer keys."""

from __future__ import annotations

from app.schemas.quiz import QuestionOut
from app.services.answer_grading import expects_numeric_response


def safe_question_out(question) -> QuestionOut:
    payload = QuestionOut.model_validate(question)
    fmt = "numeric" if expects_numeric_response(question) else "text"
    return payload.model_copy(update={"response_format": fmt})


def safe_questions_out(questions) -> list[QuestionOut]:
    return [safe_question_out(q) for q in questions]
