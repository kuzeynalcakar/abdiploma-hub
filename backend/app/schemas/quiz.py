from pydantic import BaseModel, ConfigDict, Field


class TopicInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ChoiceOut(BaseModel):
    """Answer choice as exposed to the client. Deliberately has no
    is_correct field, so correctness can never leak into a response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    label: str = Field(validation_alias="choice_text")


class QuestionOut(BaseModel):
    """Safe question shape for quiz fetch — no answers or explanations."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    question_text: str
    question_type: str
    # Guides the answer control without revealing the key.
    # "numeric" → decimal short answer; "text" → free short answer.
    response_format: str = "numeric"
    unit: str | None
    difficulty: str | None
    topic: TopicInfo
    choices: list[ChoiceOut]


class AvailableCountResponse(BaseModel):
    course_id: int
    course_code: str
    available_count: int
    topic_ids: list[int]


class QuestionListResponse(BaseModel):
    quiz_attempt_id: int
    course_id: int
    course_code: str
    topic_id: int | None
    requested_count: int
    question_count: int
    available_count: int
    partial_fulfillment: bool = False
    questions: list[QuestionOut]


class GuestQuestionListResponse(QuestionListResponse):
    """Guest quiz fetch includes a signed token for subsequent grading."""

    guest_token: str

