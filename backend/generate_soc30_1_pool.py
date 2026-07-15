"""Generate unbalanced SOC30-1 question pool (~450), validate, export JSON."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from soc30_questions.build_pool import build_all

OUTPUT = Path(__file__).parent.parent / "questions.json" / "soc30-1_questions_pool.json"

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def main() -> None:
    pool = [order_item(q) for q in build_all()]

    # Deduplicate by question_text
    seen: set[str] = set()
    unique = []
    for q in pool:
        key = q["question_text"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(q)
    pool = unique

    errors = []
    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        for r in reasons:
            errors.append((i, q.get("question_text", "")[:80], r))
        if q["question_type"] == "Numerical Response":
            ans = str(q["answer"]).strip()
            if len(ans) == 4 and set(ans) <= set("1234") and len(set(ans)) == 4:
                errors.append((i, "sequence_nr", f"forbidden sequence-code NR: {ans}"))

    if errors:
        print(f"VALIDATION ERRORS: {len(errors)}")
        for e in errors[:20]:
            print(" ", e)
        raise SystemExit(1)

    mc_pos = assert_mc_position_balanced(pool, label=str(OUTPUT))
    print("MC correct-position distribution:", format_position_report(mc_pos))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote {len(pool)} questions -> {OUTPUT}")
    print("By topic:", dict(Counter(q["topic"] for q in pool)))
    print("By type:", dict(Counter(q["question_type"] for q in pool)))
    print("By difficulty:", dict(Counter(q["difficulty"] for q in pool)))
    print("Outcomes:", len(Counter(q["outcome_code"] for q in pool)), "distinct")
    texts = [q["question_text"] for q in pool]
    print("Unique stems:", len(set(texts)), "/", len(texts))


if __name__ == "__main__":
    main()
