from datetime import date, datetime, timezone



from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session, selectinload



from app.core.deps import get_current_user

from app.database.session import get_db

from app.models import (

    AnswerChoice,

    Question,

    QuestionHistory,

    QuizAttempt,

    QuizAttemptQuestion,

    Topic,

    TopicPerformance,

    User,

    UserAnswer,

)

from app.schemas.answer import AnswerResult, AnswerSubmission, AttemptResults

from app.services.answer_grading import (

    MULTIPLE_CHOICE,

    NUMERICAL_RESPONSE,

    WRITTEN_RESPONSE,

    grade_answer,

)

from app.services.mastery import weakness_level_for
from app.services.practice_streak import update_practice_streak



router = APIRouter(prefix="/quiz", tags=["quiz"])





def _update_question_history(

    db: Session, user_id: int, question_id: int, grade

) -> None:

    now = datetime.now(timezone.utc)

    history = (

        db.query(QuestionHistory)

        .filter(

            QuestionHistory.user_id == user_id,

            QuestionHistory.question_id == question_id,

        )

        .first()

    )

    if history is None:

        history = QuestionHistory(

            user_id=user_id,

            question_id=question_id,

            times_attempted=0,

            times_correct=0,

            consecutive_correct=0,

        )

        db.add(history)



    history.times_attempted += 1

    if grade.auto_graded and grade.is_correct is True:

        history.times_correct += 1

        history.consecutive_correct += 1

        history.last_was_correct = True

    elif grade.auto_graded:

        history.consecutive_correct = 0

        history.last_was_correct = False

    history.last_answered_at = now





def _get_owned_attempt(

    db: Session, attempt_id: int, current_user: User

) -> QuizAttempt:

    attempt = db.get(QuizAttempt, attempt_id)

    if attempt is None:

        raise HTTPException(status_code=404, detail="Quiz attempt not found.")

    if attempt.user_id != current_user.id:

        raise HTTPException(

            status_code=403, detail="This quiz attempt belongs to another user."

        )

    return attempt





def _count_graded_correct(db: Session, attempt_id: int) -> int:

    answers = (

        db.query(UserAnswer)

        .filter(UserAnswer.quiz_attempt_id == attempt_id)

        .all()

    )

    return sum(

        1

        for answer in answers

        if answer.auto_graded and answer.is_correct is True

    )





@router.post("/answer", response_model=AnswerResult)

def submit_answer(

    submission: AnswerSubmission,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    attempt = _get_owned_attempt(db, submission.quiz_attempt_id, current_user)



    question = (

        db.query(Question)

        .options(selectinload(Question.choices))

        .filter(Question.id == submission.question_id)

        .first()

    )

    if question is None:

        raise HTTPException(status_code=404, detail="Question not found.")

    if question.topic.course_id != attempt.course_id:

        raise HTTPException(

            status_code=400,

            detail="Question does not belong to this attempt's course.",

        )

    if attempt.topic_id is not None and question.topic_id != attempt.topic_id:

        raise HTTPException(

            status_code=400,

            detail="Question does not belong to this attempt's topic.",

        )



    if attempt.mode == "daily_practice":

        in_attempt = (

            db.query(QuizAttemptQuestion)

            .filter(

                QuizAttemptQuestion.quiz_attempt_id == attempt.id,

                QuizAttemptQuestion.question_id == question.id,

            )

            .first()

        )

        if in_attempt is None:

            raise HTTPException(

                status_code=400,

                detail="Question is not part of this daily practice session.",

            )



    already_answered = (

        db.query(UserAnswer)

        .filter(

            UserAnswer.quiz_attempt_id == attempt.id,

            UserAnswer.question_id == question.id,

        )

        .first()

    )

    if already_answered is not None:

        raise HTTPException(

            status_code=400,

            detail="Question already answered in this attempt.",

        )



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



    db.add(

        UserAnswer(

            quiz_attempt_id=attempt.id,

            question_id=question.id,

            answer_choice_id=submission.answer_choice_id,

            response_text=submission.response_text,

            auto_graded=grade.auto_graded,

            is_correct=grade.is_correct,

        )

    )



    answered_count = (

        db.query(UserAnswer)

        .filter(UserAnswer.quiz_attempt_id == attempt.id)

        .count()

        + 1

    )

    if answered_count >= attempt.questions_total:

        correct_count = _count_graded_correct(db, attempt.id)

        if grade.auto_graded and grade.is_correct is True:

            correct_count += 1

        attempt.questions_correct = correct_count

        attempt.completed_at = datetime.now(timezone.utc)

        if attempt.mode == "daily_practice":
            update_practice_streak(current_user, date.today())



    performance = (

        db.query(TopicPerformance)

        .filter(

            TopicPerformance.user_id == attempt.user_id,

            TopicPerformance.topic_id == question.topic_id,

        )

        .first()

    )

    if performance is None:

        performance = TopicPerformance(

            user_id=attempt.user_id,

            topic_id=question.topic_id,

            questions_attempted=0,

            questions_correct=0,

        )

        db.add(performance)



    if grade.auto_graded:

        performance.questions_attempted += 1

        if grade.is_correct:

            performance.questions_correct += 1

        performance.accuracy = (

            performance.questions_correct / performance.questions_attempted * 100

        )

        performance.weakness_level = weakness_level_for(performance.accuracy)



    _update_question_history(db, attempt.user_id, question.id, grade)



    db.commit()



    return {

        "question_type": question.question_type,

        "is_correct": grade.is_correct,

        "auto_graded": grade.auto_graded,

        "requires_review": grade.requires_review,

        "correct_choice_id": grade.correct_choice_id,

        "expected_answer": grade.expected_answer,

        "explanation": question.explanation,

        "common_mistake": question.common_mistake,

        "attempt_progress": {

            "answered": answered_count,

            "total": attempt.questions_total,

            "completed": answered_count >= attempt.questions_total,

        },

    }





@router.get("/attempt/{attempt_id}/results", response_model=AttemptResults)

def get_attempt_results(

    attempt_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(get_current_user),

):

    """Score summary for one attempt, computed from stored answers."""

    attempt = _get_owned_attempt(db, attempt_id, current_user)



    answers = (

        db.query(UserAnswer)

        .filter(UserAnswer.quiz_attempt_id == attempt.id)

        .all()

    )

    answered = len(answers)

    correct = sum(

        1

        for answer in answers

        if answer.auto_graded and answer.is_correct is True

    )

    wrong = sum(

        1

        for answer in answers

        if answer.auto_graded and answer.is_correct is False

    )

    review_required = sum(1 for answer in answers if not answer.auto_graded)

    graded_total = correct + wrong

    total = attempt.questions_total

    score_percent = round(correct / graded_total * 100, 1) if graded_total else 0.0



    type_counts = {

        MULTIPLE_CHOICE: 0,

        NUMERICAL_RESPONSE: 0,

        WRITTEN_RESPONSE: 0,

    }

    by_topic: dict[int, dict] = {}



    for answer in answers:

        question = db.get(Question, answer.question_id)

        type_counts[question.question_type] = (

            type_counts.get(question.question_type, 0) + 1

        )



        entry = by_topic.setdefault(

            question.topic_id, {"correct": 0, "total": 0, "graded": 0}

        )

        if answer.auto_graded:

            entry["total"] += 1

            entry["graded"] += 1

            if answer.is_correct:

                entry["correct"] += 1



    topics = []

    for topic_id, entry in by_topic.items():

        topic = db.get(Topic, topic_id)

        graded = entry["graded"]

        accuracy = round(entry["correct"] / graded * 100, 1) if graded else 0.0

        topics.append(

            {

                "topic_id": topic_id,

                "topic_name": topic.name,

                "correct": entry["correct"],

                "total": entry["graded"],

                "accuracy": accuracy,

            }

        )

    topics.sort(key=lambda item: item["accuracy"])



    return {

        "quiz_attempt_id": attempt.id,

        "course_id": attempt.course_id,

        "total_questions": total,

        "answered": answered,

        "correct": correct,

        "wrong": wrong,

        "review_required": review_required,

        "score_percent": score_percent,

        "completed": attempt.completed_at is not None,

        "question_types": {

            "multiple_choice": type_counts.get(MULTIPLE_CHOICE, 0),

            "numerical_response": type_counts.get(NUMERICAL_RESPONSE, 0),

            "written_response": type_counts.get(WRITTEN_RESPONSE, 0),

        },

        "topics": topics,

    }


