"""Shared helpers for building Science 10 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "SCI10"
SOURCE = "ai"

TOPIC_UNIT = {
    "Energy and Matter in Chemical Change": "Energy and Matter in Chemical Change",
    "Energy Flow in Technological Systems": "Energy Flow in Technological Systems",
    "Cycling of Matter in Living Systems": "Cycling of Matter in Living Systems",
    "Energy Flow in Global Systems": "Energy Flow in Global Systems",
}

VALID_OUTCOMES = {
    "Energy and Matter in Chemical Change": {
        "A1.1k", "A1.2k", "A1.3k", "A1.1sts",
        "A2.1k", "A2.2k", "A2.3k", "A2.4k", "A2.5k", "A2.6k", "A2.7k", "A2.1sts",
        "A3.1k", "A3.2k", "A3.3k", "A3.4k", "A3.5k", "A3.6k", "A3.7k", "A3.8k", "A3.9k",
        "A1.1s", "A1.2s", "A1.3s", "A1.4s",
    },
    "Energy Flow in Technological Systems": {
        "B1.1k", "B1.2k", "B1.3k", "B1.4k", "B1.1sts",
        "B2.1k", "B2.2k", "B2.3k", "B2.4k", "B2.5k", "B2.6k", "B2.7k",
        "B2.8k", "B2.9k", "B2.10k", "B2.11k", "B2.12k",
        "B3.1k", "B3.2k", "B3.3k", "B3.4k", "B3.5k", "B3.6k", "B3.7k", "B3.8k", "B3.1sts",
        "B1.1s", "B1.2s", "B1.3s", "B1.4s",
    },
    "Cycling of Matter in Living Systems": {
        "C1.1k", "C1.2k", "C1.3k", "C1.1sts",
        "C2.1k", "C2.2k", "C2.3k", "C2.4k", "C2.5k", "C2.6k", "C2.7k", "C2.8k", "C2.9k",
        "C3.1k", "C3.2k", "C3.3k", "C3.4k", "C3.5k", "C3.6k", "C3.1sts",
        "C1.1s", "C1.2s", "C1.3s", "C1.4s",
    },
    "Energy Flow in Global Systems": {
        "D1.1k", "D1.2k", "D1.3k", "D1.4k", "D1.5k", "D1.1sts",
        "D2.1k", "D2.2k", "D2.3k", "D2.4k", "D2.5k", "D2.6k",
        "D3.1k", "D3.2k", "D3.3k", "D3.4k", "D3.1sts",
        "D4.1k", "D4.2k", "D4.3k", "D4.4k", "D4.5k", "D4.6k", "D4.1sts",
        "D1.1s", "D1.2s", "D1.3s", "D1.4s",
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
