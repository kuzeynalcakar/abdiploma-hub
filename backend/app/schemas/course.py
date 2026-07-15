from pydantic import BaseModel, ConfigDict


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    question_count: int = 0


class CourseListResponse(BaseModel):
    courses: list[CourseOut]


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class TopicListResponse(BaseModel):
    course_id: int
    topics: list[TopicOut]
