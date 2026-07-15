from datetime import date



import json



from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session, selectinload



from app.core.deps import get_current_user

from app.database.session import get_db

from app.models import Course, QuizAttempt, QuizAttemptQuestion, User

from app.schemas.daily_practice import (

    DailyPracticeStartResponse,

    DailyPracticeStatus,

    DailyPracticeTargetArea,

    DailyPracticeTopic,

)

from app.schemas.quiz import QuestionOut
from app.services.quiz_serialize import safe_questions_out

from app.services.daily_practice import (

    answered_count_for_attempt,

    daily_question_target,

    estimated_minutes,

    build_focus_message,
    get_target_areas,

    get_today_session,

    select_daily_questions,

    selection_metadata_from_attempt,

    topics_in_session,

    _has_practice_history,

)



router = APIRouter(prefix="/daily-practice", tags=["daily-practice"])





def _validate_course(db: Session, course_id: int) -> Course:

    course = (

        db.query(Course)

        .filter(Course.id == course_id, Course.is_active.is_(True))

        .first()

    )

    if course is None:

        raise HTTPException(status_code=404, detail="Course not found.")

    return course





def _status_for_session(

    db: Session,

    course: Course,

    user: User,

    today: date,

    session: QuizAttempt | None,

    preview_questions=None,

    preview_metadata: dict | None = None,

) -> DailyPracticeStatus:

    has_history = _has_practice_history(db, user.id, course.id)

    target_areas = [

        DailyPracticeTargetArea(**area)

        for area in get_target_areas(db, user.id, course.id)

    ]

    focus_message = build_focus_message([area.model_dump() for area in target_areas])



    if session is None:

        target = daily_question_target(db, course.id)

        questions = preview_questions or []

        metadata = preview_metadata or {}

        if not questions:

            questions, metadata = select_daily_questions(db, user.id, course.id)

        return DailyPracticeStatus(

            course_id=course.id,

            course_code=course.code,

            course_name=course.name,

            practice_date=today.isoformat(),

            total_questions=target or len(questions),

            completed_count=0,

            is_completed=False,

            is_started=False,

            estimated_time_minutes=estimated_minutes(questions),

            topics_included=[

                DailyPracticeTopic(**topic) for topic in topics_in_session(questions)

            ],

            target_areas=target_areas,

            focus_message=focus_message,

            quiz_attempt_id=None,

            has_history=has_history,

        )



    completed_count = answered_count_for_attempt(db, session.id)

    is_completed = session.completed_at is not None



    topics_included: list[DailyPracticeTopic] = []

    estimated_time = 15

    metadata = selection_metadata_from_attempt(session)

    if metadata.get("target_topics"):

        topics_included = [

            DailyPracticeTopic(

                topic_id=item["topic_id"],

                topic_name=item["topic_name"],

                question_count=item.get("question_count", 0),

            )

            for item in metadata["target_topics"]

        ]

    elif session.questions_total:

        estimated_time = max(1, round(session.questions_total * 2))



    return DailyPracticeStatus(

        course_id=course.id,

        course_code=course.code,

        course_name=course.name,

        practice_date=today.isoformat(),

        total_questions=session.questions_total,

        completed_count=completed_count,

        is_completed=is_completed,

        is_started=completed_count > 0 or is_completed,

        estimated_time_minutes=estimated_time,

        topics_included=topics_included,

        target_areas=target_areas,

        focus_message=focus_message,

        quiz_attempt_id=session.id,

        has_history=has_history,

    )





@router.get("", response_model=DailyPracticeStatus)

def get_daily_practice_status(

    course_id: int = Query(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    course = _validate_course(db, course_id)

    today = date.today()

    session = get_today_session(db, current_user.id, course_id, today)



    if session and session.completed_at is not None:

        return _status_for_session(db, course, current_user, today, session)



    if session and session.completed_at is None:

        status = _status_for_session(db, course, current_user, today, session)

        from app.models import Question



        attempt_questions = (

            db.query(QuizAttemptQuestion)

            .filter(QuizAttemptQuestion.quiz_attempt_id == session.id)

            .order_by(QuizAttemptQuestion.sort_order)

            .all()

        )

        if attempt_questions:

            question_ids = [aq.question_id for aq in attempt_questions]

            questions = (

                db.query(Question)

                .filter(Question.id.in_(question_ids))

                .options(selectinload(Question.topic))

                .all()

            )

            question_by_id = {q.id: q for q in questions}

            ordered = [

                question_by_id[qid]

                for qid in question_ids

                if qid in question_by_id

            ]

            if not status.topics_included:

                status.topics_included = [

                    DailyPracticeTopic(**topic)

                    for topic in topics_in_session(ordered)

                ]

            status.estimated_time_minutes = estimated_minutes(ordered)

        return status



    preview, metadata = select_daily_questions(db, current_user.id, course_id)

    return _status_for_session(

        db,

        course,

        current_user,

        today,

        None,

        preview_questions=preview,

        preview_metadata=metadata,

    )





@router.post("/start", response_model=DailyPracticeStartResponse)

def start_daily_practice(

    course_id: int = Query(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    course = _validate_course(db, course_id)

    today = date.today()

    existing = get_today_session(db, current_user.id, course_id, today)



    if existing is not None:

        if existing.completed_at is not None:

            raise HTTPException(

                status_code=400,

                detail="Today's daily practice is already complete. Come back tomorrow!",

            )

        answered = answered_count_for_attempt(db, existing.id)

        if answered > 0:

            raise HTTPException(

                status_code=400,

                detail="You already started today's practice. Resume from Daily Practice.",

            )

        db.delete(existing)

        db.flush()



    questions, metadata = select_daily_questions(db, current_user.id, course_id)

    if not questions:

        raise HTTPException(

            status_code=404,

            detail="No questions available for daily practice.",

        )



    attempt = QuizAttempt(

        user_id=current_user.id,

        course_id=course_id,

        topic_id=None,

        mode="daily_practice",

        practice_date=today,

        questions_total=len(questions),

        selection_metadata=json.dumps(metadata),

    )

    db.add(attempt)

    db.flush()



    for index, question in enumerate(questions):

        db.add(

            QuizAttemptQuestion(

                quiz_attempt_id=attempt.id,

                question_id=question.id,

                sort_order=index,

            )

        )



    db.commit()



    return DailyPracticeStartResponse(

        quiz_attempt_id=attempt.id,

        course_id=course_id,

        course_code=course.code,

        total_questions=len(questions),

        questions=safe_questions_out(questions),

    )





@router.get("/resume", response_model=DailyPracticeStartResponse)

def resume_daily_practice(

    course_id: int = Query(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    from app.models import Question



    course = _validate_course(db, course_id)

    today = date.today()

    session = get_today_session(db, current_user.id, course_id, today)



    if session is None or session.completed_at is not None:

        raise HTTPException(

            status_code=404,

            detail="No in-progress daily practice session found for today.",

        )



    attempt_questions = (

        db.query(QuizAttemptQuestion)

        .filter(QuizAttemptQuestion.quiz_attempt_id == session.id)

        .order_by(QuizAttemptQuestion.sort_order)

        .all()

    )



    if not attempt_questions:

        raise HTTPException(

            status_code=404,

            detail="Daily practice session has no questions stored.",

        )



    question_ids = [aq.question_id for aq in attempt_questions]

    questions = (

        db.query(Question)

        .filter(Question.id.in_(question_ids))

        .options(selectinload(Question.choices), selectinload(Question.topic))

        .all()

    )

    question_by_id = {q.id: q for q in questions}

    ordered = [question_by_id[qid] for qid in question_ids if qid in question_by_id]



    return DailyPracticeStartResponse(

        quiz_attempt_id=session.id,

        course_id=course_id,

        course_code=course.code,

        total_questions=len(ordered),

        questions=safe_questions_out(ordered),

    )

