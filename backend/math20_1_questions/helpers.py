"""Shared helpers for building Mathematics 20-1 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "MATH20-1"
SOURCE = "ai"

TOPIC_UNIT = {
    "Sequences and Series": "Relations and Functions",
    "Trigonometry": "Trigonometry",
    "Quadratic Functions": "Relations and Functions",
    "Quadratic Equations": "Relations and Functions",
    "Radical Expressions and Equations": "Algebra and Number",
    "Rational Expressions and Equations": "Algebra and Number",
    "Absolute Value and Reciprocal Functions": "Relations and Functions",
    "Systems of Equations": "Relations and Functions",
    "Linear and Quadratic Inequalities": "Relations and Functions",
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
