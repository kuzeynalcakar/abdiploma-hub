"""Data-driven weakness analysis from stored student answer history."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import Course, Question, QuestionHistory, Topic, UserAnswer
from app.services.mastery import (
    confidence_level_for,
    mastery_label,
    mastery_level_for,
)

STRONG_ACCURACY_THRESHOLD = 75.0
RECENT_WINDOW = 12
MIN_ATTEMPTS_FOR_STRONG = 3

DIFFICULTY_WEIGHT = {
    "easy": 1.0,
    "medium": 1.5,
    "hard": 2.0,
}

STATUS_STRONG = "Strong"
STATUS_NEEDS_PRACTICE = "Needs Practice"


@dataclass
class AnswerRecord:
    topic_id: int
    topic_name: str
    outcome_code: str | None
    skill_tested: str | None
    difficulty: str | None
    is_correct: bool
    answered_at: object


@dataclass
class TopicAnalysis:
    topic_id: int
    topic_name: str
    questions_attempted: int = 0
    questions_correct: int = 0
    accuracy: float = 0.0
    status: str = STATUS_NEEDS_PRACTICE
    weakness_score: float = 0.0
    recent_wrong: int = 0
    recent_total: int = 0
    why: str = ""
    recommended_action: str = ""
    mastery_level: str = "not_attempted"
    mastery_label: str = "Not Attempted"
    confidence_level: str = "not_attempted"
    outcome_accuracy: dict[str, float] = field(default_factory=dict)
    difficulty_performance: dict[str, dict[str, float | int]] = field(
        default_factory=dict
    )
    repeat_mistakes: int = 0


def _normalize_difficulty(value: str | None) -> str:
    if not value:
        return "medium"
    lowered = value.strip().lower()
    if lowered in DIFFICULTY_WEIGHT:
        return lowered
    return "medium"


def compute_weakness_score(
    *,
    accuracy: float,
    recent_wrong: int,
    recent_total: int,
    hard_attempted: int,
    hard_wrong: int,
    repeat_mistakes: int,
) -> float:
    """Higher score means higher practice priority (0–100 scale)."""
    accuracy_penalty = (100.0 - accuracy) / 100.0

    recent_penalty = (
        recent_wrong / recent_total if recent_total > 0 else accuracy_penalty
    )

    hard_penalty = (
        hard_wrong / hard_attempted if hard_attempted > 0 else 0.0
    )

    repeat_penalty = min(repeat_mistakes / 5.0, 1.0)

    score = (
        accuracy_penalty * 40.0
        + recent_penalty * 30.0
        + hard_penalty * 20.0
        + repeat_penalty * 10.0
    )
    return round(min(max(score, 0.0), 100.0), 1)


def _weakest_skill(answers: list[AnswerRecord]) -> str | None:
    """Return the skill area with the most recent wrong answers."""
    skill_wrong: dict[str, int] = defaultdict(int)
    skill_total: dict[str, int] = defaultdict(int)

    for answer in answers:
        skill = getattr(answer, "skill_tested", None)
        if not skill:
            continue
        skill = skill.strip()
        skill_total[skill] += 1
        if not answer.is_correct:
            skill_wrong[skill] += 1

    if not skill_wrong:
        return None

    return max(
        skill_wrong,
        key=lambda skill: (skill_wrong[skill], skill_wrong[skill] / skill_total[skill]),
    )


def build_why_message(
    recent_wrong: int,
    recent_total: int,
    *,
    weakest_skill: str | None = None,
    repeat_mistakes: int = 0,
) -> str:
    if weakest_skill:
        skill = weakest_skill.strip().rstrip(".")
        if skill.lower().startswith("solving "):
            skill = skill[8:]
        return f"You are struggling with {skill.lower()}"
    if repeat_mistakes >= 2:
        return "You keep missing the same types of questions in this topic"
    if recent_total <= 0:
        return "Complete more questions in this topic to refine recommendations."
    return f"You missed {recent_wrong} of your last {recent_total} questions"


def build_recommended_action(
    *,
    accuracy: float,
    weakest_difficulty: str,
) -> str:
    if accuracy < 50:
        return "Practice 10 easy questions"
    if accuracy < 75:
        return "Practice 10 targeted questions"
    return f"Practice 10 {weakest_difficulty} questions"


def _fetch_answer_records(
    db: Session, user_id: int, course_id: int
) -> list[AnswerRecord]:
    from app.models import QuizAttempt

    rows = (
        db.query(UserAnswer, Question, Topic)
        .join(Question, UserAnswer.question_id == Question.id)
        .join(Topic, Question.topic_id == Topic.id)
        .join(QuizAttempt, UserAnswer.quiz_attempt_id == QuizAttempt.id)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.course_id == course_id,
            UserAnswer.auto_graded.is_(True),
        )
        .order_by(UserAnswer.answered_at.desc())
        .all()
    )

    return [
        AnswerRecord(
            topic_id=topic.id,
            topic_name=topic.name,
            outcome_code=question.outcome_code,
            skill_tested=question.skill_tested,
            difficulty=question.difficulty,
            is_correct=answer.is_correct is True,
            answered_at=answer.answered_at,
        )
        for answer, question, topic in rows
    ]


def _fetch_repeat_mistakes_by_topic(
    db: Session, user_id: int, course_id: int
) -> dict[int, int]:
    rows = (
        db.query(QuestionHistory, Question, Topic)
        .join(Question, QuestionHistory.question_id == Question.id)
        .join(Topic, Question.topic_id == Topic.id)
        .filter(
            QuestionHistory.user_id == user_id,
            Topic.course_id == course_id,
            QuestionHistory.times_attempted > 1,
            QuestionHistory.times_correct < QuestionHistory.times_attempted,
        )
        .all()
    )

    counts: dict[int, int] = defaultdict(int)
    for _history, _question, topic in rows:
        counts[topic.id] += 1
    return dict(counts)


def _accuracy(correct: int, attempted: int) -> float:
    if attempted <= 0:
        return 0.0
    return round(correct / attempted * 100.0, 1)


def _analyze_topic(
    topic: Topic,
    answers: list[AnswerRecord],
    repeat_mistakes: int,
) -> TopicAnalysis:
    attempted = len(answers)
    correct = sum(1 for answer in answers if answer.is_correct)
    accuracy = _accuracy(correct, attempted)

    recent = answers[:RECENT_WINDOW]
    recent_total = len(recent)
    recent_wrong = sum(1 for answer in recent if not answer.is_correct)

    hard_attempted = 0
    hard_wrong = 0
    difficulty_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"attempted": 0, "correct": 0}
    )
    outcome_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"attempted": 0, "correct": 0}
    )

    for answer in answers:
        difficulty = _normalize_difficulty(answer.difficulty)
        difficulty_stats[difficulty]["attempted"] += 1
        if answer.is_correct:
            difficulty_stats[difficulty]["correct"] += 1

        if difficulty == "hard":
            hard_attempted += 1
            if not answer.is_correct:
                hard_wrong += 1

        code = answer.outcome_code or "unknown"
        outcome_stats[code]["attempted"] += 1
        if answer.is_correct:
            outcome_stats[code]["correct"] += 1

    difficulty_performance = {
        key: {
            "attempted": stats["attempted"],
            "correct": stats["correct"],
            "accuracy": _accuracy(stats["correct"], stats["attempted"]),
        }
        for key, stats in difficulty_stats.items()
    }

    outcome_accuracy = {
        code: _accuracy(stats["correct"], stats["attempted"])
        for code, stats in outcome_stats.items()
    }

    weakest_difficulty = "medium"
    if difficulty_performance:
        weakest_difficulty = min(
            difficulty_performance,
            key=lambda key: (
                difficulty_performance[key]["accuracy"],
                -difficulty_performance[key]["attempted"],
            ),
        )

    weakness_score = compute_weakness_score(
        accuracy=accuracy,
        recent_wrong=recent_wrong,
        recent_total=recent_total,
        hard_attempted=hard_attempted,
        hard_wrong=hard_wrong,
        repeat_mistakes=repeat_mistakes,
    )

    mastery_level = mastery_level_for(accuracy, attempted)
    is_strong = (
        attempted >= MIN_ATTEMPTS_FOR_STRONG
        and accuracy >= STRONG_ACCURACY_THRESHOLD
    )

    recent_wrong_answers = [a for a in recent if not a.is_correct]
    weakest_skill = _weakest_skill(recent_wrong_answers or answers)

    return TopicAnalysis(
        topic_id=topic.id,
        topic_name=topic.name,
        questions_attempted=attempted,
        questions_correct=correct,
        accuracy=accuracy,
        status=STATUS_STRONG if is_strong else STATUS_NEEDS_PRACTICE,
        weakness_score=weakness_score,
        recent_wrong=recent_wrong,
        recent_total=recent_total,
        why=build_why_message(
            recent_wrong,
            recent_total,
            weakest_skill=weakest_skill,
            repeat_mistakes=repeat_mistakes,
        ),
        recommended_action=build_recommended_action(
            accuracy=accuracy,
            weakest_difficulty=weakest_difficulty,
        ),
        mastery_level=mastery_level,
        mastery_label=mastery_label(mastery_level),
        confidence_level=confidence_level_for(attempted),
        outcome_accuracy=outcome_accuracy,
        difficulty_performance=difficulty_performance,
        repeat_mistakes=repeat_mistakes,
    )


def analyze_course_weakness(
    db: Session, user_id: int, course_id: int
) -> dict:
    """Build weakness map payload from answer history for one course."""
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_active.is_(True))
        .first()
    )
    if course is None:
        return {"error": "course_not_found"}

    topics = (
        db.query(Topic)
        .filter(Topic.course_id == course_id)
        .order_by(Topic.sort_order)
        .all()
    )

    answer_records = _fetch_answer_records(db, user_id, course_id)
    repeat_by_topic = _fetch_repeat_mistakes_by_topic(db, user_id, course_id)

    answers_by_topic: dict[int, list[AnswerRecord]] = defaultdict(list)
    for record in answer_records:
        answers_by_topic[record.topic_id].append(record)

    analyses: list[TopicAnalysis] = []
    for topic in topics:
        topic_answers = answers_by_topic.get(topic.id, [])
        analyses.append(
            _analyze_topic(
                topic,
                topic_answers,
                repeat_by_topic.get(topic.id, 0),
            )
        )

    attempted_analyses = [
        analysis for analysis in analyses if analysis.questions_attempted > 0
    ]

    strong_topics = sorted(
        [
            analysis
            for analysis in attempted_analyses
            if analysis.status == STATUS_STRONG
        ],
        key=lambda item: item.accuracy,
        reverse=True,
    )

    needs_practice = sorted(
        [
            analysis
            for analysis in attempted_analyses
            if analysis.status == STATUS_NEEDS_PRACTICE
        ],
        key=lambda item: item.weakness_score,
        reverse=True,
    )

    total_attempted = sum(item.questions_attempted for item in attempted_analyses)
    total_correct = sum(item.questions_correct for item in attempted_analyses)
    overall_accuracy = _accuracy(total_correct, total_attempted)

    strongest = strong_topics[0] if strong_topics else None
    weakest = needs_practice[0] if needs_practice else None

    from app.services.mastery import MASTERED_LEVELS, WEAK_LEVELS

    mastered_count = sum(
        1 for item in attempted_analyses if item.mastery_level in MASTERED_LEVELS
    )
    weak_count = sum(
        1 for item in attempted_analyses if item.mastery_level in WEAK_LEVELS
    )

    return {
        "course_id": course.id,
        "course_code": course.code,
        "course_name": course.name,
        "overall_accuracy": overall_accuracy,
        "strong_topics": strong_topics,
        "needs_practice": needs_practice,
        "topics": analyses,
        "strongest": strongest,
        "weakest": weakest,
        "mastered_topics_count": mastered_count,
        "weak_topics_count": weak_count,
        "has_attempted_topics": len(attempted_analyses) > 0,
    }
