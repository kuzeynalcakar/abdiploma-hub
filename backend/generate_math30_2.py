"""Generate Mathematics 30-2 question pool (~450 original questions)."""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from math30_2_questions.helpers import order_item
from math30_2_questions.set_theory_logic import generate as gen_set_theory
from math30_2_questions.counting import generate as gen_counting
from math30_2_questions.probability import generate as gen_probability
from math30_2_questions.rationals import generate as gen_rationals
from math30_2_questions.polynomial import generate as gen_polynomial
from math30_2_questions.exp_log import generate as gen_exp_log
from math30_2_questions.sinusoidal import generate as gen_sinusoidal
from math30_2_questions.supplements import generate as gen_supplements

OUTPUT = Path(__file__).parent.parent / "questions.json" / "math30-2_questions_pool.json"
SEED = 302


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def deduplicate(questions: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for q in questions:
        key = f"{q['topic']}|{normalize_text(q['question_text'])}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
    return unique


def validate_all(questions: list[dict]) -> list[str]:
    errors = []
    for i, q in enumerate(questions):
        reasons = validate_question(q, i)
        if reasons:
            errors.append(f"Q{i}: {'; '.join(reasons)}")
    return errors


def main():
    import random
    rng = random.Random(SEED)

    generators = [
        gen_set_theory,
        gen_counting,
        gen_probability,
        gen_rationals,
        gen_polynomial,
        gen_exp_log,
        gen_sinusoidal,
        gen_supplements,
    ]

    pool: list[dict] = []
    for gen in generators:
        pool.extend(gen(rng))

    pool = deduplicate(pool)
    pool = [order_item(q) for q in pool]

    errors = validate_all(pool)
    if errors:
        print(f"Validation errors ({len(errors)}):")
        for e in errors[:30]:
            print(f"  {e}")
        if len(errors) > 30:
            print(f"  ... and {len(errors) - 30} more")
        sys.exit(1)

    mc_pos = assert_mc_position_balanced(pool, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(pool, f, indent=2, ensure_ascii=False)
        f.write("\n")

    topics = Counter(q["topic"] for q in pool)
    types = Counter(q["question_type"] for q in pool)
    diffs = Counter(q["difficulty"] for q in pool)
    outcomes = Counter(q["outcome_code"] for q in pool)

    print(f"Wrote {len(pool)} questions to {OUTPUT}")
    print(f"Topics: {dict(sorted(topics.items()))}")
    print(f"Types: {dict(types)}")
    print(f"Difficulty: {dict(diffs)}")
    print(f"Outcomes ({len(outcomes)}): {dict(sorted(outcomes.items()))}")


if __name__ == "__main__":
    main()
