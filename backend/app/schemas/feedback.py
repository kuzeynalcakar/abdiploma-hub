from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


VALID_RATINGS = ("positive", "negative")
VALID_REPORT_REASONS = (
    "incorrect_answer",
    "confusing_wording",
    "wrong_explanation",
    "other",
)


class FeedbackCreate(BaseModel):
    course_id: int
    quiz_attempt_id: int | None = None
    rating: Literal["positive", "negative"]
    message: str | None = Field(None, max_length=2000)


class FeedbackOut(BaseModel):
    id: int
    course_id: int
    rating: str
    message: str | None
    created_at: datetime


class QuestionReportCreate(BaseModel):
    question_id: int
    reason: Literal[
        "incorrect_answer", "confusing_wording", "wrong_explanation", "other"
    ]
    comment: str | None = Field(None, max_length=2000)


class QuestionReportOut(BaseModel):
    id: int
    question_id: int
    reason: str
    comment: str | None
    created_at: datetime


class PlatformStats(BaseModel):
    students_helped: int
    questions_completed: int
    practice_sessions: int


class AdminFeedbackItem(BaseModel):
    id: int
    user_id: int | None
    course_id: int
    quiz_attempt_id: int | None
    rating: str
    message: str | None
    created_at: datetime
