"""Select ~300 production Social Studies 30-1 questions from the validated pool.

Optimizes curriculum coverage, diploma related-issue weighting (adjusted to pool),
outcome balance, cognitive diversity, difficulty mix, and minimum template repetition.

Type mix: retain every objectively gradable NR in the pool (23); fill remainder with MC.
(Requested 60/40 MC/NR is not curriculum-feasible — SS diploma Part B is MC-only and
the validated pool contains only 23 auto-gradable NR items.)

Output: soc30-1_questions_final.json and course_questions_final.json
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "soc30-1_questions_pool.json"
OUTPUT = HERE / "soc30-1_questions_final.json"
OUTPUT_ALIAS = HERE / "course_questions_final.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

TARGET_TOTAL = 300

# Diploma Part B midpoints scaled to 300: RI1=40, RI2=115, RI3=115, RI4=30.
# Pool caps Viability at 92 and Origins at 51 — redistribute surplus to Identity /
# Resistance / Citizenship while preserving RI2-heavy and RI3-heavy emphasis.
TOPIC_TYPE_TARGETS = {
    "Ideology and Identity": {"Multiple Choice": 44, "Numerical Response": 4},
    "Origins of Liberalism": {"Multiple Choice": 45, "Numerical Response": 5},
    "Resistance to Liberalism": {"Multiple Choice": 66, "Numerical Response": 4},
    "The Viability of Contemporary Liberalism": {
        "Multiple Choice": 85,
        "Numerical Response": 7,
    },
    "Citizenship and Ideology": {"Multiple Choice": 37, "Numerical Response": 3},
}

TOPIC_TARGETS = {
    topic: sum(targets.values()) for topic, targets in TOPIC_TYPE_TARGETS.items()
}

TYPE_TARGETS = {
    "Multiple Choice": sum(v["Multiple Choice"] for v in TOPIC_TYPE_TARGETS.values()),
    "Numerical Response": sum(
        v["Numerical Response"] for v in TOPIC_TYPE_TARGETS.values()
    ),
}

# House target is 105/120/75, but this validated pool only has 116 Medium.
DIFF_TARGETS = {
    "Easy": 105,
    "Medium": 116,
    "Hard": 79,
}

# Diploma Part B cognitive split (~50/50 Understanding & Analysis / Evaluation & Synthesis)
COGNITIVE_TARGETS = {
    "understanding_analysis": 150,
    "evaluation_synthesis": 150,
}

MAX_PER_TEMPLATE = 1
MAX_PER_SKILL = 1
# Hard caps keep any single PoS outcome from dominating a topic strip.
MAX_PER_OUTCOME = {
    "Ideology and Identity": 8,
    "Origins of Liberalism": 14,
    # Pool-limited: 2.11/2.12/2.13 are small; allow more 2.9/2.10 without monopoly.
    "Resistance to Liberalism": 23,
    "The Viability of Contemporary Liberalism": 32,
    "Citizenship and Ideology": 8,
}

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]

EVAL_OUTCOMES = {
    "1.9k", "1.10k",
    "2.9k", "2.11k", "2.12k", "2.13k",
    "3.6k", "3.7k", "3.8k", "3.9k",
    "4.7k", "4.8k",
}
EVAL_VERBS = re.compile(
    r"\b(evaluat|assess|justif|weigh|viabilit|extent|critique|balanc|"
    r"tension|trade-?off|should governments|most balanced|strongest .* evaluation|"
    r"illiberal|resistan\w+ justif)\w*",
    re.I,
)


def normalize(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize_text(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    words = text.split()
    return f"{q['topic']}|{' '.join(words[:14])}"


def cognitive_bucket(q: dict) -> str:
    if q["outcome_code"] in EVAL_OUTCOMES:
        return "evaluation_synthesis"
    blob = f"{q['skill_tested']} {q['question_text']}"
    if EVAL_VERBS.search(blob):
        return "evaluation_synthesis"
    return "understanding_analysis"


def outcome_cap(q: dict) -> int:
    # Full-strip topics (target ≈ pool size) cannot rebalance outcomes further.
    if q["topic"] == "The Viability of Contemporary Liberalism":
        return 10_000
    if q["topic"] == "Origins of Liberalism":
        return 14
    return MAX_PER_OUTCOME.get(q["topic"], 12)


def can_add(
    q: dict,
    *,
    template_counts: Counter,
    skill_counts: Counter,
    outcome_counts: Counter,
) -> bool:
    if template_counts[template_key(q)] >= MAX_PER_TEMPLATE:
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
    tmpl = template_key(q)
    if template_counts[tmpl] >= MAX_PER_TEMPLATE:
        return -1e9

    score = 0.0
    score += diff_need[q["difficulty"]] * 5
    score += outcome_need[q["outcome_code"]] * 7
    bucket = cognitive_bucket(q)
    score += cognitive_need[bucket] * 5
    if cognitive_need.get("evaluation_synthesis", 0) > 20 and bucket == "evaluation_synthesis":
        score += 8
    if template_counts[tmpl] == 0:
        score += 4
    if skill_counts[q["skill_tested"]] == 0:
        score += 3
    if outcome_counts.get(q["outcome_code"], 0) == 0:
        score += 6
    score -= template_counts[tmpl] * 3
    score -= skill_counts[q["skill_tested"]] * 2
    if outcome_counts.get(q["outcome_code"], 0) >= outcome_cap(q):
        score -= 20
    if q["difficulty"] == "Medium" and diff_need["Medium"] > 0:
        score += 1.2
    if q["difficulty"] == "Hard" and diff_need["Hard"] > 0:
        score += 1.0
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
    chosen: list[dict] = []

    while len(chosen) < need and remaining:
        diff_need = Counter({d: DIFF_TARGETS[d] - diff_counts[d] for d in DIFF_TARGETS})
        pool_outcomes = {q["outcome_code"] for q in candidates}
        outcome_need = Counter()
        for oc in pool_outcomes:
            have = outcome_counts[oc]
            if have == 0:
                outcome_need[oc] = 4
            elif have < 3:
                outcome_need[oc] = 2
            elif have >= outcome_cap({"topic": candidates[0]["topic"], "outcome_code": oc}):
                outcome_need[oc] = -8

        cognitive_need = Counter(COGNITIVE_TARGETS)
        for bucket, have in cognitive_counts.items():
            cognitive_need[bucket] = max(0, COGNITIVE_TARGETS[bucket] - have)

        viable = [
            q
            for q in remaining
            if can_add(
                q,
                template_counts=template_counts,
                skill_counts=skill_counts,
                outcome_counts=outcome_counts,
            )
        ]
        if not viable:
            # Last resort: still enforce template + outcome caps (never ignore outcomes).
            viable = [
                q
                for q in remaining
                if template_counts[template_key(q)] < MAX_PER_TEMPLATE
                and outcome_counts[q["outcome_code"]] < outcome_cap(q)
            ]
        if not viable:
            break

        pick_pool = viable
        # Prefer under-filled cognitive bucket when far from target.
        if cognitive_need["evaluation_synthesis"] > cognitive_need["understanding_analysis"] + 10:
            es = [q for q in viable if cognitive_bucket(q) == "evaluation_synthesis"]
            if es:
                pick_pool = es
        for priority_diff in ("Medium", "Hard", "Easy"):
            if diff_need[priority_diff] > 0:
                subset = [q for q in pick_pool if q["difficulty"] == priority_diff]
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

        if not scored:
            break
        scored.sort(key=lambda x: x[0], reverse=True)
        q = scored[0][1]
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


def rebalance_difficulty(
    selected: list[dict],
    pool: list[dict],
    rng: random.Random,
    *,
    template_counts: Counter,
    outcome_counts: Counter,
    skill_counts: Counter,
    cognitive_counts: Counter,
) -> list[dict]:
    selected = list(selected)
    selected_ids = {id(q) for q in selected}
    by_topic_type = defaultdict(lambda: defaultdict(list))
    for q in pool:
        by_topic_type[q["topic"]][q["question_type"]].append(q)

    for _ in range(400):
        diff_counts = Counter(q["difficulty"] for q in selected)
        over = [d for d in DIFF_TARGETS if diff_counts[d] > DIFF_TARGETS[d]]
        under = [d for d in DIFF_TARGETS if diff_counts[d] < DIFF_TARGETS[d]]
        if not over or not under:
            break

        swap_out = next(
            (
                q
                for q in selected
                if diff_counts[q["difficulty"]] > DIFF_TARGETS[q["difficulty"]]
            ),
            None,
        )
        if swap_out is None:
            break

        need_diff = under[0]
        def candidates_for(diff: str) -> list[dict]:
            return [
                q
                for q in by_topic_type[swap_out["topic"]][swap_out["question_type"]]
                if id(q) not in selected_ids
                and q["difficulty"] == diff
                and can_add(
                    q,
                    template_counts=template_counts,
                    skill_counts=skill_counts,
                    outcome_counts=outcome_counts,
                )
            ]

        candidates = candidates_for(need_diff)
        if not candidates:
            for nd in under:
                candidates = candidates_for(nd)
                if candidates:
                    need_diff = nd
                    break
        if not candidates:
            rng.shuffle(selected)
            continue

        # Prefer cognitive under-fill among difficulty-matched candidates
        cog_need = Counter(COGNITIVE_TARGETS)
        for b, have in cognitive_counts.items():
            cog_need[b] = max(0, COGNITIVE_TARGETS[b] - have)
        if cog_need["evaluation_synthesis"] > cog_need["understanding_analysis"]:
            es = [q for q in candidates if cognitive_bucket(q) == "evaluation_synthesis"]
            if es:
                candidates = es

        swap_in = rng.choice(candidates)
        idx = selected.index(swap_out)
        template_counts[template_key(swap_out)] -= 1
        skill_counts[swap_out["skill_tested"]] -= 1
        outcome_counts[swap_out["outcome_code"]] -= 1
        cognitive_counts[cognitive_bucket(swap_out)] -= 1
        selected_ids.remove(id(swap_out))

        selected[idx] = swap_in
        selected_ids.add(id(swap_in))
        record_pick(
            swap_in,
            diff_counts=Counter(),
            outcome_counts=outcome_counts,
            template_counts=template_counts,
            skill_counts=skill_counts,
            cognitive_counts=cognitive_counts,
        )

    return selected


def select_balanced(pool: list[dict], seed: int = 301) -> list[dict]:
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

    assert sum(TOPIC_TARGETS.values()) == TARGET_TOTAL
    assert sum(TYPE_TARGETS.values()) == TARGET_TOTAL

    diff_counts = Counter()
    outcome_counts = Counter()
    template_counts = Counter()
    skill_counts = Counter()
    cognitive_counts = Counter()
    selected: list[dict] = []

    # Pick NR first (scarce), then MC
    for topic in TOPIC_TARGETS:
        for qtype in ("Numerical Response", "Multiple Choice"):
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
        cognitive_counts=cognitive_counts,
    )
    rng.shuffle(selected)
    return selected[:TARGET_TOTAL]


def print_report(items: list[dict]) -> None:
    print(f"\n=== SOC30-1 PRODUCTION BANK ({len(items)}) ===")
    print("\nTopic distribution (diploma-adjusted):")
    for topic, count in sorted(
        Counter(i["topic"] for i in items).items(), key=lambda x: -x[1]
    ):
        tgt = TOPIC_TARGETS[topic]
        print(f"  {topic}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")

    print("\nQuestion type distribution:")
    for qtype, count in sorted(Counter(i["question_type"] for i in items).items()):
        tgt = TYPE_TARGETS[qtype]
        print(f"  {qtype}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")
    print(
        "  NOTE: NR capped at full validated pool (23). "
        "Requested 40% NR not feasible for SS30-1."
    )

    print("\nDifficulty distribution:")
    for diff in ("Easy", "Medium", "Hard"):
        count = sum(1 for i in items if i["difficulty"] == diff)
        tgt = DIFF_TARGETS[diff]
        print(f"  {diff}: {count} (target {tgt}, {100 * count / len(items):.1f}%)")

    outcomes = Counter(i["outcome_code"] for i in items)
    print(
        f"\nUnique outcomes: {len(outcomes)} "
        f"(min {min(outcomes.values())}, max {max(outcomes.values())})"
    )
    for oc, n in sorted(outcomes.items(), key=lambda x: (x[0][0], float(re.sub(r'[a-z]', '', x[0][2:]) or 0))):
        print(f"  {oc}: {n}")

    cog = Counter(cognitive_bucket(i) for i in items)
    print("\nCognitive distribution:")
    for bucket, tgt in COGNITIVE_TARGETS.items():
        print(f"  {bucket}: {cog[bucket]} (target {tgt})")

    templates = Counter(template_key(i) for i in items)
    skills = Counter(i["skill_tested"] for i in items)
    print(f"\nUnique templates: {len(templates)} (max repeats {max(templates.values())})")
    print(f"Unique skills: {len(skills)} (max repeats {max(skills.values())})")


def main() -> None:
    pool = json.loads(INPUT.read_text(encoding="utf-8"))
    print(f"Loaded pool: {len(pool)} questions")
    print(f"Type targets: {TYPE_TARGETS}")
    print(f"Topic targets: {TOPIC_TARGETS}")

    selected = select_balanced(pool)
    if len(selected) != TARGET_TOTAL:
        raise SystemExit(f"Expected {TARGET_TOTAL}, got {len(selected)}")

    ordered = [normalize(q) for q in selected]
    for i, q in enumerate(ordered):
        reasons = validate_question(q, i)
        if reasons:
            raise SystemExit(f"Invalid item {i}: {reasons}")

    # Exact stem uniqueness
    stems = [normalize_text(q["question_text"]) for q in ordered]
    if len(stems) != len(set(stems)):
        raise SystemExit("Duplicate stems in production selection")

    payload = json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"
    OUTPUT.write_text(payload, encoding="utf-8")
    OUTPUT_ALIAS.write_text(payload, encoding="utf-8")

    print_report(ordered)
    print(f"\nWrote production bank to {OUTPUT}")
    print(f"Alias copy: {OUTPUT_ALIAS}")


if __name__ == "__main__":
    main()
