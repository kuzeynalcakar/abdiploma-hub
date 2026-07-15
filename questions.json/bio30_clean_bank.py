"""Clean, balance, and export Biology 30 question bank to production spec (~300 questions)."""

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "biology30_questions_pool.json"
OUTPUT = HERE / "biology30_questions_final.json"

sys.path.insert(0, str(HERE.parent / "backend"))
from app.database.question_validator import validate_question

REQUIRED_FIELDS = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]

TARGET_TOTAL = 300

TOPIC_TARGETS = {
    "Nervous and Endocrine Systems": 75,
    "Reproduction and Development": 60,
    "Cell Division": 45,
    "Genetics and Molecular Biology": 75,
    "Population and Community Dynamics": 45,
}

TYPE_TARGETS = {
    "Multiple Choice": 180,
    "Numerical Response": 90,
    "Written Response": 30,
}

DIFF_TARGETS = {
    "Easy": 105,
    "Medium": 120,
    "Hard": 75,
}

FIELD_ORDER = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation", "common_mistake", "source",
]


def normalize(item):
    ordered = {k: item[k] for k in FIELD_ORDER}
    for f in REQUIRED_FIELDS:
        if f not in ordered or ordered[f] is None or ordered[f] == "":
            raise ValueError(f"Missing field {f}")
    return ordered


def score_item(item, type_need, diff_need):
    """Higher score = more needed for balancing."""
    t = item["question_type"]
    d = item["difficulty"]
    return type_need.get(t, 0) * 3 + diff_need.get(d, 0)


def pick_with_difficulty(candidates, need, diff_count, rng):
    """Pick `need` items preferring difficulties still under target."""
    chosen = []
    remaining = list(candidates)
    rng.shuffle(remaining)
    while len(chosen) < need and remaining:
        under = [d for d in DIFF_TARGETS if diff_count[d] < DIFF_TARGETS[d]]
        pick = None
        if under:
            for i, item in enumerate(remaining):
                if item["difficulty"] in under:
                    pick = remaining.pop(i)
                    break
        if pick is None:
            pick = remaining.pop(0)
        chosen.append(pick)
        diff_count[pick["difficulty"]] += 1
    return chosen


def select_balanced(pool: list[dict], seed: int = 30) -> list[dict]:
    rng = random.Random(seed)
    by_topic_type = defaultdict(lambda: defaultdict(list))
    for item in pool:
        by_topic_type[item["topic"]][item["question_type"]].append(item)

    topic_type_targets = {}
    for topic, tcount in TOPIC_TARGETS.items():
        topic_type_targets[topic] = {
            "Multiple Choice": round(tcount * 0.60),
            "Numerical Response": round(tcount * 0.30),
            "Written Response": tcount - round(tcount * 0.60) - round(tcount * 0.30),
        }
    mc_sum = sum(v["Multiple Choice"] for v in topic_type_targets.values())
    if mc_sum != TYPE_TARGETS["Multiple Choice"]:
        diff = TYPE_TARGETS["Multiple Choice"] - mc_sum
        topic_type_targets["Genetics and Molecular Biology"]["Multiple Choice"] += diff

    selected = []
    diff_count = Counter()
    for topic, type_targets in topic_type_targets.items():
        for qtype, need in type_targets.items():
            candidates = list(by_topic_type[topic][qtype])
            if len(candidates) < need:
                raise ValueError(
                    f"Pool short for {topic}/{qtype}: need {need}, have {len(candidates)}"
                )
            selected.extend(pick_with_difficulty(candidates, need, diff_count, rng))

    selected = rebalance_difficulty(selected, pool, rng)
    return selected[:TARGET_TOTAL]


def rebalance_difficulty(selected, pool, rng):
    diff_count = Counter(i["difficulty"] for i in selected)
    selected_ids = {id(i) for i in selected}

    def deficit(d):
        return DIFF_TARGETS[d] - diff_count[d]

    for _ in range(1000):
        over = [d for d in DIFF_TARGETS if diff_count[d] > DIFF_TARGETS[d]]
        under = [d for d in DIFF_TARGETS if deficit(d) > 0]
        if not over or not under:
            break

        swap_out = None
        for item in selected:
            if diff_count[item["difficulty"]] > DIFF_TARGETS[item["difficulty"]]:
                swap_out = item
                break
        if not swap_out:
            break

        topic = swap_out["topic"]
        qtype = swap_out["question_type"]
        candidates = [
            c for c in pool
            if c["topic"] == topic
            and c["question_type"] == qtype
            and c["difficulty"] in under
            and id(c) not in selected_ids
        ]
        if not candidates:
            continue
        swap_in = candidates[0]
        selected.remove(swap_out)
        selected_ids.remove(id(swap_out))
        diff_count[swap_out["difficulty"]] -= 1
        selected.append(swap_in)
        selected_ids.add(id(swap_in))
        diff_count[swap_in["difficulty"]] += 1

    return selected


def validate_all(items):
    errors = []
    seen = set()
    for i, item in enumerate(items):
        reasons = validate_question(item, i)
        if not reasons:
            key = (
                item["topic"].strip().lower(),
                " ".join(item["question_text"].split()).lower(),
            )
            if key in seen:
                reasons = ["duplicate question text in file"]
            else:
                seen.add(key)
        if reasons:
            errors.append((i, reasons))
    return errors


def print_report(items):
    print(f"\n=== Biology 30 Bank Report ===")
    print(f"Total: {len(items)}")
    print("\nTopic distribution:")
    for k, v in sorted(Counter(i["topic"] for i in items).items()):
        pct = 100 * v / len(items)
        print(f"  {k}: {v} ({pct:.1f}%)")
    print("\nDifficulty distribution:")
    for k, v in sorted(Counter(i["difficulty"] for i in items).items()):
        pct = 100 * v / len(items)
        print(f"  {k}: {v} ({pct:.1f}%)")
    print("\nQuestion type distribution:")
    for k, v in sorted(Counter(i["question_type"] for i in items).items()):
        pct = 100 * v / len(items)
        print(f"  {k}: {v} ({pct:.1f}%)")
    outcomes = Counter(i["outcome_code"] for i in items)
    print(f"\nUnique outcome codes: {len(outcomes)}")
    print(f"All have explanation: {all(i.get('explanation') for i in items)}")
    print(f"All have common_mistake: {all(i.get('common_mistake') for i in items)}")
    print(f"All have skill_tested: {all(i.get('skill_tested') for i in items)}")


def main():
    raw_path = INPUT
    if not raw_path.is_file():
        print(f"Input not found: {raw_path}. Run generate_biology30.py first.")
        raise SystemExit(1)

    with raw_path.open(encoding="utf-8") as f:
        pool = json.load(f)

    pool = [normalize(i) for i in pool]
    print(f"Loaded pool: {len(pool)} questions")

    selected = select_balanced(pool)
    selected = [normalize(i) for i in selected]

    errors = validate_all(selected)
    if errors:
        print(f"Validation failed: {len(errors)} errors")
        for idx, reasons in errors[:10]:
            print(f"  {idx}: {reasons}")
        raise SystemExit(1)

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print_report(selected)
    print(f"\nWrote production bank to {OUTPUT}")
    print("Validation: PASSED")
    print("Import-ready for: python -m app.database.question_import")


if __name__ == "__main__":
    main()
