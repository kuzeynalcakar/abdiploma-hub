from pydantic import BaseModel


class TopicWeakness(BaseModel):
    topic_id: int
    topic_name: str
    questions_attempted: int
    questions_correct: int
    accuracy: float
    confidence_level: str
    mastery_level: str
    mastery_label: str
    status: str
    weakness_score: float = 0.0
    why: str = ""
    recommended_action: str = ""


class StrongTopic(BaseModel):
    topic_id: int
    topic_name: str
    accuracy: float
    questions_attempted: int
    questions_correct: int
    status: str = "Strong"


class NeedsPracticeTopic(BaseModel):
    topic_id: int
    topic_name: str
    accuracy: float
    questions_attempted: int
    questions_correct: int
    weakness_score: float
    recommended_action: str
    why: str
    status: str = "Needs Practice"
    mastery_level: str
    mastery_label: str


class TopicSummary(BaseModel):
    topic_id: int
    topic_name: str
    accuracy: float
    mastery_level: str


class WeaknessMapResponse(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    overall_accuracy: float
    has_attempted_topics: bool
    strong_topics: list[StrongTopic]
    needs_practice: list[NeedsPracticeTopic]
    strongest_topic: TopicSummary | None
    weakest_topic: TopicSummary | None
    mastered_topics_count: int
    weak_topics_count: int
    topics: list[TopicWeakness]
