from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.admin import require_admin
from app.core.deps import get_optional_user
from app.core.rate_limit import rate_limit_public
from app.database.session import get_db
from app.models import Course, Question, QuizAttempt, QuizFeedback, QuestionReport, User
from app.schemas.feedback import (
    AdminFeedbackItem,
    FeedbackCreate,
    FeedbackOut,
    PlatformStats,
    QuestionReportCreate,
    QuestionReportOut,
)
from app.services.platform_stats import compute_platform_stats

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackOut)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
    _: None = Depends(rate_limit_public),
):
    course = db.get(Course, payload.course_id)
    if course is None or not course.is_active:
        raise HTTPException(status_code=404, detail="Course not found.")

    if payload.quiz_attempt_id is not None:
        if current_user is None:
            raise HTTPException(
                status_code=401,
                detail="Log in to attach feedback to a quiz attempt.",
            )
        attempt = db.get(QuizAttempt, payload.quiz_attempt_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="Quiz attempt not found.")
        if attempt.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Attempt does not belong to you.")
        if attempt.course_id != payload.course_id:
            raise HTTPException(status_code=400, detail="Attempt course mismatch.")

    row = QuizFeedback(
        user_id=current_user.id if current_user else None,
        course_id=payload.course_id,
        quiz_attempt_id=payload.quiz_attempt_id,
        rating=payload.rating,
        message=payload.message.strip() if payload.message else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/question-reports", response_model=QuestionReportOut)
def report_question(
    payload: QuestionReportCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
    _: None = Depends(rate_limit_public),
):
    question = db.get(Question, payload.question_id)
    if question is None or not question.is_active:
        raise HTTPException(status_code=404, detail="Question not found.")

    row = QuestionReport(
        question_id=payload.question_id,
        user_id=current_user.id if current_user else None,
        reason=payload.reason,
        comment=payload.comment.strip() if payload.comment else None,
        status="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/stats/platform", response_model=PlatformStats)
def get_platform_stats(db: Session = Depends(get_db)):
    return compute_platform_stats(db)


@router.get("/feedback/admin", response_model=list[AdminFeedbackItem])
def list_feedback_admin(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    rows = (
        db.query(QuizFeedback)
        .order_by(QuizFeedback.created_at.desc())
        .limit(200)
        .all()
    )
    return rows
