from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Course, Question, Topic
from app.schemas.course import CourseListResponse, TopicListResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=CourseListResponse)
def list_courses(db: Session = Depends(get_db)):
    courses = (
        db.query(Course)
        .filter(Course.is_active.is_(True))
        .order_by(Course.code)
        .all()
    )

    # Playable questions per course (all active formats).
    counts = dict(
        db.query(Topic.course_id, func.count(Question.id))
        .join(Question, Question.topic_id == Topic.id)
        .filter(
            Question.is_active.is_(True),
        )
        .group_by(Topic.course_id)
        .all()
    )

    return {
        "courses": [
            {
                "id": course.id,
                "code": course.code,
                "name": course.name,
                "question_count": counts.get(course.id, 0),
            }
            for course in courses
        ]
    }


@router.get("/{course_id}/topics", response_model=TopicListResponse)
def list_topics(course_id: int, db: Session = Depends(get_db)):
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_active.is_(True))
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")

    topics = (
        db.query(Topic)
        .filter(Topic.course_id == course_id)
        .order_by(Topic.sort_order)
        .all()
    )
    return {"course_id": course_id, "topics": topics}
