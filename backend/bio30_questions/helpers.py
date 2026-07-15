"""Shared helpers for building Biology 30 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "BIO30"
SOURCE = "ai"

TOPIC_UNIT = {
    "Nervous and Endocrine Systems": "Nervous and Endocrine Systems",
    "Reproduction and Development": "Reproduction and Development",
    "Cell Division": "Cell Division, Genetics, and Molecular Biology",
    "Genetics and Molecular Biology": "Cell Division, Genetics, and Molecular Biology",
    "Population and Community Dynamics": "Population and Community Dynamics",
}


def mc(qtext, answer, distractors, explanation, mistake, *, topic, outcome_code,
       skill_tested, difficulty, estimated_time_seconds):
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


def wr(qtext, answer, explanation, mistake, *, topic, outcome_code,
       skill_tested, difficulty, estimated_time_seconds):
    return {
        "course_code": COURSE,
        "unit": TOPIC_UNIT[topic],
        "topic": topic,
        "outcome_code": outcome_code,
        "skill_tested": skill_tested,
        "question_type": "Written Response",
        "difficulty": difficulty,
        "estimated_time_seconds": estimated_time_seconds,
        "question_text": qtext,
        "answer": answer,
        "choices": [],
        "explanation": explanation,
        "common_mistake": mistake,
        "source": SOURCE,
    }
