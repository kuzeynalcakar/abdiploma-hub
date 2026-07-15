from pydantic import BaseModel, Field, model_validator

MAX_RESPONSE_TEXT_LENGTH = 2000


class AnswerSubmission(BaseModel):
    quiz_attempt_id: int
    question_id: int
    answer_choice_id: int | None = None
    response_text: str | None = Field(None, max_length=MAX_RESPONSE_TEXT_LENGTH)

    @model_validator(mode="after")
    def validate_payload(self):
        has_choice = self.answer_choice_id is not None
        has_response = bool(
            self.response_text and self.response_text.strip()
        )
        if has_choice and has_response:
            raise ValueError(
                "Provide either answer_choice_id or response_text, not both."
            )
        if not has_choice and not has_response:
            raise ValueError("An answer is required.")
        return self


class AttemptProgress(BaseModel):
    answered: int
    total: int
    completed: bool


class AnswerResult(BaseModel):
    """Post-submit feedback fields intended by product design."""

    question_type: str
    is_correct: bool | None
    auto_graded: bool
    requires_review: bool
    correct_choice_id: int | None = None
    expected_answer: str | None = None
    explanation: str | None
    common_mistake: str | None
    attempt_progress: AttemptProgress


class QuestionTypeBreakdown(BaseModel):
    multiple_choice: int = 0
    numerical_response: int = 0
    written_response: int = 0


class TopicBreakdown(BaseModel):
    topic_id: int
    topic_name: str
    correct: int
    total: int
    accuracy: float


class AttemptResults(BaseModel):
    quiz_attempt_id: int
    course_id: int
    total_questions: int
    answered: int
    correct: int
    wrong: int
    review_required: int
    score_percent: float
    completed: bool
    question_types: QuestionTypeBreakdown
    topics: list[TopicBreakdown]

