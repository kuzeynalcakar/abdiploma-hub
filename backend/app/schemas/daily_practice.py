from pydantic import BaseModel





class DailyPracticeTopic(BaseModel):

    topic_id: int

    topic_name: str

    question_count: int = 0





class DailyPracticeTargetArea(BaseModel):

    topic_id: int

    topic_name: str

    accuracy: float

    weakness_score: float = 0.0





class DailyPracticeStatus(BaseModel):

    course_id: int

    course_code: str

    course_name: str

    practice_date: str

    total_questions: int

    completed_count: int

    is_completed: bool

    is_started: bool

    estimated_time_minutes: int

    topics_included: list[DailyPracticeTopic]

    target_areas: list[DailyPracticeTargetArea]

    focus_message: str = ""

    quiz_attempt_id: int | None

    has_history: bool





class DailyPracticeStartResponse(BaseModel):

    quiz_attempt_id: int

    course_id: int

    course_code: str

    total_questions: int

    questions: list

