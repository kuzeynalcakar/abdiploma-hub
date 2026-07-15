"""Shared helpers for building Physics 30 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "PHYS30"
SOURCE = "ai"

TOPIC_UNIT = {
    "Momentum and Impulse": "Momentum and Impulse",
    "Forces and Fields": "Forces and Fields",
    "Electromagnetic Radiation": "Electromagnetic Radiation",
    "Atomic Physics": "Atomic Physics",
}

VALID_OUTCOMES = {
    "Momentum and Impulse": {
        "A1.1k", "A1.2k", "A1.3k", "A1.4k", "A1.5k",
        "A1.1sts", "A1.1s", "A1.2s", "A1.3s", "A1.4s",
    },
    "Forces and Fields": {
        "B1.1k", "B1.2k", "B1.3k", "B1.4k", "B1.5k", "B1.6k", "B1.7k", "B1.8k",
        "B1.1sts", "B1.2sts", "B1.1s", "B1.2s", "B1.3s", "B1.4s",
        "B2.1k", "B2.2k", "B2.3k", "B2.4k", "B2.5k", "B2.6k", "B2.7k", "B2.8k",
        "B2.9k", "B2.10k", "B2.1sts", "B2.2sts", "B2.1s", "B2.2s", "B2.3s", "B2.4s",
        "B3.1k", "B3.2k", "B3.3k", "B3.4k", "B3.5k", "B3.6k", "B3.7k", "B3.8k", "B3.9k",
        "B3.1sts", "B3.2sts", "B3.3sts", "B3.1s", "B3.2s", "B3.3s", "B3.4s",
    },
    "Electromagnetic Radiation": {
        "C1.1k", "C1.2k", "C1.3k", "C1.4k", "C1.5k", "C1.6k", "C1.7k", "C1.8k",
        "C1.9k", "C1.10k", "C1.11k", "C1.12k",
        "C1.1sts", "C1.2sts", "C1.1s", "C1.2s", "C1.3s", "C1.4s",
        "C2.1k", "C2.2k", "C2.3k", "C2.4k", "C2.5k", "C2.6k",
        "C2.1sts", "C2.2sts", "C2.3sts", "C2.1s", "C2.2s", "C2.3s", "C2.4s",
    },
    "Atomic Physics": {
        "D1.1k", "D1.2k", "D1.3k", "D1.4k", "D1.1sts", "D1.1s", "D1.2s", "D1.3s", "D1.4s",
        "D2.1k", "D2.2k", "D2.3k", "D2.4k", "D2.5k", "D2.6k", "D2.7k",
        "D2.1sts", "D2.2sts", "D2.1s", "D2.2s", "D2.3s", "D2.4s",
        "D3.1k", "D3.2k", "D3.3k", "D3.4k", "D3.5k", "D3.6k",
        "D3.1sts", "D3.2sts", "D3.1s", "D3.2s", "D3.3s", "D3.4s",
        "D4.1k", "D4.2k", "D4.3k", "D4.4k", "D4.5k",
        "D4.1sts", "D4.2sts", "D4.3sts", "D4.1s", "D4.2s", "D4.3s", "D4.4s",
    },
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
