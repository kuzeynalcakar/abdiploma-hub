"""Shared helpers for building Mathematics 30-2 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "MATH30-2"
SOURCE = "ai"

TOPIC_UNIT = {
    "Set Theory and Logic": "Logical Reasoning",
    "Counting Methods": "Probability",
    "Probability": "Probability",
    "Rational Expressions and Equations": "Relations and Functions",
    "Polynomial Functions": "Relations and Functions",
    "Exponential and Logarithmic Functions": "Relations and Functions",
    "Sinusoidal Functions": "Relations and Functions",
}

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def mc(qtext, answer, distractors, explanation, mistake, *, topic, outcome_code,
       skill_tested, difficulty, estimated_time_seconds):
    if len(distractors) != 3:
        raise ValueError("MC questions require exactly 3 distractors")
    choices = [{"text": answer, "is_correct": True}]
    for d in distractors:
        choices.append({"text": d, "is_correct": False})
    choices = shuffle_mc_choices(choices)
    return {
        "course_code": COURSE,
        "unit": TOPIC_UNIT[topic],
        "topic": topic,
        "outcome_code": outcome_code,
        "skill_tested": skill_tested,
        "question_type": "Multiple Choice",
        "difficulty": difficulty,
        "estimated_time_seconds": estimated_time_seconds,
        "question_text": qtext,
        "answer": answer,
        "choices": choices,
        "explanation": explanation,
        "common_mistake": mistake,
        "source": SOURCE,
    }


def nr(qtext, answer, explanation, mistake, *, topic, outcome_code,
       skill_tested, difficulty, estimated_time_seconds):
    return {
        "course_code": COURSE,
        "unit": TOPIC_UNIT[topic],
        "topic": topic,
        "outcome_code": outcome_code,
        "skill_tested": skill_tested,
        "question_type": "Numerical Response",
        "difficulty": difficulty,
        "estimated_time_seconds": estimated_time_seconds,
        "question_text": qtext,
        "answer": str(answer),
        "choices": [],
        "explanation": explanation,
        "common_mistake": mistake,
        "source": SOURCE,
    }
