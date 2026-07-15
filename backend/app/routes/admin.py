"""Admin dashboard API routes — overview, reports, feedback, analytics, health."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.admin import require_admin
from app.core.security import utcnow
from app.database.session import get_db
from app.models import QuestionReport, User
from app.schemas.admin import (
    AdminAnalytics,
    AdminDbHealth,
    AdminFeedbackSummary,
    AdminImpact,
    AdminIntegrity,
    AdminOverview,
    AdminQuestionDetail,
    AdminQuestionQuality,
    AdminReliability,
    AdminReportList,
    ReportStatusUpdate,
)
from app.services import admin_stats
from app.services.admin_audit import log_admin_action
from app.services.integrity import run_integrity_audit

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverview)
def admin_overview(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.compute_overview(db)


@router.get("/reliability", response_model=AdminReliability)
def admin_reliability(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    """Operator metrics — counts and sanitized recent errors only."""
    return admin_stats.compute_reliability(db)


@router.get("/reports", response_model=AdminReportList)
def admin_reports(
    status: str | None = Query("all"),
    reason: str | None = Query("all"),
    search: str | None = Query(None),
    sort: str = Query("newest"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.list_reports(
        db,
        status=status,
        reason=reason,
        search=search,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.patch("/reports/{report_id}")
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    db: Session = Depends(get_db),
    admin: User | None = Depends(require_admin),
):
    row = db.get(QuestionReport, report_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found.")

    previous = getattr(row, "status", None) or "pending"
    row.status = payload.status
    row.status_changed_at = utcnow()
    if payload.admin_note is not None:
        note = payload.admin_note.strip()
        row.admin_note = note or None

    action_map = {
        "resolved": "report.resolve",
        "ignored": "report.ignore",
        "pending": "report.reopen",
    }
    log_admin_action(
        db,
        admin=admin,
        action=action_map.get(payload.status, "report.status_change"),
        entity_type="question_report",
        entity_id=row.id,
        detail={
            "from_status": previous,
            "to_status": payload.status,
            "question_id": row.question_id,
            "has_admin_note": bool(row.admin_note),
        },
    )
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "status": row.status,
        "status_changed_at": row.status_changed_at,
        "admin_note": row.admin_note,
        "question_id": row.question_id,
    }


@router.get("/question-quality", response_model=AdminQuestionQuality)
def admin_question_quality(
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.compute_question_quality(db, limit=limit)


@router.get("/questions/{question_id}", response_model=AdminQuestionDetail)
def admin_question_detail(
    question_id: int,
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    detail = admin_stats.get_question_detail(db, question_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    return detail


@router.get("/feedback", response_model=AdminFeedbackSummary)
def admin_feedback(
    limit: int = Query(100, ge=1, le=500),
    rating: str | None = Query("all"),
    unread_only: bool = Query(False),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    rating_filter = rating if rating in ("positive", "negative") else None
    return admin_stats.compute_feedback_summary(
        db,
        limit=limit,
        rating=rating_filter,
        unread_only=unread_only,
        since=since,
        until=until,
    )


@router.post("/feedback/{feedback_id}/review")
def mark_feedback_reviewed(
    feedback_id: int,
    db: Session = Depends(get_db),
    admin: User | None = Depends(require_admin),
):
    row = admin_stats.mark_feedback_reviewed(db, feedback_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    log_admin_action(
        db,
        admin=admin,
        action="feedback.mark_reviewed",
        entity_type="quiz_feedback",
        entity_id=row.id,
        detail={"rating": row.rating},
    )
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "is_unread": False,
        "admin_reviewed_at": row.admin_reviewed_at,
    }


@router.get("/analytics", response_model=AdminAnalytics)
def admin_analytics(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.compute_analytics(db)


@router.get("/health", response_model=AdminDbHealth)
def admin_db_health(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.compute_db_health(db)


@router.get("/integrity", response_model=AdminIntegrity)
def admin_integrity(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    """Orphan / relationship integrity audit (read-only)."""
    return run_integrity_audit(db)


@router.get("/impact", response_model=AdminImpact)
def admin_impact(
    db: Session = Depends(get_db),
    _admin: User | None = Depends(require_admin),
):
    return admin_stats.compute_impact(db)
