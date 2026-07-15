"""Full production QA audit for Science 10 question pool."""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question, is_numerical_answer
from sci10_questions.helpers import VALID_OUTCOMES
from sci10_questions.pool_qa import (
    normalize_text,
    template_key,
    recalc_nr_answer,
    is_weak_distractor,
    clarify_stem,
)

POOL = Path(__file__).parent.parent.parent / "questions.json" / "science10_questions_pool.json"

WEAK_PATTERNS = (
    "none of the above", "all of the above", "incorrect option", "(incorrect",
)

def is_ambiguous_stem(stem: str) -> bool:
    s = stem.strip()
    if s.endswith("?"):
        return False
    low = s.lower()
    if low.startswith((
        "what ", "how ", "which ", "why ", "when ", "where ",
        "calculate ", "determine ", "record ", "express ", "given ",
    )):
        return False
    return " _______?" in clarify_stem(s)


def audit_pool(pool: list[dict]) -> dict[str, list]:
    issues = defaultdict(list)

    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            issues["schema"].extend([(i, r) for r in reasons])

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            issues["outcome_mismatch"].append((i, q["outcome_code"], q["topic"]))

        if is_ambiguous_stem(q["question_text"]):
            issues["ambiguous"].append((i, q["question_text"][:80]))

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1:
                issues["wrong_key"].append((i, "no single correct choice"))
            elif normalize_text(correct[0]["text"]) != normalize_text(q["answer"]):
                issues["wrong_key"].append((i, "answer field mismatch"))
            texts = [normalize_text(c["text"]) for c in q["choices"]]
            if len(set(texts)) < 4:
                issues["implausible_distractor"].append((i, "duplicate choice texts"))
            for c in q["choices"]:
                if not c["is_correct"] and is_weak_distractor(c["text"]):
                    issues["weak_distractor"].append((i, c["text"][:50]))

        if q["question_type"] == "Numerical Response":
            if not is_numerical_answer(q["answer"]):
                issues["grading_ambiguity"].append((i, f"non-numeric answer: {q['answer']}"))
            calc = recalc_nr_answer(q)
            if calc is not None:
                try:
                    if abs(float(calc) - float(q["answer"])) > 0.15:
                        issues["wrong_key"].append((i, f"NR expected {calc}, got {q['answer']}"))
                except ValueError:
                    if normalize_text(calc) != normalize_text(str(q["answer"])):
                        issues["wrong_key"].append((i, f"NR expected {calc}, got {q['answer']}"))

    seen = {}
    for i, q in enumerate(pool):
        key = (normalize_text(q["topic"]), normalize_text(q["question_text"]))
        if key in seen:
            issues["duplicate"].append((i, seen[key], q["question_text"][:70]))
        else:
            seen[key] = i

    tc = Counter(template_key(q) for q in pool)
    for i, q in enumerate(pool):
        tk = template_key(q)
        if tc[tk] > 2:
            issues["duplicate_template"].append((i, tc[tk], q["question_text"][:60]))

    for field, thresh in [("explanation", 3), ("common_mistake", 4), ("skill_tested", 6)]:
        c = Counter(normalize_text(q[field]) for q in pool)
        for i, q in enumerate(pool):
            if c[normalize_text(q[field])] >= thresh:
                issues[f"repeated_{field}"].append((i, c[normalize_text(q[field])], q[field][:50]))

    return dict(issues)


def main() -> int:
    if not POOL.is_file():
        print(f"Pool not found: {POOL}")
        return 1

    pool = json.loads(POOL.read_text(encoding="utf-8"))
    issues = audit_pool(pool)

    print(f"Pool size: {len(pool)}")
    total = 0
    for category in sorted(issues.keys()):
        items = issues[category]
        total += len(items)
        print(f"\n{category}: {len(items)}")
        for item in items[:8]:
            print(f"  {item}")
        if len(items) > 8:
            print(f"  ... and {len(items) - 8} more")

    if total:
        print(f"\nAUDIT FAILED: {total} issue(s)")
        return 1

    print("\nAUDIT PASSED: zero issues")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
