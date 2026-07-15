"""Select ~300 production Mathematics 30-2 questions from the validated pool.

Blueprint-driven selection optimizing diploma topic weighting, outcome balance,
cognitive diversity (procedural/conceptual/problem-solving), difficulty mix, and
minimum template repetition.

Pool constraint: only 64 MC available (QA-clean pool is NR-heavy). All 64 MC are
retained; NR fills to 300 (21.3% MC / 78.7% NR). Ideal diploma practice split
is 60/40 MC/NR but cannot be met without additional MC authoring.

Output: math30-2_questions_final.json and course_questions_final.json
"""

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "math30-2_questions_pool.json"
OUTPUT = HERE / "math30-2_questions_final.json"
OUTPUT_ALIAS = HERE / "course_questions_final.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

TARGET_TOTAL = 300

# Diploma-weighted topic targets (adjusted to pool availability).
TOPIC_TARGETS = {
    "Set Theory and Logic": 43,
    "Counting Methods": 50,
    "Probability": 56,
    "Rational Expressions and Equations": 43,
    "Polynomial Functions": 30,
    "Exponential and Logarithmic Functions": 42,
    "Sinusoidal Functions": 36,
}

# All pool MC retained per topic; remainder NR.
TOPIC_TYPE_TARGETS = {
    "Set Theory and Logic": {"Multiple Choice": 13, "Numerical Response": 30},
    "Counting Methods": {"Multiple Choice": 6, "Numerical Response": 44},
    "Probability": {"Multiple Choice": 14, "Numerical Response": 42},
    "Rational Expressions and Equations": {"Multiple Choice": 7, "Numerical Response": 36},
    "Polynomial Functions": {"Multiple Choice": 12, "Numerical Response": 18},
    "Exponential and Logarithmic Functions": {"Multiple Choice": 9, "Numerical Response": 33},
    "Sinusoidal Functions": {"Multiple Choice": 3, "Numerical Response": 33},
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

COGNITIVE_TARGETS = {
    "procedural": 90,
    "conceptual": 102,
    "problem_solving": 108,
}

OUTCOME_TARGETS = {
    "LR1": 15, "LR2": 28,
    "P1": 20, "P2": 15, "P3": 21, "P4": 22, "P5": 21, "P6": 18,
    "RF1": 16, "RF2": 14, "RF3": 18, "RF4": 12, "RF5": 14,
    "RF6": 16, "RF7": 27, "RF8": 33,
}

MAX_PER_TEMPLATE_MC = 3
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
        "classifying", "locating", "defining", "validity", "assessing",
    )):
        return "conceptual"
    if any(w in s for w in (
        "modelling", "contextual", "applying", "problem", "system",
        "survey", "context", "committee", "festival", "jar", "playoff",
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

    target = OUTCOME_TARGETS.get(q["outcome_code"], 0)
    if outcome_counts[q["outcome_code"]] < target:
        score += (target - outcome_counts[q["outcome_code"]]) * 2

    if template_counts[tmpl] == 0:
        score += 4
    if skill_counts[q["skill_tested"]] == 0:
        score += 3

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

        outcome_need = Counter()
        for oc in OUTCOME_TARGETS:
            tgt = OUTCOME_TARGETS[oc]
            have = outcome_counts[oc]
            if have < tgt:
                outcome_need[oc] = tgt - have
            elif have >= outcome_cap({"outcome_code": oc, "question_type": qtype}):
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


def select_balanced(pool: list[dict], seed: int = 302) -> list[dict]:
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
            reasons = reasons + [f"template family exceeds cap ({cap})"]
        template_counts[tmpl] += 1
        if reasons:
            errors.append((i, reasons))
    return errors


def print_report(items: list[dict]) -> None:
    print("\n=== Mathematics 30-2 Production Bank ===")
    print(f"Total: {len(items)}")
    print("\nTopic distribution (diploma-weighted):")
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
        print(f"Input not found: {INPUT}. Run math30_2_qa_fix.py first.")
        raise SystemExit(1)

    with INPUT.open(encoding="utf-8") as f:
        pool = [normalize(i) for i in json.load(f)]

    assert sum(TOPIC_TARGETS.values()) == TARGET_TOTAL
    assert sum(TYPE_TARGETS.values()) == TARGET_TOTAL

    print(f"Loaded pool: {len(pool)} questions")
    print(f"Type targets: {TYPE_TARGETS}")
    print(
        f"MC share: {100 * TYPE_TARGETS['Multiple Choice'] / TARGET_TOTAL:.1f}% "
        f"(pool MC cap: {sum(1 for q in pool if q['question_type']=='Multiple Choice')})"
    )

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
