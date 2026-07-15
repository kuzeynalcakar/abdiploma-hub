"""Shared helpers for Social Studies 30-1 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "SOC30-1"
SOURCE = "ai"

TOPIC_UNIT = {
    "Ideology and Identity": "Related Issue 1",
    "Origins of Liberalism": "Related Issue 2 (origins)",
    "Resistance to Liberalism": "Related Issue 2 (resistance)",
    "The Viability of Contemporary Liberalism": "Related Issue 3",
    "Citizenship and Ideology": "Related Issue 4",
}


def mc(
    qtext,
    answer,
    distractors,
    explanation,
    mistake,
    *,
    topic,
    outcome_code,
    skill_tested,
    difficulty,
    estimated_time_seconds,
):
    choices = [{"text": answer, "is_correct": True}]
    for d in distractors:
        choices.append({"text": d, "is_correct": False})
    choices = shuffle_mc_choices(choices)
    if len(choices) != 4:
        raise ValueError(f"MC requires 4 choices, got {len(choices)}: {qtext[:60]}")
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


def nr(
    qtext,
    answer,
    explanation,
    mistake,
    *,
    topic,
    outcome_code,
    skill_tested,
    difficulty,
    estimated_time_seconds,
):
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
