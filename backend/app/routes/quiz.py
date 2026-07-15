from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.core.rate_limit import rate_limit_public
from app.database.session import get_db
from app.models import AnswerChoice, Question, QuizAttempt, User
from app.schemas.guest import GuestGradeRequest, GuestGradeResult
from app.schemas.quiz import AvailableCountResponse, QuestionListResponse, QuestionOut
from app.services.guest_quiz_session import require_guest_question, set_guest_quiz_cookie
from app.services.quiz_questions import fetch_quiz_questions, count_matching_questions
from app.services.quiz_serialize import safe_questions_out

router = APIRouter(prefix="/quiz", tags=["quiz"])

MAX_QUIZ_QUESTIONS = 50


def _quiz_response(
    course,
    questions: list,
    meta: dict,
    *,
    quiz_attempt_id: int,
    course_id: int,
    topic_id: int | None,
) -> dict:
    requested = meta["requested_count"]
    actual = meta["question_count"]
    return {
        "quiz_attempt_id": quiz_attempt_id,
        "course_id": course_id,
        "course_code": course.code,
        "topic_id": topic_id,
        "requested_count": requested,
        "question_count": actual,
        "available_count": meta["available_count"],
        "partial_fulfillment": actual < requested,
        "questions": questions,
    }


def _safe_questions(questions) -> list[QuestionOut]:
    """Serialize through QuestionOut so answer keys never leave the API."""
    return safe_questions_out(questions)


@router.get("/available-count", response_model=AvailableCountResponse)
def get_available_question_count(
    course_id: int,
    topic_ids: list[int] | None = Query(None),
    difficulty: str | None = None,
    db: Session = Depends(get_db),
):
    """Preview how many questions match the current quiz filters."""
    from app.services.quiz_questions import _validate_course

    course = _validate_course(db, course_id)
    available = count_matching_questions(
        db, course_id, topic_ids=topic_ids, difficulty=difficulty
    )
    return {
        "course_id": course_id,
        "course_code": course.code,
        "available_count": available,
        "topic_ids": topic_ids or [],
    }


@router.get("/questions", response_model=QuestionListResponse)
def get_quiz_questions(
    course_id: int,
    topic_id: int | None = None,
    topic_ids: list[int] | None = Query(None),
    difficulty: str | None = None,
    count: int = Query(10, ge=1, le=MAX_QUIZ_QUESTIONS),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course, questions, meta = fetch_quiz_questions(
        db,
        course_id,
        topic_id=topic_id,
        topic_ids=topic_ids,
        difficulty=difficulty,
        count=count,
    )

    stored_topic_id = topic_id
    if stored_topic_id is None and topic_ids and len(topic_ids) == 1:
        stored_topic_id = topic_ids[0]

    attempt = QuizAttempt(
        user_id=current_user.id,
        course_id=course_id,
        topic_id=stored_topic_id,
        mode="quiz",
        questions_total=meta["question_count"],
    )
    db.add(attempt)
    db.commit()

    return _quiz_response(
        course,
        _safe_questions(questions),
        meta,
        quiz_attempt_id=attempt.id,
        course_id=course_id,
        topic_id=stored_topic_id,
    )


@router.get("/guest/questions", response_model=QuestionListResponse)
def get_guest_quiz_questions(
    response: Response,
    course_id: int,
    topic_ids: list[int] | None = Query(None),
    difficulty: str | None = None,
    count: int = Query(10, ge=1, le=MAX_QUIZ_QUESTIONS),
    db: Session = Depends(get_db),
):
    """Public quiz questions for guests — no attempt persisted.

    Issues an HttpOnly cookie binding /guest/grade to these question IDs.
    """
    course, questions, meta = fetch_quiz_questions(
        db,
        course_id,
        topic_ids=topic_ids,
        difficulty=difficulty,
        count=count,
    )

    safe = _safe_questions(questions)
    set_guest_quiz_cookie(response, [q.id for q in safe])

    return _quiz_response(
        course,
        safe,
        meta,
        quiz_attempt_id=0,
        course_id=course_id,
        topic_id=None,
    )


@router.post("/guest/grade", response_model=GuestGradeResult)
def grade_guest_answer(
    request: Request,
    submission: GuestGradeRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_public),
):
    """Grade a guest answer. Requires cookie from /guest/questions."""
    from app.services.answer_grading import grade_answer

    require_guest_question(request, submission.question_id)

    question = (
        db.query(Question)
        .options(selectinload(Question.choices))
        .filter(Question.id == submission.question_id, Question.is_active.is_(True))
        .first()
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")

    choice = None
    if submission.answer_choice_id is not None:
        choice = db.get(AnswerChoice, submission.answer_choice_id)
        if choice is None or choice.question_id != question.id:
            raise HTTPException(status_code=404, detail="Answer choice not found.")

    try:
        grade = grade_answer(
            question,
            answer_choice=choice,
            response_text=submission.response_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "question_type": question.question_type,
        "is_correct": grade.is_correct,
        "auto_graded": grade.auto_graded,
        "requires_review": grade.requires_review,
        "correct_choice_id": grade.correct_choice_id,
        "expected_answer": grade.expected_answer,
        "explanation": question.explanation,
        "common_mistake": question.common_mistake,
    }
