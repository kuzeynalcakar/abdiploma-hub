from pydantic import BaseModel


class TopicProgress(BaseModel):
    topic_id: int
    topic_name: str
    questions_attempted: int
    questions_correct: int
    accuracy: float


class CourseProgress(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    quizzes_completed: int
    questions_answered: int
    correct_answers: int
    accuracy_percent: float
    strong_topics: list[TopicProgress]
    weak_topics: list[TopicProgress]


class LearningImpact(BaseModel):
    questions_completed: int = 0
    practice_sessions: int = 0
    subjects_practiced: int = 0
    daily_practice_sessions: int = 0
    overall_accuracy: float = 0.0
    strong_topics_count: int = 0
    topics_improved: int = 0
    weaknesses_identified: int = 0
    targeted_questions_completed: int = 0
    early_accuracy: float | None = None
    recent_accuracy: float | None = None
    accuracy_change: float | None = None


class ProgressResponse(BaseModel):
    courses: list[CourseProgress]
    practice_streak: int = 0
    last_practice_date: str | None = None
    impact: LearningImpact | None = None
