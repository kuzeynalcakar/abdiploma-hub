"""Shared helpers for building Chemistry 30 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "CHEM30"
SOURCE = "ai"

TOPIC_UNIT = {
    "Thermochemical Changes": "Thermochemical Changes",
    "Electrochemical Changes": "Electrochemical Changes",
    "Chemical Changes of Organic Compounds": "Chemical Changes of Organic Compounds",
    "Chemical Equilibrium Focusing on Acid-Base Systems": (
        "Chemical Equilibrium Focusing on Acid-Base Systems"
    ),
}

VALID_OUTCOMES = {
    "Thermochemical Changes": {
        "A1.1k", "A1.2k", "A1.3k", "A1.4k", "A1.5k", "A1.6k", "A1.7k", "A1.8k",
        "A1.9k", "A1.10k", "A1.1sts", "A1.2sts", "A1.1s", "A1.2s", "A1.3s", "A1.4s",
        "A2.1k", "A2.2k", "A2.3k", "A2.4k", "A2.1sts", "A2.2sts", "A2.3sts",
        "A2.1s", "A2.2s", "A2.3s", "A2.4s",
    },
    "Electrochemical Changes": {
        "B1.1k", "B1.2k", "B1.3k", "B1.4k", "B1.5k", "B1.6k", "B1.7k", "B1.8k",
        "B1.1sts", "B1.2sts", "B1.1s", "B1.2s", "B1.3s", "B1.4s",
        "B2.1k", "B2.2k", "B2.3k", "B2.4k", "B2.5k", "B2.6k", "B2.7k", "B2.8k",
        "B2.1sts", "B2.2sts", "B2.3sts", "B2.1s", "B2.2s", "B2.3s", "B2.4s",
    },
    "Chemical Changes of Organic Compounds": {
        "C1.1k", "C1.2k", "C1.3k", "C1.4k", "C1.5k", "C1.6k", "C1.7k",
        "C1.1sts", "C1.2sts", "C1.1s", "C1.2s", "C1.3s", "C1.4s",
        "C2.1k", "C2.2k", "C2.3k", "C2.4k", "C2.1sts", "C2.2sts", "C2.3sts",
        "C2.1s", "C2.2s", "C2.3s", "C2.4s",
    },
    "Chemical Equilibrium Focusing on Acid-Base Systems": {
        "D1.1k", "D1.2k", "D1.3k", "D1.4k", "D1.5k", "D1.6k", "D1.7k", "D1.8k",
        "D1.1sts", "D1.2sts", "D1.3sts", "D1.1s", "D1.2s", "D1.3s", "D1.4s",
        "D2.1k", "D2.2k", "D2.3k", "D2.1sts", "D2.1s", "D2.2s", "D2.3s", "D2.4s",
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
