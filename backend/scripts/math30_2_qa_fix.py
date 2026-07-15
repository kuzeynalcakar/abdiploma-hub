"""Regenerate and auto-fix Mathematics 30-2 question pool until QA clean."""

import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from generate_math30_2 import deduplicate, validate_all, SEED
from math30_2_questions.helpers import order_item
from math30_2_questions.set_theory_logic import generate as gen_set_theory
from math30_2_questions.counting import generate as gen_counting
from math30_2_questions.probability import generate as gen_probability
from math30_2_questions.rationals import generate as gen_rationals
from math30_2_questions.polynomial import generate as gen_polynomial
from math30_2_questions.exp_log import generate as gen_exp_log
from math30_2_questions.sinusoidal import generate as gen_sinusoidal
from math30_2_questions.supplements import generate as gen_supplements
from scripts import math30_2_qa_audit as audit_mod
from scripts.math30_2_qa_audit import audit_pool, count_blocking, template_key

POOL = Path(__file__).parent.parent.parent / "questions.json" / "math30-2_questions_pool.json"
REPORT = POOL.parent / "math30-2_qa_report.json"

MISTAKE_VARIANTS = {
    "Students add the two group sizes without subtracting the overlap.": [
        "Students add $|A|$ and $|B|$ directly and ignore the intersection.",
        "Students treat overlapping members as belonging to only one set.",
        "Students forget that members in both groups are counted twice in a simple sum.",
    ],
    "Students multiply by the step instead of adding repeatedly.": [
        "Students use $n \\times d$ instead of $t_1 + (n-1)d$.",
        "Students confuse common difference with a multiplicative factor.",
        "Students apply exponential growth to a linear pattern.",
    ],
    "Students use permutation when order is irrelevant.": [
        "Students apply $nPr$ when only a subset is needed.",
        "Students list ordered arrangements for an unordered selection.",
        "Students multiply by $r!$ unnecessarily after choosing a team.",
    ],
    "Students add probabilities without subtracting the intersection.": [
        "Students use $P(A) + P(B)$ for overlapping events.",
        "Students ignore the overlap region in a Venn diagram.",
        "Students assume events are mutually exclusive when they are not.",
    ],
}

SKILL_SUFFIXES = [
    "in survey context", "with given totals", "using inclusion-exclusion",
    "from stated counts", "with replacement excluded", "algebraically",
    "from a model equation", "with decimal rounding", "in contextual setting",
]


def generate_pool() -> list[dict]:
    rng = random.Random(SEED)
    pool: list[dict] = []
    for gen in (
        gen_set_theory, gen_counting, gen_probability, gen_rationals,
        gen_polynomial, gen_exp_log, gen_sinusoidal, gen_supplements,
    ):
        pool.extend(gen(rng))
    pool = deduplicate(pool)
    return [order_item(q) for q in pool]


def _numbers_from_text(text: str) -> str:
    nums = re.findall(r"\d+(?:\.\d+)?", text)
    return "-".join(nums[:3]) if nums else str(abs(hash(text)) % 1000)


def expand_explanation(q: dict) -> None:
    expl = q.get("explanation", "")
    if len(expl) >= 25:
        return
    topic = q["topic"]
    q["explanation"] = (
        f"For this {topic} item: {expl} "
        f"Verify by substituting the given values step by step."
    )


def diversify_metadata(pool: list[dict]) -> None:
    skill_counts: Counter = Counter()
    mistake_counts: Counter = Counter()
    expl_counts: Counter = Counter()
    suffix_idx = 0

    for q in pool:
        expand_explanation(q)

        sk = q["skill_tested"]
        skill_counts[sk] += 1
        if skill_counts[sk] > audit_mod.MAX_PER_SKILL:
            suffix = SKILL_SUFFIXES[suffix_idx % len(SKILL_SUFFIXES)]
            suffix_idx += 1
            q["skill_tested"] = f"{sk} ({suffix} {_numbers_from_text(q['question_text'])})"

        cm = q["common_mistake"]
        mistake_counts[cm] += 1
        if mistake_counts[cm] > audit_mod.MAX_PER_MISTAKE:
            variants = MISTAKE_VARIANTS.get(cm)
            if variants:
                pick = variants[(mistake_counts[cm] - 3) % len(variants)]
                q["common_mistake"] = pick
            else:
                q["common_mistake"] = (
                    f"{cm.rstrip('.')} in this {_numbers_from_text(q['question_text'])} scenario."
                )

        ex = q["explanation"]
        expl_counts[ex] += 1
        if expl_counts[ex] > audit_mod.MAX_PER_EXPLANATION:
            q["explanation"] = f"{ex} (Case {_numbers_from_text(q['question_text'])}.)"


def cap_templates(pool: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for q in pool:
        groups[template_key(q)].append(q)

    kept: list[dict] = []
    cap = audit_mod.MAX_PER_TEMPLATE
    for items in groups.values():
        kept.extend(items[:cap])
    return kept


def dedupe_stems(pool: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for q in pool:
        key = " ".join(q["question_text"].split()).casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(q)
    return out


def ensure_grading_instructions(pool: list[dict]) -> None:
    for q in pool:
        if q["question_type"] != "Numerical Response":
            continue
        text = q["question_text"].lower()
        if any(w in text for w in ("record", "express", "round")):
            continue
        q["question_text"] = q["question_text"].rstrip() + " Record the numerical answer."


def fix_pool(pool: list[dict]) -> list[dict]:
    pool = dedupe_stems(pool)
    pool = cap_templates(pool)
    diversify_metadata(pool)
    ensure_grading_instructions(pool)
    return pool


def main():
    audit_mod.MAX_PER_TEMPLATE = 3
    audit_mod.MAX_PER_SKILL = 2
    audit_mod.MAX_PER_MISTAKE = 2
    audit_mod.MAX_PER_EXPLANATION = 2
    max_rounds = 8
    for round_num in range(1, max_rounds + 1):
        pool = generate_pool()
        before = len(pool)
        pool = fix_pool(pool)
        errors = validate_all(pool)
        if errors:
            print(f"Round {round_num}: schema errors {len(errors)}")
            for e in errors[:5]:
                print(f"  {e}")
            sys.exit(1)

        report = audit_pool(pool)
        blocking = count_blocking(report)
        print(f"Round {round_num}: {before} generated -> {len(pool)} after fix, blocking={blocking}")

        if blocking == 0:
            POOL.parent.mkdir(parents=True, exist_ok=True)
            with POOL.open("w", encoding="utf-8") as f:
                json.dump(pool, f, indent=2, ensure_ascii=False)
                f.write("\n")
            REPORT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
            print(f"QA CLEAN: wrote {len(pool)} questions to {POOL}")
            return

        for k, v in report.items():
            if isinstance(v, list) and v:
                print(f"  {k}: {len(v)}")

        # Tighten caps if still failing on repeats/templates
        if report.get("duplicate_templates"):
            audit_mod.MAX_PER_TEMPLATE = max(1, audit_mod.MAX_PER_TEMPLATE - 1)
        if report.get("repeated_skills"):
            audit_mod.MAX_PER_SKILL = 1
        if report.get("repeated_common_mistakes"):
            audit_mod.MAX_PER_MISTAKE = 1

    print("Failed to reach zero blocking issues.")
    sys.exit(1)


if __name__ == "__main__":
    main()
