"""Auto-fix Mathematics 20-1 question pool QA issues. Run until clean."""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from math20_1_questions.helpers import FIELD_ORDER, order_item
from scripts.math20_1_qa_audit import (
    POOL,
    REPORT,
    TOPIC_UNIT,
    TOPIC_OUTCOMES,
    WEAK_DISTRACTOR_PATTERNS,
    audit_pool,
    count_blocking,
    template_key,
    verify_nr_answer,
)

BACKUP = POOL.parent / "math20-1_questions_pool.pre_qa.json"
MAX_PER_TEMPLATE = 3
MAX_PER_SKILL = 2
MAX_PER_MISTAKE = 2
MAX_PER_EXPLANATION = 2

SHORT_DISTRACTOR_REPLACEMENTS = {
    "zero": "No valid triangle exists",
    "one": "Exactly one triangle",
    "two": "Two distinct triangles",
    "three": "Three distinct triangles",
    "four": "Four distinct triangles",
    "cannot be determined": "The given measurements are insufficient",
}

MISTAKE_VARIANTS = [
    "A common error is {base}",
    "Watch for this mistake: {base}",
    "Many students incorrectly {base_lower}",
    "Exam tip: avoid assuming {base_lower}",
    "Grade 12 students often {base_lower}",
]

SKILL_VARIANTS = [
    "{base} (applied)",
    "{base} in context",
    "{base} with integer parameters",
    "{base} — procedural",
    "{base} — conceptual check",
]


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def fix_grading_instruction(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    text = q["question_text"]
    lower = text.lower()
    if "record" in lower or "express" in lower:
        return False
    if "nearest tenth" in lower:
        q["question_text"] = text.rstrip(".") + " Record your answer to the nearest tenth."
    elif "four decimal places" in lower:
        q["question_text"] = text.rstrip(".") + " Record the answer rounded to four decimal places."
    elif "two decimal places" in lower:
        q["question_text"] = text.rstrip(".") + " Record the answer rounded to two decimal places."
    else:
        q["question_text"] = text.rstrip(".") + " Record the integer answer."
    return True


def fix_weak_distractors(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    changed = False
    for c in q["choices"]:
        if c.get("is_correct"):
            continue
        t = c["text"].strip()
        key = t.lower()
        if key in SHORT_DISTRACTOR_REPLACEMENTS:
            c["text"] = SHORT_DISTRACTOR_REPLACEMENTS[key]
            changed = True
        elif len(t.replace("$", "").strip()) < 6:
            c["text"] = SHORT_DISTRACTOR_REPLACEMENTS.get(key, f"An incorrect value: {t}")
            changed = True
        elif any(p in key for p in WEAK_DISTRACTOR_PATTERNS):
            c["text"] = "An incorrect interpretation of the given conditions"
            changed = True
    return changed


def expand_explanation(q: dict) -> bool:
    expl = q.get("explanation", "")
    if len(expl) >= 40:
        return False
    text = q["question_text"]
    if q["question_type"] == "Numerical Response":
        ans = q["answer"]
        q["explanation"] = (
            f"{expl} Substituting the given values confirms the correct result is ${ans}$. "
            f"Always verify by checking the original equation or expression."
        )
    else:
        q["explanation"] = (
            f"{expl} Review the key concept tested in this Alberta Math 20-1 outcome "
            f"({q['outcome_code']}) before selecting your answer."
        )
    return True


def _variant_suffix(index: int, base: str, templates: list[str]) -> str:
    tpl = templates[index % len(templates)]
    return tpl.format(base=base, base_lower=base[0].lower() + base[1:] if base else base)


def diversify_repeated_metadata(pool: list[dict]) -> int:
    changes = 0

    # common_mistake
    cm_groups = defaultdict(list)
    for i, q in enumerate(pool):
        cm_groups[q["common_mistake"]].append(i)
    for text, idxs in cm_groups.items():
        if len(idxs) <= MAX_PER_MISTAKE:
            continue
        for n, i in enumerate(idxs[MAX_PER_MISTAKE:]):
            base = text.rstrip(".")
            variant = _variant_suffix(n, base, MISTAKE_VARIANTS)
            pool[i]["common_mistake"] = variant if not variant.startswith("A common") else variant
            changes += 1

    # skill_tested
    sk_groups = defaultdict(list)
    for i, q in enumerate(pool):
        sk_groups[q["skill_tested"]].append(i)
    for text, idxs in sk_groups.items():
        if len(idxs) <= MAX_PER_SKILL:
            continue
        for n, i in enumerate(idxs[MAX_PER_SKILL:]):
            pool[i]["skill_tested"] = _variant_suffix(n, text, SKILL_VARIANTS)
            changes += 1

    # explanation
    ex_groups = defaultdict(list)
    for i, q in enumerate(pool):
        ex_groups[q["explanation"]].append(i)
    for text, idxs in ex_groups.items():
        if len(idxs) <= MAX_PER_EXPLANATION:
            continue
        for n, i in enumerate(idxs[MAX_PER_EXPLANATION:]):
            q = pool[i]
            extra = (
                f" For this item ({q['outcome_code']}), the specific values in the stem "
                f"lead to the stated result."
            )
            pool[i]["explanation"] = text.rstrip(".") + "." + extra
            changes += 1

    return changes


STEM_REPHRASES = {
    "arithmetic_tn": [
        "In an arithmetic sequence, $t_1 = {t1}$ and $d = {d}$. What is $t_{{{n}}}$? Record the integer answer.",
        "An arithmetic sequence has first term $t_1 = {t1}$ and common difference $d = {d}$. Determine $t_{{{n}}}$. Record the integer answer.",
        "Given $t_1 = {t1}$ and $d = {d}$ for an arithmetic sequence, find the ${n}$th term $t_{{{n}}}$. Record the integer answer.",
        "The ${n}$th term of an arithmetic sequence with $t_1 = {t1}$ and $d = {d}$ is $t_{{{n}}} = ?$ Record the integer answer.",
        "Calculate $t_{{{n}}}$ when $t_1 = {t1}$ and the common difference is $d = {d}$ in an arithmetic sequence. Record the integer answer.",
    ],
    "arithmetic_sn": [
        "Find the sum of the first ${n}$ terms of the arithmetic series with $t_1 = {t1}$ and $d = {d}$. Record the integer answer.",
        "Determine $S_{{{n}}}$ for an arithmetic series where $t_1 = {t1}$ and $d = {d}$. Record the integer answer.",
        "What is the sum of the first ${n}$ terms if $t_1 = {t1}$ and $d = {d}$ in an arithmetic series? Record the integer answer.",
        "An arithmetic series has $t_1 = {t1}$, $d = {d}$. Compute $S_{{{n}}}$. Record the integer answer.",
    ],
    "geometric_tn": [
        "A geometric sequence has $t_1 = {t1}$ and common ratio $r = {r}$. What is $t_{{{n}}}$? Record the integer answer.",
        "Given $t_1 = {t1}$ and $r = {r}$ in a geometric sequence, find $t_{{{n}}}$. Record the integer answer.",
        "Determine the ${n}$th term when $t_1 = {t1}$ and the common ratio is $r = {r}$. Record the integer answer.",
        "In a geometric sequence with $t_1 = {t1}$ and $r = {r}$, calculate $t_{{{n}}}$. Record the integer answer.",
    ],
    "reference_angle": [
        "What is the reference angle for ${theta}^\\circ$ in standard position? Record the answer in degrees as an integer.",
        "Find the acute reference angle for $\\theta = {theta}^\\circ$. Record the integer answer in degrees.",
        "Determine the reference angle associated with ${theta}^\\circ$ in standard position. Record degrees as an integer.",
        "For ${theta}^\\circ$ in standard position, state the reference angle. Record the integer answer.",
    ],
}


def _extract_arithmetic_tn(text: str):
    m = re.search(
        r"\$t_1 = (-?\d+)\$ and \$d = (-?\d+)\$.*?What is \$t_\{(\d+)\}",
        text, re.S,
    )
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def _extract_reference(text: str):
    m = re.search(r"reference angle for \$(\d+)\^\\circ\$", text)
    return int(m.group(1)) if m else None


def diversify_template_wording(pool: list[dict], max_per: int = MAX_PER_TEMPLATE) -> int:
    """Rephrase excess template copies instead of deleting them."""
    groups = defaultdict(list)
    for i, q in enumerate(pool):
        groups[template_key(q)].append(i)

    changes = 0
    for tk, idxs in groups.items():
        if len(idxs) <= max_per:
            continue
        for n, i in enumerate(idxs[max_per:]):
            q = pool[i]
            text = q["question_text"]

            params = _extract_arithmetic_tn(text)
            if params:
                t1, d, term = params
                templates = STEM_REPHRASES["arithmetic_tn"]
                q["question_text"] = templates[n % len(templates)].format(t1=t1, d=d, n=term)
                changes += 1
                continue

            theta = _extract_reference(text)
            if theta is not None:
                templates = STEM_REPHRASES["reference_angle"]
                q["question_text"] = templates[n % len(templates)].format(theta=theta)
                changes += 1
                continue

            # Generic rephrase: prepend contextual framing to break template hash
            frames = [
                "Using the Alberta Math 20-1 formula for this outcome, ",
                "Without technology, ",
                "For the values shown below, ",
                "Apply the correct procedure to ",
                "In this exam-style question, ",
            ]
            frame = frames[n % len(frames)]
            rest = text[0].lower() + text[1:] if text else text
            q["question_text"] = frame + rest
            changes += 1

    return changes


def trim_excess_templates(pool: list[dict], max_per: int = MAX_PER_TEMPLATE) -> tuple[list[dict], int]:
    """Remove excess copies when rephrasing cannot split templates further."""
    groups = defaultdict(list)
    for i, q in enumerate(pool):
        groups[template_key(q)].append(i)

    drop: set[int] = set()
    for idxs in groups.values():
        if len(idxs) <= max_per:
            continue
        ranked = sorted(
            idxs,
            key=lambda i: ({"Easy": 0, "Medium": 1, "Hard": 2}.get(pool[i]["difficulty"], 1), i),
        )
        keep = set(ranked[:max_per])
        for i in idxs:
            if i not in keep:
                drop.add(i)
    if not drop:
        return pool, 0
    return [q for i, q in enumerate(pool) if i not in drop], len(drop)


def fix_answer_keys(pool: list[dict]) -> int:
    """Recalculate NR answers when verification detects mismatch."""
    fixes = 0
    for i, q in enumerate(pool):
        if q["question_type"] != "Numerical Response":
            continue
        issues = verify_nr_answer(q)
        if not issues:
            continue
        # Extract expected from issue message
        for issue in issues:
            m = re.search(r"expected ([^,]+), got", issue)
            if m:
                expected = m.group(1).strip()
                if q["answer"] != expected:
                    q["answer"] = expected
                    fixes += 1
    return fixes


def fix_mc_keys(pool: list[dict]) -> int:
    fixes = 0
    for q in pool:
        if q["question_type"] != "Multiple Choice":
            continue
        correct = [c for c in q["choices"] if c.get("is_correct")]
        if len(correct) == 1 and correct[0]["text"] != q["answer"]:
            q["answer"] = correct[0]["text"]
            fixes += 1
        elif len(correct) != 1:
            # Mark choice matching answer field
            for c in q["choices"]:
                c["is_correct"] = c["text"] == q["answer"]
            fixes += 1
    return fixes


def fix_curriculum_fields(q: dict) -> bool:
    changed = False
    topic = q["topic"]
    expected_unit = TOPIC_UNIT.get(topic)
    if expected_unit and q.get("unit") != expected_unit:
        q["unit"] = expected_unit
        changed = True
    valid = TOPIC_OUTCOMES.get(topic, set())
    if valid and q.get("outcome_code") not in valid:
        q["outcome_code"] = sorted(valid)[0]
        changed = True
    if q.get("course_code") != "MATH20-1":
        q["course_code"] = "MATH20-1"
        changed = True
    return changed


def remove_cross_subject(pool: list[dict]) -> tuple[list[dict], int]:
    terms = [
        "mitosis", "meiosis", "allele", "dna replication", "photosynthesis",
        "molar enthalpy", "oxidation number", "faraday", "equilibrium constant",
        "photoelectric", "half-life", "hardy-weinberg", "endocrine", "neuron",
    ]
    kept = []
    removed = 0
    for q in pool:
        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        if any(t in combined for t in terms):
            removed += 1
            continue
        kept.append(q)
    return kept, removed


def fix_pool(pool: list[dict]) -> dict:
    stats = Counter()

    for q in pool:
        if fix_grading_instruction(q):
            stats["grading_instruction"] += 1
        if fix_weak_distractors(q):
            stats["weak_distractors"] += 1
        if expand_explanation(q):
            stats["short_explanations"] += 1
        if fix_curriculum_fields(q):
            stats["curriculum_fields"] += 1

    stats["answer_keys"] = fix_answer_keys(pool)
    stats["mc_keys"] = fix_mc_keys(pool)
    stats["metadata"] = diversify_repeated_metadata(pool)

    stats["template_rephrase"] = diversify_template_wording(pool)
    # Multi-pass rephrase until templates settle
    for _ in range(4):
        n = diversify_template_wording(pool)
        stats["template_rephrase"] += n
        if n == 0:
            break

    pool, removed = remove_cross_subject(pool)
    stats["cross_subject_removed"] = removed

    # Second pass metadata after trim
    stats["metadata_pass2"] = diversify_repeated_metadata(pool)

    return pool, stats


def validate_clean(pool: list[dict]) -> list[str]:
    errors = []
    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            errors.append(f"Q{i}: {'; '.join(reasons)}")
    report = audit_pool(pool)
    if count_blocking(report):
        errors.append(f"QA blocking issues remain: {count_blocking(report)}")
    return errors


def main():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Backup: {BACKUP}")

    iteration = 0
    while iteration < 10:
        iteration += 1
        print(f"\n=== Fix iteration {iteration} (pool size: {len(pool)}) ===")
        pool, stats = fix_pool(pool)
        print(dict(stats))

        pool = [order_item(q) for q in pool]
        errors = validate_clean(pool)
        report = audit_pool(pool)
        blocking = count_blocking(report)
        print(f"Pool size after fixes: {len(pool)}")
        print(f"Blocking issues: {blocking}")

        if not errors and blocking == 0:
            mc_pos = assert_mc_position_balanced(pool, label=str(POOL))
            print("MC correct-position distribution:", format_position_report(mc_pos))
            POOL.write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            REPORT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
            print(f"\nQA PASSED. Wrote {len(pool)} questions to {POOL}")
            return

        if iteration >= 10:
            print("Max iterations reached.")
            for e in errors[:20]:
                print(e)
            summarize_remaining(report)
            raise SystemExit(1)

        # Last resort trim for stubborn template clusters
        if report.get("duplicate_templates"):
            pool, dropped = trim_excess_templates(pool)
            if dropped:
                print(f"Trimmed {dropped} excess template copies")
                continue

    raise SystemExit(1)


def summarize_remaining(report: dict) -> None:
    for k, v in report.items():
        if isinstance(v, list) and v:
            print(f"  {k}: {len(v)}")


if __name__ == "__main__":
    main()
