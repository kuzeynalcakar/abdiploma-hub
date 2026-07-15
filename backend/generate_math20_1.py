"""Generate Mathematics 20-1 question pool (~450 original questions)."""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from math20_1_questions.helpers import order_item, FIELD_ORDER
from math20_1_questions.sequences import generate as gen_sequences
from math20_1_questions.trigonometry import generate as gen_trig
from math20_1_questions.quadratics import generate as gen_quadratics
from math20_1_questions.radicals import generate as gen_radicals
from math20_1_questions.rationals import generate as gen_rationals
from math20_1_questions.other_topics import generate as gen_other
from math20_1_questions.supplements import generate as gen_supplements

OUTPUT = Path(__file__).parent.parent / "questions.json" / "math20-1_questions_pool.json"
SEED = 201


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
        gen_sequences,
        gen_trig,
        gen_quadratics,
        gen_radicals,
        gen_rationals,
        gen_other,
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
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
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
