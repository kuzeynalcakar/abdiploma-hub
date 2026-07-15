"""Shared helpers for building Science 30 question objects."""

from question_tools import shuffle_mc_choices

COURSE = "SCI30"
SOURCE = "ai"

TOPIC_UNIT = {
    "Circulatory and Immune Systems": "Living Systems Respond to Their Environment",
    "Genetics and Molecular Biology": "Living Systems Respond to Their Environment",
    "Environmental Chemistry": "Chemistry and the Environment",
    "Field Theory and Electrical Energy": "Electromagnetic Energy",
    "Electromagnetic Spectrum": "Electromagnetic Energy",
    "Energy and the Environment": "Energy and the Environment",
}

VALID_OUTCOMES = {
    "Circulatory and Immune Systems": {
        "A1.1k", "A1.2k", "A1.3k", "A1.4k", "A1.1sts", "A1.1s", "A1.2s", "A1.3s", "A1.4s",
        "A2.1k", "A2.2k", "A2.3k", "A2.4k", "A2.5k", "A2.1sts", "A2.1s", "A2.2s", "A2.3s", "A2.4s",
    },
    "Genetics and Molecular Biology": {
        "A3.1k", "A3.2k", "A3.3k", "A3.4k", "A3.5k", "A3.6k", "A3.7k", "A3.8k", "A3.9k", "A3.10k",
        "A3.1sts", "A3.2sts", "A3.1s", "A3.2s", "A3.3s", "A3.4s",
    },
    "Environmental Chemistry": {
        "B1.1k", "B1.2k", "B1.3k", "B1.4k", "B1.5k", "B1.6k", "B1.7k", "B1.8k", "B1.9k",
        "B1.1sts", "B1.2sts", "B1.1s", "B1.2s", "B1.3s", "B1.4s",
        "B2.1k", "B2.2k", "B2.3k", "B2.4k", "B2.5k", "B2.6k", "B2.1sts", "B2.1s", "B2.2s", "B2.3s", "B2.4s",
        "B3.1k", "B3.2k", "B3.3k", "B3.1sts", "B3.2sts", "B3.1s", "B3.2s", "B3.3s", "B3.4s",
    },
    "Field Theory and Electrical Energy": {
        "C1.1k", "C1.2k", "C1.3k", "C1.4k", "C1.5k", "C1.6k", "C1.7k", "C1.8k", "C1.9k",
        "C1.10k", "C1.11k", "C1.12k", "C1.1sts", "C1.2sts", "C1.1s", "C1.2s", "C1.3s", "C1.4s",
    },
    "Electromagnetic Spectrum": {
        "C2.1k", "C2.2k", "C2.3k", "C2.4k", "C2.5k", "C2.6k", "C2.7k", "C2.8k", "C2.9k", "C2.10k", "C2.11k",
        "C2.1sts", "C2.2sts", "C2.3sts", "C2.1s", "C2.2s", "C2.3s", "C2.4s",
    },
    "Energy and the Environment": {
        "D1.1k", "D1.2k", "D1.3k", "D1.4k", "D1.5k", "D1.6k", "D1.1sts", "D1.1s", "D1.2s", "D1.3s", "D1.4s",
        "D2.1k", "D2.2k", "D2.3k", "D2.4k", "D2.5k", "D2.6k", "D2.7k", "D2.8k", "D2.9k", "D2.10k",
        "D2.11k", "D2.12k", "D2.13k", "D2.1sts", "D2.2sts", "D2.1s", "D2.2s", "D2.3s", "D2.4s",
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
