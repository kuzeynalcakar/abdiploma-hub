"""Adaptive daily practice question selection."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models import Course, Question, QuestionHistory, QuizAttempt, Topic
from app.services.weakness_analysis import (
    STATUS_STRONG,
    TopicAnalysis,
    analyze_course_weakness,
)

DAILY_QUESTION_COUNT = 10

# 70% weak / 20% medium / 10% strong review
_TIER_ALLOCATION = [
    ("weak", 7),
    ("medium", 2),
    ("review", 1),
]

_RECENT_CORRECT_DAYS = 3
_REVIEW_AFTER_DAYS = 7
_MASTERED_STREAK = 3


def _normalize_difficulty(value: str | None) -> str:
    if not value:
        return "medium"
    lowered = value.strip().lower()
    if lowered in {"easy", "medium", "hard"}:
        return lowered
    return "medium"


def _difficulty_weights_for_accuracy(accuracy: float) -> dict[str, float]:
    if accuracy < 50:
        return {"easy": 0.55, "medium": 0.40, "hard": 0.05}
    if accuracy < 75:
        return {"easy": 0.15, "medium": 0.70, "hard": 0.15}
    return {"easy": 0.10, "medium": 0.45, "hard": 0.45}


def _classify_topics(
    analysis: dict,
) -> tuple[list[TopicAnalysis], list[TopicAnalysis], list[TopicAnalysis]]:
    weak = list(analysis["needs_practice"])
    strong = list(analysis["strong_topics"])

    weak_ids = {item.topic_id for item in weak}
    strong_ids = {item.topic_id for item in strong}

    medium: list[TopicAnalysis] = []
    for item in analysis["topics"]:
        if item.questions_attempted == 0:
            continue
        if item.topic_id in weak_ids or item.topic_id in strong_ids:
            continue
        if 50 <= item.accuracy < 75 or item.mastery_level == "improving":
            medium.append(item)

    medium.sort(key=lambda topic: (topic.accuracy, -topic.weakness_score))
    return weak, medium, strong


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _question_priority(
    history: QuestionHistory | None, now: datetime
) -> float:
    """Higher score = more likely to be selected."""
    if history is None or history.last_answered_at is None:
        return 55.0

    last_answered = _normalize_datetime(history.last_answered_at)
    now_aware = _normalize_datetime(now)
    days_since = max(0, (now_aware - last_answered).days)

    if history.last_was_correct is False:
        return max(70.0, 100.0 - days_since * 1.5)

    if history.consecutive_correct >= _MASTERED_STREAK:
        if days_since < _REVIEW_AFTER_DAYS:
            return 8.0
        if days_since < 14:
            return 22.0
        return 35.0

    if days_since < _RECENT_CORRECT_DAYS:
        return 12.0
    if days_since < _REVIEW_AFTER_DAYS:
        return 28.0
    return 42.0


def _weighted_sample(
    candidates: list[tuple[Question, float]], count: int
) -> list[Question]:
    pool = list(candidates)
    selected: list[Question] = []

    while pool and len(selected) < count:
        weights = [max(score, 1.0) for _, score in pool]
        total = sum(weights)
        pick = random.uniform(0, total)
        cumulative = 0.0
        chosen_index = 0
        for index, weight in enumerate(weights):
            cumulative += weight
            if pick <= cumulative:
                chosen_index = index
                break

        question, _ = pool.pop(chosen_index)
        selected.append(question)

    return selected


def _distribute_counts(
    topics: list[TopicAnalysis], total: int
) -> dict[int, int]:
    if total <= 0 or not topics:
        return {}

    if len(topics) >= total:
        return {topics[index].topic_id: 1 for index in range(total)}

    weights = [
        max(topic.weakness_score, 1.0) if topic.weakness_score else 1.0
        for topic in topics
    ]
    weight_sum = sum(weights)
    allocation = {
        topic.topic_id: max(1, round(total * weight / weight_sum))
        for topic, weight in zip(topics, weights)
    }

    while sum(allocation.values()) > total:
        richest = max(allocation, key=lambda key: allocation[key])
        if allocation[richest] > 1:
            allocation[richest] -= 1

    while sum(allocation.values()) < total:
        poorest = min(
            allocation,
            key=lambda key: (
                allocation[key],
                -next(t.weakness_score for t in topics if t.topic_id == key),
            ),
        )
        allocation[poorest] += 1

    return allocation


def _questions_for_topic(
    db: Session,
    user_id: int,
    topic: TopicAnalysis,
    count: int,
    exclude_ids: set[int],
    now: datetime,
) -> list[Question]:
    if count <= 0:
        return []

    questions = (
        db.query(Question)
        .filter(
            Question.topic_id == topic.topic_id,
            Question.is_active.is_(True),
            ~Question.id.in_(exclude_ids) if exclude_ids else True,
        )
        .options(selectinload(Question.choices), selectinload(Question.topic))
        .all()
    )
    if not questions:
        return []

    histories = {
        history.question_id: history
        for history in db.query(QuestionHistory)
        .filter(
            QuestionHistory.user_id == user_id,
            QuestionHistory.question_id.in_([question.id for question in questions]),
        )
        .all()
    }

    difficulty_weights = _difficulty_weights_for_accuracy(topic.accuracy)
    candidates: list[tuple[Question, float]] = []
    for question in questions:
        difficulty = _normalize_difficulty(question.difficulty)
        history_score = _question_priority(histories.get(question.id), now)
        difficulty_boost = difficulty_weights.get(difficulty, 0.33) * 100
        candidates.append((question, history_score + difficulty_boost))

    return _weighted_sample(candidates, count)


def _questions_for_tier(
    db: Session,
    user_id: int,
    topics: list[TopicAnalysis],
    count: int,
    exclude_ids: set[int],
    now: datetime,
) -> list[Question]:
    if count <= 0 or not topics:
        return []

    allocation = _distribute_counts(topics, count)
    selected: list[Question] = []

    for topic in topics:
        needed = allocation.get(topic.topic_id, 0)
        if needed <= 0:
            continue
        picked = _questions_for_topic(
            db, user_id, topic, needed, exclude_ids, now
        )
        for question in picked:
            if question.id not in exclude_ids:
                selected.append(question)
                exclude_ids.add(question.id)

    return selected[:count]


def _random_questions(
    db: Session,
    course_id: int,
    count: int,
    exclude_ids: set[int],
) -> list[Question]:
    query = (
        db.query(Question)
        .join(Topic, Question.topic_id == Topic.id)
        .filter(
            Topic.course_id == course_id,
            Question.is_active.is_(True),
        )
        .options(selectinload(Question.choices), selectinload(Question.topic))
    )
    if exclude_ids:
        query = query.filter(~Question.id.in_(exclude_ids))

    questions = query.all()
    if len(questions) <= count:
        return questions
    return random.sample(questions, count)


def _has_practice_history(db: Session, user_id: int, course_id: int) -> bool:
    analysis = analyze_course_weakness(db, user_id, course_id)
    return analysis["has_attempted_topics"]


def available_question_count(db: Session, course_id: int) -> int:
    return (
        db.query(Question)
        .join(Topic, Question.topic_id == Topic.id)
        .filter(
            Topic.course_id == course_id,
            Question.is_active.is_(True),
        )
        .count()
    )


def daily_question_target(db: Session, course_id: int) -> int:
    available = available_question_count(db, course_id)
    if available == 0:
        return 0
    return min(DAILY_QUESTION_COUNT, available)


def build_focus_message(target_areas: list[dict]) -> str:
    if not target_areas:
        return ""
    if len(target_areas) == 1:
        topic = target_areas[0]["topic_name"]
        return (
            f"Today's practice focuses on {topic} because this is your weakest topic."
        )
    names = [area["topic_name"] for area in target_areas[:2]]
    if len(names) == 2:
        return (
            f"Today's practice focuses on {names[0]} and {names[1]} "
            "because these are your weakest topics."
        )
    return (
        f"Today's practice focuses on {names[0]}, {names[1]}, and more "
        "based on your weakest areas."
    )


def get_target_areas(
    db: Session, user_id: int, course_id: int, limit: int = 3
) -> list[dict]:
    """Top weak topics to display before starting daily practice."""
    analysis = analyze_course_weakness(db, user_id, course_id)
    areas = []
    for topic in analysis["needs_practice"][:limit]:
        areas.append(
            {
                "topic_id": topic.topic_id,
                "topic_name": topic.topic_name,
                "accuracy": topic.accuracy,
                "weakness_score": topic.weakness_score,
            }
        )
    return areas


def build_selection_metadata(
    weak: list[TopicAnalysis],
    medium: list[TopicAnalysis],
    strong: list[TopicAnalysis],
    questions: list[Question],
) -> dict:
    topic_tier: dict[int, str] = {}
    for topic in weak:
        topic_tier[topic.topic_id] = "weak"
    for topic in medium:
        topic_tier[topic.topic_id] = "medium"
    for topic in strong:
        topic_tier[topic.topic_id] = "review"

    counts: dict[int, dict] = {}
    for question in questions:
        entry = counts.setdefault(
            question.topic_id,
            {
                "topic_id": question.topic_id,
                "topic_name": question.topic.name,
                "tier": topic_tier.get(question.topic_id, "mixed"),
                "question_count": 0,
            },
        )
        entry["question_count"] += 1

    return {
        "allocation": {
            "weak": _TIER_ALLOCATION[0][1],
            "medium": _TIER_ALLOCATION[1][1],
            "review": _TIER_ALLOCATION[2][1],
        },
        "target_topics": sorted(
            counts.values(), key=lambda item: item["topic_name"]
        ),
        "practice_date": date.today().isoformat(),
    }


def select_daily_questions(
    db: Session,
    user_id: int,
    course_id: int,
    count: int | None = None,
) -> tuple[list[Question], dict]:
    """Build today's adaptive question set and selection metadata."""
    if count is None:
        count = daily_question_target(db, course_id)
    if count <= 0:
        return [], {}

    now = datetime.now(timezone.utc)
    analysis = analyze_course_weakness(db, user_id, course_id)
    weak, medium, strong = _classify_topics(analysis)

    if not analysis["has_attempted_topics"]:
        questions = _random_questions(db, course_id, count, set())
        metadata = {
            "allocation": {"weak": 0, "medium": 0, "review": 0},
            "target_topics": topics_in_session(questions),
            "practice_date": date.today().isoformat(),
            "cold_start": True,
        }
        random.shuffle(questions)
        return questions[:count], metadata

    selected: list[Question] = []
    exclude_ids: set[int] = set()

    tier_topics = {
        "weak": weak,
        "medium": medium,
        "review": strong,
    }

    for tier_name, tier_count in _TIER_ALLOCATION:
        topics = tier_topics[tier_name]
        if not topics and tier_name == "medium":
            topics = [
                item
                for item in analysis["topics"]
                if item.questions_attempted > 0
                and item.status != STATUS_STRONG
                and item.topic_id not in {t.topic_id for t in weak}
            ][:3]
        if not topics and tier_name == "review":
            topics = [
                item
                for item in analysis["topics"]
                if item.questions_attempted > 0 and item.accuracy >= 60
            ][:2]

        picked = _questions_for_tier(
            db, user_id, topics, tier_count, exclude_ids, now
        )
        selected.extend(picked)

    if len(selected) < count:
        fallback_topics = weak or medium or [
            item for item in analysis["topics"] if item.questions_attempted > 0
        ]
        extra = _questions_for_tier(
            db,
            user_id,
            fallback_topics,
            count - len(selected),
            exclude_ids,
            now,
        )
        selected.extend(extra)

    if len(selected) < count:
        extra = _random_questions(
            db, course_id, count - len(selected), exclude_ids
        )
        selected.extend(extra)

    random.shuffle(selected)
    questions = selected[:count]
    metadata = build_selection_metadata(weak, medium, strong, questions)
    return questions, metadata


def topics_in_session(questions: list[Question]) -> list[dict]:
    counts: dict[int, dict] = {}
    for question in questions:
        entry = counts.setdefault(
            question.topic_id,
            {
                "topic_id": question.topic_id,
                "topic_name": question.topic.name,
                "question_count": 0,
            },
        )
        entry["question_count"] += 1
    return sorted(counts.values(), key=lambda item: item["topic_name"])


def estimated_minutes(questions: list[Question]) -> int:
    seconds = sum(question.estimated_time_seconds or 120 for question in questions)
    return max(1, round(seconds / 60))


def get_today_session(
    db: Session, user_id: int, course_id: int, today: date
) -> QuizAttempt | None:
    return (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.course_id == course_id,
            QuizAttempt.mode == "daily_practice",
            QuizAttempt.practice_date == today,
        )
        .order_by(QuizAttempt.id.desc())
        .first()
    )


def answered_count_for_attempt(db: Session, attempt_id: int) -> int:
    from app.models import UserAnswer

    return (
        db.query(UserAnswer)
        .filter(UserAnswer.quiz_attempt_id == attempt_id)
        .count()
    )


def selection_metadata_from_attempt(attempt: QuizAttempt | None) -> dict:
    if attempt is None or not attempt.selection_metadata:
        return {}
    try:
        return json.loads(attempt.selection_metadata)
    except json.JSONDecodeError:
        return {}
