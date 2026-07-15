from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models import User
from app.schemas.weakness_map import (
    NeedsPracticeTopic,
    StrongTopic,
    TopicSummary,
    TopicWeakness,
    WeaknessMapResponse,
)
from app.services.weakness_analysis import analyze_course_weakness

router = APIRouter(prefix="/weakness-map", tags=["weakness-map"])


def _to_response(payload: dict) -> WeaknessMapResponse:
    strongest = payload.get("strongest")
    weakest = payload.get("weakest")

    return WeaknessMapResponse(
        course_id=payload["course_id"],
        course_code=payload["course_code"],
        course_name=payload["course_name"],
        overall_accuracy=payload["overall_accuracy"],
        has_attempted_topics=payload["has_attempted_topics"],
        strong_topics=[
            StrongTopic(
                topic_id=item.topic_id,
                topic_name=item.topic_name,
                accuracy=item.accuracy,
                questions_attempted=item.questions_attempted,
                questions_correct=item.questions_correct,
                status=item.status,
            )
            for item in payload["strong_topics"]
        ],
        needs_practice=[
            NeedsPracticeTopic(
                topic_id=item.topic_id,
                topic_name=item.topic_name,
                accuracy=item.accuracy,
                questions_attempted=item.questions_attempted,
                questions_correct=item.questions_correct,
                weakness_score=item.weakness_score,
                recommended_action=item.recommended_action,
                why=item.why,
                status=item.status,
                mastery_level=item.mastery_level,
                mastery_label=item.mastery_label,
            )
            for item in payload["needs_practice"]
        ],
        strongest_topic=(
            TopicSummary(
                topic_id=strongest.topic_id,
                topic_name=strongest.topic_name,
                accuracy=strongest.accuracy,
                mastery_level=strongest.mastery_level,
            )
            if strongest
            else None
        ),
        weakest_topic=(
            TopicSummary(
                topic_id=weakest.topic_id,
                topic_name=weakest.topic_name,
                accuracy=weakest.accuracy,
                mastery_level=weakest.mastery_level,
            )
            if weakest
            else None
        ),
        mastered_topics_count=payload["mastered_topics_count"],
        weak_topics_count=payload["weak_topics_count"],
        topics=[
            TopicWeakness(
                topic_id=item.topic_id,
                topic_name=item.topic_name,
                questions_attempted=item.questions_attempted,
                questions_correct=item.questions_correct,
                accuracy=item.accuracy,
                confidence_level=item.confidence_level,
                mastery_level=item.mastery_level,
                mastery_label=item.mastery_label,
                status=item.status,
                weakness_score=item.weakness_score,
                why=item.why,
                recommended_action=item.recommended_action,
            )
            for item in payload["topics"]
        ],
    )


@router.get("", response_model=WeaknessMapResponse)
def get_weakness_map(
    course_id: int = Query(..., description="Course to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return data-driven weakness analysis from stored answer history."""
    payload = analyze_course_weakness(db, current_user.id, course_id)
    if payload.get("error") == "course_not_found":
        raise HTTPException(status_code=404, detail="Course not found.")
    return _to_response(payload)
