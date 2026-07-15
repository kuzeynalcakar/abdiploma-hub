"""Select ~300 production Mathematics 20-1 questions from the validated pool.

Optimizes curriculum coverage, school-final topic weighting, outcome balance,
cognitive diversity (procedural/conceptual/problem-solving), difficulty mix,
and minimum template repetition.

The pool contains 139 MC and 491 NR items. Ideal split is 60/40 (180 MC / 120 NR),
but all 139 MC are retained and NR fills to 300 (46.3% MC / 53.7% NR).

Output: math20-1_questions_final.json and course_questions_final.json
"""

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "math20-1_questions_pool.json"
OUTPUT = HERE / "math20-1_questions_final.json"
OUTPUT_ALIAS = HERE / "course_questions_final.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

TARGET_TOTAL = 300

# School-final topic weighting (blueprint proxy for Math 20-1).
TOPIC_TARGETS = {
    "Quadratic Equations": 52,
    "Rational Expressions and Equations": 45,
    "Trigonometry": 45,
    "Quadratic Functions": 36,
    "Absolute Value and Reciprocal Functions": 36,
    "Radical Expressions and Equations": 30,
    "Sequences and Series": 23,
    "Linear and Quadratic Inequalities": 18,
    "Systems of Equations": 15,
}

# MC capped by pool availability (139 total MC in pool — all retained).
TOPIC_TYPE_TARGETS = {
    "Quadratic Equations": {"Multiple Choice": 24, "Numerical Response": 28},
    "Rational Expressions and Equations": {"Multiple Choice": 9, "Numerical Response": 36},
    "Trigonometry": {"Multiple Choice": 19, "Numerical Response": 26},
    "Quadratic Functions": {"Multiple Choice": 28, "Numerical Response": 8},
    "Absolute Value and Reciprocal Functions": {"Multiple Choice": 29, "Numerical Response": 7},
    "Radical Expressions and Equations": {"Multiple Choice": 4, "Numerical Response": 26},
    "Sequences and Series": {"Multiple Choice": 9, "Numerical Response": 14},
    "Linear and Quadratic Inequalities": {"Multiple Choice": 13, "Numerical Response": 5},
    "Systems of Equations": {"Multiple Choice": 4, "Numerical Response": 11},
}

TYPE_TARGETS = {
    "Multiple Choice": sum(v["Multiple Choice"] for v in TOPIC_TYPE_TARGETS.values()),
    "Numerical Response": sum(v["Numerical Response"] for v in TOPIC_TYPE_TARGETS.values()),
}

DIFF_TARGETS = {
    "Easy": 105,
    "Medium": 120,
    "Hard": 75,
}

# Alberta Math cognitive framework (diploma-style).
COGNITIVE_TARGETS = {
    "procedural": 90,
    "conceptual": 102,
    "problem_solving": 108,
}

MAX_PER_TEMPLATE_MC = 3  # Pool has 139 MC across few templates; cap 2 cannot fill targets.
MAX_PER_TEMPLATE_NR = 3
MAX_PER_OUTCOME_MC = 10
MAX_PER_OUTCOME_NR = 12
MAX_PER_SKILL = 2

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]


def normalize(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize_text(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def cognitive_bucket(q: dict) -> str:
    s = q["skill_tested"].casefold()
    if any(w in s for w in (
        "explaining", "identifying", "distinguishing", "interpreting",
        "describing", "recognizing", "comparing", "relating", "choosing",
        "classifying", "locating", "defining",
    )):
        return "conceptual"
    if any(w in s for w in (
        "modelling", "contextual", "applying", "problem", "system",
        "ambiguous", "intersection", "modelling",
    )):
        return "problem_solving"
    return "procedural"


def template_cap(q: dict) -> int:
    return MAX_PER_TEMPLATE_NR if q["question_type"] == "Numerical Response" else MAX_PER_TEMPLATE_MC


def outcome_cap(q: dict) -> int:
    return MAX_PER_OUTCOME_NR if q["question_type"] == "Numerical Response" else MAX_PER_OUTCOME_MC


def can_add(
    q: dict,
    *,
    template_counts: Counter,
    skill_counts: Counter,
    outcome_counts: Counter,
) -> bool:
    if template_counts[template_key(q)] >= template_cap(q):
        return False
    if skill_counts[q["skill_tested"]] >= MAX_PER_SKILL:
        return False
    if outcome_counts[q["outcome_code"]] >= outcome_cap(q):
        return False
    return True


def score_item(
    q: dict,
    *,
    diff_need: Counter,
    outcome_need: Counter,
    template_counts: Counter,
    skill_counts: Counter,
    cognitive_need: Counter,
    outcome_counts: Counter,
) -> float:
    score = 0.0
    tmpl = template_key(q)
    if template_counts[tmpl] >= template_cap(q):
        return -1e9

    score += diff_need[q["difficulty"]] * 4
    score += outcome_need[q["outcome_code"]] * 8
    score += cognitive_need[cognitive_bucket(q)] * 5

    if template_counts[tmpl] == 0:
        score += 4
    if skill_counts[q["skill_tested"]] == 0:
        score += 3
    if outcome_need[q["outcome_code"]] > 0:
        score += 5

    score -= template_counts[tmpl] * 3
    score -= skill_counts[q["skill_tested"]] * 0.75
    if outcome_counts.get(q["outcome_code"], 0) >= outcome_cap(q):
        score -= 12

    return score


def record_pick(
    q: dict,
    *,
    diff_counts: Counter,
    outcome_counts: Counter,
    template_counts: Counter,
    skill_counts: Counter,
    cognitive_counts: Counter,
) -> None:
    diff_counts[q["difficulty"]] += 1
    outcome_counts[q["outcome_code"]] += 1
    template_counts[template_key(q)] += 1
    skill_counts[q["skill_tested"]] += 1
    cognitive_counts[cognitive_bucket(q)] += 1


def pick_for_slot(
    candidates: list[dict],
    need: int,
    qtype: str,
    rng: random.Random,
    *,
    diff_counts: Counter,
    outcome_counts: Counter,
    template_counts: Counter,
    skill_counts: Counter,
    cognitive_counts: Counter,
) -> list[dict]:
    if need <= 0:
        return []

    remaining = list(candidates)
    chosen = []

    while len(chosen) < need and remaining:
        diff_need = Counter({d: DIFF_TARGETS[d] - diff_counts[d] for d in DIFF_TARGETS})
        pool_outcomes = {q["outcome_code"] for q in candidates}
        outcome_need = Counter()
        for oc in pool_outcomes:
            if outcome_counts[oc] == 0:
                outcome_need[oc] = 5
            elif outcome_counts[oc] < 2:
                outcome_need[oc] = 3
            elif outcome_counts[oc] >= outcome_cap({"outcome_code": oc, "question_type": qtype}):
                outcome_need[oc] = -10

        cognitive_need = Counter(COGNITIVE_TARGETS)
        for bucket in cognitive_counts:
            cognitive_need[bucket] = max(0, cognitive_need[bucket] - cognitive_counts[bucket])

        viable = [
            q for q in remaining
            if can_add(
                q,
                template_counts=template_counts,
                skill_counts=skill_counts,
                outcome_counts=outcome_counts,
            )
        ]
        if not viable:
            viable = [
                q for q in remaining
                if template_counts[template_key(q)] < template_cap(q)
                and skill_counts[q["skill_tested"]] < MAX_PER_SKILL
            ]
        if not viable:
            viable = list(remaining)
        if not viable:
            break

        pick_pool = viable
        for priority_diff in ("Hard", "Medium", "Easy"):
            if diff_need[priority_diff] > 0:
                subset = [q for q in viable if q["difficulty"] == priority_diff]
                if subset:
                    pick_pool = subset
                    break

        scored = []
        for q in pick_pool:
            s = score_item(
                q,
                diff_need=diff_need,
                outcome_need=outcome_need,
                template_counts=template_counts,
                skill_counts=skill_counts,
                cognitive_need=cognitive_need,
                outcome_counts=outcome_counts,
            )
            if s > -1e8:
                scored.append((s + rng.random() * 0.01, q))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            q = scored[0][1]
        else:
            q = pick_pool[rng.randrange(len(pick_pool))]

        remaining.remove(q)
        chosen.append(q)
        record_pick(
            q,
            diff_counts=diff_counts,
            outcome_counts=outcome_counts,
            template_counts=template_counts,
            skill_counts=skill_counts,
            cognitive_counts=cognitive_counts,
        )

    return chosen


def select_balanced(pool: list[dict], seed: int = 201) -> list[dict]:
    rng = random.Random(seed)
    by_topic_type = defaultdict(lambda: defaultdict(list))
    for item in pool:
        by_topic_type[item["topic"]][item["question_type"]].append(item)

    for topic, type_targets in TOPIC_TYPE_TARGETS.items():
        for qtype, need in type_targets.items():
            available = len(by_topic_type[topic][qtype])
            if available < need:
                raise ValueError(
                    f"Pool short for {topic}/{qtype}: need {need}, have {available}"
                )

    diff_counts = Counter()
    outcome_counts = Counter()
    template_counts = Counter()
    skill_counts = Counter()
    cognitive_counts = Counter()
    selected: list[dict] = []

    for topic in TOPIC_TARGETS:
        # MC pool is the binding constraint (139 total) — select MC before NR.
        for qtype in ("Multiple Choice", "Numerical Response"):
            need = TOPIC_TYPE_TARGETS[topic][qtype]
            candidates = list(by_topic_type[topic][qtype])
            rng.shuffle(candidates)
            picked = pick_for_slot(
                candidates,
                need,
                qtype,
                rng,
                diff_counts=diff_counts,
                outcome_counts=outcome_counts,
                template_counts=template_counts,
                skill_counts=skill_counts,
                cognitive_counts=cognitive_counts,
            )
            if len(picked) != need:
                raise ValueError(
                    f"Selected {len(picked)} for {topic}/{qtype}, expected {need}"
                )
            selected.extend(picked)

    selected = rebalance_difficulty(
        selected,
        pool,
        rng,
        template_counts=template_counts,
        outcome_counts=outcome_counts,
        skill_counts=skill_counts,
    )
    return selected[:TARGET_TOTAL]


def rebalance_difficulty(
    selected: list[dict],
    pool: list[dict],
    rng: random.Random,
    *,
    template_counts: Counter,
    outcome_counts: Counter,
    skill_counts: Counter,
):
    diff_counts = Counter(q["difficulty"] for q in selected)
    selected_set = {id(q) for q in selected}

    for _ in range(3000):
        over = [d for d in DIFF_TARGETS if diff_counts[d] > DIFF_TARGETS[d]]
        under = [d for d in DIFF_TARGETS if diff_counts[d] < DIFF_TARGETS[d]]
        if not over or not under:
            break

        swap_out = next(
            (q for q in selected if diff_counts[q["difficulty"]] > DIFF_TARGETS[q["difficulty"]]),
            None,
        )
        if swap_out is None:
            break

        template_counts[template_key(swap_out)] -= 1
        outcome_counts[swap_out["outcome_code"]] -= 1
        skill_counts[swap_out["skill_tested"]] -= 1

        candidates = [
            c
            for c in pool
            if c["topic"] == swap_out["topic"]
            and c["question_type"] == swap_out["question_type"]
            and c["difficulty"] in under
            and id(c) not in selected_set
            and can_add(
                c,
                template_counts=template_counts,
                skill_counts=skill_counts,
                outcome_counts=outcome_counts,
            )
        ]

        if not candidates:
            template_counts[template_key(swap_out)] += 1
            outcome_counts[swap_out["outcome_code"]] += 1
            skill_counts[swap_out["skill_tested"]] += 1
            continue

        swap_in = candidates[rng.randrange(len(candidates))]
        selected.remove(swap_out)
        selected_set.remove(id(swap_out))
        diff_counts[swap_out["difficulty"]] -= 1
        selected.append(swap_in)
        selected_set.add(id(swap_in))
        diff_counts[swap_in["difficulty"]] += 1
        template_counts[template_key(swap_in)] += 1
        outcome_counts[swap_in["outcome_code"]] += 1
        skill_counts[swap_in["skill_tested"]] += 1

    return selected


def validate_all(items: list[dict]) -> list[tuple[int, list[str]]]:
    errors = []
    seen_text = set()
    template_counts = Counter()
    for i, item in enumerate(items):
        reasons = validate_question(item, i)
        key = (item["topic"].strip().lower(), normalize_text(item["question_text"]))
        if not reasons:
            if key in seen_text:
                reasons = ["duplicate question text in file"]
            else:
                seen_text.add(key)
        tmpl = template_key(item)
        cap = template_cap(item)
        if template_counts[tmpl] >= cap:
            reasons = reasons + [f"template family exceeds cap ({cap}): {tmpl[:60]}"]
        template_counts[tmpl] += 1
        if reasons:
            errors.append((i, reasons))
    return errors


def print_report(items: list[dict]) -> None:
    print("\n=== Mathematics 20-1 Production Bank ===")
    print(f"Total: {len(items)}")
    print("\nTopic distribution (school-final weighting):")
    for topic, count in sorted(Counter(i["topic"] for i in items).items()):
        tgt = TOPIC_TARGETS[topic]
        print(f"  {topic}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")
    print("\nQuestion type distribution:")
    for qtype, count in sorted(Counter(i["question_type"] for i in items).items()):
        tgt = TYPE_TARGETS[qtype]
        print(f"  {qtype}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")
    print("\nDifficulty distribution:")
    for diff, count in sorted(Counter(i["difficulty"] for i in items).items()):
        tgt = DIFF_TARGETS[diff]
        print(f"  {diff}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")
    outcomes = Counter(i["outcome_code"] for i in items)
    print(f"\nUnique outcomes: {len(outcomes)} (min {min(outcomes.values())}, max {max(outcomes.values())})")
    print("Outcome counts:", dict(sorted(outcomes.items())))
    templates = Counter(template_key(i) for i in items)
    print(f"Template families: {len(templates)} (max per family {max(templates.values())})")
    cognitive = Counter(cognitive_bucket(i) for i in items)
    print(f"Cognitive mix: {dict(cognitive)}")
    print(f"Cognitive targets: {COGNITIVE_TARGETS}")
    skills = Counter(i["skill_tested"] for i in items)
    print(f"Unique skills: {len(skills)} (max repeats {max(skills.values())})")


def main() -> None:
    if not INPUT.is_file():
        print(f"Input not found: {INPUT}. Run generate_math20_1.py and math20_1_qa_fix.py first.")
        raise SystemExit(1)

    with INPUT.open(encoding="utf-8") as f:
        pool = [normalize(i) for i in json.load(f)]

    assert sum(TOPIC_TARGETS.values()) == TARGET_TOTAL
    assert sum(TYPE_TARGETS.values()) == TARGET_TOTAL

    print(f"Loaded pool: {len(pool)} questions")
    print(f"Type targets: {TYPE_TARGETS} ({100*TYPE_TARGETS['Multiple Choice']/TARGET_TOTAL:.1f}% MC)")

    selected = select_balanced(pool)
    selected = [normalize(i) for i in selected]

    errors = validate_all(selected)
    if errors:
        print(f"Validation failed: {len(errors)} errors")
        for idx, reasons in errors[:15]:
            print(f"  {idx}: {reasons}")
        raise SystemExit(1)

    payload = json.dumps(selected, indent=2, ensure_ascii=False) + "\n"
    OUTPUT.write_text(payload, encoding="utf-8")
    OUTPUT_ALIAS.write_text(payload, encoding="utf-8")

    print_report(selected)
    print(f"\nWrote production bank to {OUTPUT}")
    print(f"Alias copy: {OUTPUT_ALIAS}")
    print("Validation: PASSED")
    print("Import-ready for: python -m app.database.question_import")


if __name__ == "__main__":
    main()
