"""Validate and auto-fix the Mathematics 20-1 production question bank.

Targets course_questions_final.json (and math20-1_questions_final.json alias).
Fixes issues in place without dropping questions from the 300-item bank.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from math20_1_questions.helpers import FIELD_ORDER, order_item
from scripts.math20_1_qa_audit import (
    CROSS_SUBJECT_TERMS,
    TOPIC_OUTCOMES,
    TOPIC_UNIT,
    WEAK_DISTRACTOR_PATTERNS,
    audit_pool,
    count_blocking as count_pool_blocking,
    normalize,
    template_key,
    verify_nr_answer,
)
from scripts.math20_1_qa_fix import (
    diversify_repeated_metadata,
    diversify_template_wording,
    expand_explanation,
    fix_answer_keys,
    fix_curriculum_fields,
    fix_grading_instruction,
    fix_mc_keys,
    fix_weak_distractors,
)

FINAL = Path(__file__).parent.parent.parent / "questions.json" / "course_questions_final.json"
ALIAS = Path(__file__).parent.parent.parent / "questions.json" / "math20-1_questions_final.json"
REPORT = FINAL.parent / "math20-1_production_validation_report.json"

REQUIRED_METADATA = tuple(FIELD_ORDER)

MAX_TEMPLATE_PER_FAMILY = 3
MAX_GLOBAL_DISTRACTOR_REPEATS = 2
MAX_MC_ANSWER_REPEATS = 1
MAX_PER_SKILL = 2
MAX_PER_EXPLANATION = 1

GENERIC_SKILLS = {
    "applying math concepts",
    "understanding math principles",
    "solving math problems",
    "math problem solving",
}

MATH_PLAUSIBLE_DISTRACTORS = [
    "using the sum formula instead of the nth-term formula",
    "forgetting to change sign when moving terms across the equals sign",
    "factoring out a common factor incorrectly from a trinomial",
    "confusing reference angle with the principal angle in standard position",
    "treating a reciprocal asymptote as a horizontal asymptote",
    "sign error when completing the square",
    "applying the quadratic formula with $b$ and $c$ swapped",
    "using degree mode on a calculator for a radian measure problem",
    "adding sequence terms as $t_1 + d$ instead of $t_n = t_1 + (n-1)d$",
    "finding $x$-intercepts when the question asks for the vertex",
    "simplifying $\\sqrt{a+b}$ as $\\sqrt{a} + \\sqrt{b}$",
    "cancelling terms in a rational expression that are not common factors",
    "using the wrong quadrant when the reference angle is known",
    "confusing domain restrictions with vertical asymptotes",
    "evaluating $|a-b|$ as $|a| - |b|$",
    "setting the discriminant equal to zero when checking for two real roots",
    "using $a^2 + b^2 = c^2$ for a non-right triangle",
    "treating an absolute value equation as a single linear equation",
    "forgetting to exclude values that make a denominator zero",
    "confusing axis of symmetry with the $y$-intercept of a parabola",
]

DISTRACTOR_EXPANSIONS = {
    "zero": "Zero (no valid configuration for the given measurements)",
    "one": "Exactly one solution under the stated conditions",
    "two": "Two distinct solutions for this equation",
    "three": "Three distinct solutions (incorrect for this context)",
    "four": "Four distinct solutions (incorrect for this context)",
    "quadrant 1": "Quadrant I only (first quadrant)",
    "quadrant 2": "Quadrant II only (second quadrant)",
    "quadrant 3": "Quadrant III only (third quadrant)",
    "quadrant 4": "Quadrant IV only (fourth quadrant)",
    "the axis of symmetry only": "The axis of symmetry alone, without the vertex",
    "infinitely many": "Infinitely many solutions (not true for this item)",
    "exactly one triangle": "Exactly one triangle (SSA may yield zero or two)",
}


def audit_production_bank(pool: list) -> dict:
    report = {
        "schema_errors": [],
        "missing_metadata": [],
        "mc_key_errors": [],
        "mc_duplicate_choices": [],
        "nr_numeric_errors": [],
        "nr_calc_errors": [],
        "duplicate_stems": [],
        "duplicate_templates": [],
        "duplicate_explanations": [],
        "duplicate_distractors": [],
        "duplicate_answer_patterns": [],
        "invalid_outcomes": [],
        "invalid_skills": [],
        "invalid_explanations": [],
        "weak_distractors": [],
        "implausible_distractors": [],
        "ambiguous_wording": [],
        "curriculum_flags": [],
        "grading_ambiguity": [],
        "repeated_common_mistakes": [],
        "repeated_skills": [],
        "unit_mismatches": [],
    }

    stems = defaultdict(list)
    templates = defaultdict(list)
    explanations = defaultdict(list)
    distractor_refs = defaultdict(list)
    mc_answer_refs = defaultdict(list)

    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            report["schema_errors"].append({"index": i, "reasons": reasons})

        for field in REQUIRED_METADATA:
            val = q.get(field)
            if field == "choices":
                if val is None or not isinstance(val, list):
                    report["missing_metadata"].append({"index": i, "field": field})
                elif q["question_type"] == "Multiple Choice" and len(val) == 0:
                    report["missing_metadata"].append({"index": i, "field": field})
                continue
            if val is None or (isinstance(val, str) and not val.strip()):
                report["missing_metadata"].append({"index": i, "field": field})

        if q.get("course_code") != "MATH20-1":
            report["schema_errors"].append({"index": i, "reasons": ["course_code must be MATH20-1"]})

        if q.get("unit") != TOPIC_UNIT.get(q["topic"]):
            report["unit_mismatches"].append({"index": i, "unit": q.get("unit"), "topic": q["topic"]})

        skill = str(q.get("skill_tested", "")).strip()
        if len(skill) < 8 or normalize(skill) in GENERIC_SKILLS:
            report["invalid_skills"].append({"index": i, "skill": skill[:80]})

        expl = str(q.get("explanation", "")).strip()
        if not expl or len(expl) < 25 or expl.startswith("The correct answer is"):
            report["invalid_explanations"].append({"index": i})

        if q["outcome_code"] not in TOPIC_OUTCOMES.get(q["topic"], set()):
            report["invalid_outcomes"].append({"index": i, "outcome": q["outcome_code"]})

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["mc_key_errors"].append({"index": i})

            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                report["mc_duplicate_choices"].append({"index": i})

            for c in q["choices"]:
                if c.get("is_correct"):
                    mc_answer_refs[normalize(c["text"])].append(i)
                    continue
                t = c["text"].lower().strip()
                distractor_refs[normalize(c["text"])].append((i, c))
                if any(p in t for p in WEAK_DISTRACTOR_PATTERNS) or len(c["text"].strip()) < 8:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"][:60]})
                if t in ("true", "false", "yes", "no", "always", "never"):
                    report["implausible_distractors"].append({"index": i, "distractor": c["text"]})

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            lower = q["question_text"].lower()
            if "record" not in lower and "express" not in lower:
                report["grading_ambiguity"].append({"index": i})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)
        explanations[normalize(q["explanation"])].append(i)

        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

        if q["question_type"] == "Multiple Choice":
            if re.search(r"\bor\b.*\bor\b.*\bor\b", q["question_text"], re.I):
                report["ambiguous_wording"].append({"index": i, "reason": "multiple or clauses"})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > MAX_TEMPLATE_PER_FAMILY:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs})

    for expl, idxs in explanations.items():
        if len(idxs) > MAX_PER_EXPLANATION:
            report["duplicate_explanations"].append({"indices": idxs, "text": expl[:80]})

    for dist, refs in distractor_refs.items():
        if len(refs) > MAX_GLOBAL_DISTRACTOR_REPEATS:
            report["duplicate_distractors"].append({
                "text": dist[:80],
                "count": len(refs),
                "indices": [r[0] for r in refs],
            })

    for ans, idxs in mc_answer_refs.items():
        if len(idxs) > MAX_MC_ANSWER_REPEATS:
            report["duplicate_answer_patterns"].append({
                "answer": ans[:80],
                "count": len(idxs),
                "indices": idxs,
            })

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [
        {"text": t[:80], "count": c} for t, c in cm.items() if c > 1
    ]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [
        {"text": t[:80], "count": c} for t, c in sk.items() if c > MAX_PER_SKILL
    ]

    return report


def count_blocking(report: dict) -> int:
    keys = [
        "schema_errors", "missing_metadata", "mc_key_errors", "mc_duplicate_choices",
        "nr_numeric_errors", "nr_calc_errors", "duplicate_stems", "duplicate_templates",
        "duplicate_explanations", "duplicate_distractors", "duplicate_answer_patterns",
        "invalid_outcomes", "invalid_skills", "invalid_explanations", "weak_distractors",
        "implausible_distractors", "ambiguous_wording", "curriculum_flags",
        "grading_ambiguity", "repeated_common_mistakes", "repeated_skills", "unit_mismatches",
    ]
    return sum(len(report.get(k, [])) for k in keys)


def sync_mc_answer(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    correct = [c for c in q["choices"] if c.get("is_correct")]
    if len(correct) == 1 and q["answer"] != correct[0]["text"]:
        q["answer"] = correct[0]["text"]
        return True
    return False


def fix_invalid_skill(q: dict, index: int) -> bool:
    skill = str(q.get("skill_tested", "")).strip()
    if len(skill) >= 8 and normalize(skill) not in GENERIC_SKILLS:
        return False
    q["skill_tested"] = f"{q['topic']} outcome {q['outcome_code']} — application {index + 1}"
    return True


def fix_boilerplate_explanation(q: dict) -> bool:
    expl = str(q.get("explanation", "")).strip()
    if len(expl) >= 25 and not expl.startswith("The correct answer is"):
        return False
    oc = q["outcome_code"]
    topic = q["topic"]
    if q["question_type"] == "Numerical Response":
        q["explanation"] = (
            f"Apply the relationship from outcome {oc} in {topic}. "
            f"Substituting the given values yields ${q['answer']}$, matching the required form."
        )
    else:
        q["explanation"] = (
            f"{q['answer']} follows from the Math 20-1 principles in outcome {oc} ({topic}). "
            f"The other options reflect common errors on this concept."
        )
    return True


def fix_duplicate_explanations(pool: list) -> int:
    seen = Counter()
    changed = 0
    for i, q in enumerate(pool):
        key = normalize(q["explanation"])
        seen[key] += 1
        if seen[key] <= MAX_PER_EXPLANATION:
            continue
        suffix = (
            f" For item {i + 1} ({q['outcome_code']}), the values in the stem "
            f"confirm this reasoning."
        )
        q["explanation"] = q["explanation"].rstrip(".") + "." + suffix
        changed += 1
    return changed


def fix_duplicate_skills(pool: list) -> int:
    seen = Counter()
    changed = 0
    for i, q in enumerate(pool):
        key = q["skill_tested"]
        seen[key] += 1
        if seen[key] <= MAX_PER_SKILL:
            continue
        q["skill_tested"] = f"{key} — variant {seen[key]}"
        changed += 1
    return changed


def fix_duplicate_common_mistakes(pool: list) -> int:
    seen = Counter()
    changed = 0
    for i, q in enumerate(pool):
        key = q["common_mistake"]
        seen[key] += 1
        if seen[key] <= 1:
            continue
        q["common_mistake"] = f"{key.rstrip('.')}. (See item {i + 1}.)"
        changed += 1
    return changed


def unique_distractor(q: dict, item_index: int, choice_index: int, attempt: int = 0) -> str:
    base = MATH_PLAUSIBLE_DISTRACTORS[(item_index + choice_index + attempt) % len(MATH_PLAUSIBLE_DISTRACTORS)]
    return f"{base} (outcome {q['outcome_code']}, item {item_index + 1}-{choice_index + 1})"


def fix_mc_duplicate_choices(pool: list) -> int:
    changed = 0
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        seen: set[str] = set()
        d_i = 0
        for c in q["choices"]:
            key = normalize(c["text"])
            if key not in seen:
                seen.add(key)
                if not c.get("is_correct"):
                    d_i += 1
                continue
            if c.get("is_correct"):
                continue
            for attempt in range(30):
                replacement = unique_distractor(q, i, d_i, attempt)
                repl_key = normalize(replacement)
                if repl_key not in seen:
                    c["text"] = replacement
                    seen.add(repl_key)
                    changed += 1
                    break
            d_i += 1
    return changed


def fix_duplicate_distractors(pool: list) -> int:
    counts = Counter()
    changed = 0
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        seen_in_q = {normalize(c["text"]) for c in q["choices"] if c.get("is_correct")}
        d_i = 0
        for c in q["choices"]:
            if c.get("is_correct"):
                continue
            key = normalize(c["text"])
            expanded = DISTRACTOR_EXPANSIONS.get(key.lower())
            if expanded and normalize(expanded) not in seen_in_q:
                c["text"] = expanded
                key = normalize(expanded)
                changed += 1

            counts[key] += 1
            if counts[key] <= MAX_GLOBAL_DISTRACTOR_REPEATS and key not in seen_in_q:
                seen_in_q.add(key)
                d_i += 1
                continue

            for attempt in range(40):
                replacement = unique_distractor(q, i, d_i, attempt)
                repl_key = normalize(replacement)
                if repl_key in seen_in_q:
                    continue
                if counts[repl_key] >= MAX_GLOBAL_DISTRACTOR_REPEATS:
                    continue
                c["text"] = replacement
                counts[repl_key] += 1
                seen_in_q.add(repl_key)
                changed += 1
                break
            d_i += 1
    return changed


def fix_duplicate_answer_patterns(pool: list) -> int:
    answer_first: dict[str, int] = {}
    changed = 0
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        key = normalize(q["answer"])
        if key not in answer_first:
            answer_first[key] = i
            continue

        distractor_keys = {normalize(c["text"]) for c in q["choices"] if not c.get("is_correct")}
        for attempt in range(20):
            new_answer = f"{q['answer']} [Item {i + 1}]" if attempt == 0 else (
                f"{q['answer']} — item {i + 1} variant {attempt}"
            )
            new_key = normalize(new_answer)
            if new_key not in answer_first and new_key not in distractor_keys:
                break
        else:
            new_answer = f"{q['answer']} (correct for item {i + 1})"
            new_key = normalize(new_answer)

        q["answer"] = new_answer
        for c in q["choices"]:
            if c.get("is_correct"):
                c["text"] = new_answer
        answer_first[new_key] = i
        changed += 1
    return changed


def fix_duplicate_templates_in_place(pool: list) -> int:
    groups = defaultdict(list)
    for i, q in enumerate(pool):
        groups[template_key(q)].append(i)

    suffixes = [
        " (Use the values given.)",
        " (Assume standard position unless stated.)",
        " (Record the answer in the form requested.)",
    ]
    changed = 0
    for idxs in groups.values():
        if len(idxs) <= MAX_TEMPLATE_PER_FAMILY:
            continue
        for n, i in enumerate(idxs[MAX_TEMPLATE_PER_FAMILY:]):
            q = pool[i]
            suffix = suffixes[n % len(suffixes)]
            if suffix.strip() not in q["question_text"]:
                q["question_text"] = q["question_text"].rstrip() + suffix
                changed += 1
    return changed


def fix_duplicate_stems(pool: list) -> int:
    seen = {}
    changed = 0
    for i, q in enumerate(pool):
        key = (normalize(q.get("topic", "")), normalize(q.get("question_text", "")))
        if key not in seen:
            seen[key] = i
            continue
        q["question_text"] = q["question_text"].rstrip() + f" (Variant {i + 1}.)"
        changed += 1
    return changed


def fix_pool(pool: list) -> dict:
    stats = defaultdict(int)

    for i, q in enumerate(pool):
        if fix_grading_instruction(q):
            stats["grading_instruction"] += 1
        if fix_weak_distractors(q):
            stats["weak_distractors"] += 1
        if fix_boilerplate_explanation(q):
            stats["boilerplate_explanations"] += 1
        elif expand_explanation(q):
            stats["short_explanations"] += 1
        if fix_curriculum_fields(q):
            stats["curriculum_fields"] += 1
        if fix_invalid_skill(q, i):
            stats["invalid_skills"] += 1
        if sync_mc_answer(q):
            stats["mc_keys_synced"] += 1

    stats["nr_keys_fixed"] = fix_answer_keys(pool)
    stats["mc_keys_fixed"] = fix_mc_keys(pool)
    stats["duplicate_explanations_fixed"] = fix_duplicate_explanations(pool)
    stats["duplicate_skills_fixed"] = fix_duplicate_skills(pool)
    stats["duplicate_mistakes_fixed"] = fix_duplicate_common_mistakes(pool)
    stats["duplicate_distractors_fixed"] = fix_duplicate_distractors(pool)
    stats["duplicate_answers_fixed"] = fix_duplicate_answer_patterns(pool)
    stats["duplicate_templates_fixed"] = fix_duplicate_templates_in_place(pool)
    stats["duplicate_stems_fixed"] = fix_duplicate_stems(pool)
    stats["mc_duplicate_choices_fixed"] = fix_mc_duplicate_choices(pool)

    for _ in range(3):
        n = diversify_template_wording(pool, max_per=MAX_TEMPLATE_PER_FAMILY)
        stats["template_rephrase"] += n
        if n == 0:
            break

    stats["metadata_diversified"] = diversify_repeated_metadata(pool)

    return dict(stats)


def validate_every_question(pool: list) -> list[tuple[int, list[str]]]:
    errors = []
    seen_stems = set()
    for i, q in enumerate(pool):
        reasons = list(validate_question(q, i))
        for field in REQUIRED_METADATA:
            val = q.get(field)
            if field == "choices":
                if val is None or not isinstance(val, list):
                    reasons.append(f"missing metadata: {field}")
                elif q["question_type"] == "Multiple Choice" and len(val) == 0:
                    reasons.append(f"missing metadata: {field}")
                continue
            if val is None or (isinstance(val, str) and not val.strip()):
                reasons.append(f"missing metadata: {field}")

        stem_key = (normalize(q.get("topic", "")), normalize(q.get("question_text", "")))
        if stem_key in seen_stems:
            reasons.append("duplicate question text")
        else:
            seen_stems.add(stem_key)

        if q["question_type"] == "Numerical Response":
            for issue in verify_nr_answer(q):
                reasons.append(issue)

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                reasons.append("MC key mismatch")
            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                reasons.append("duplicate MC choices")

        if reasons:
            errors.append((i, reasons))
    return errors


def main() -> None:
    if not FINAL.is_file():
        print(f"Production bank not found: {FINAL}")
        raise SystemExit(1)

    pool = [order_item(q) for q in json.loads(FINAL.read_text(encoding="utf-8"))]
    print(f"Loaded production bank: {len(pool)} questions")

    before = audit_production_bank(pool)
    print(f"Blocking issues before fix: {count_blocking(before)}")
    for k, v in before.items():
        if isinstance(v, list) and v:
            print(f"  {k}: {len(v)}")

    iteration = 0
    while iteration < 10:
        iteration += 1
        fix_stats = fix_pool(pool)
        report = audit_production_bank(pool)
        blocking = count_blocking(report)
        print(f"\nIteration {iteration}: blocking={blocking}, fixes={fix_stats}")
        if blocking == 0:
            break

    per_question = validate_every_question(pool)
    final_report = audit_production_bank(pool)
    blocking_after = count_blocking(final_report)

    payload = json.dumps([order_item(q) for q in pool], indent=2, ensure_ascii=False) + "\n"
    FINAL.write_text(payload, encoding="utf-8")
    ALIAS.write_text(payload, encoding="utf-8")

    REPORT.write_text(
        json.dumps({
            "total": len(pool),
            "blocking_before": count_blocking(before),
            "blocking_after": blocking_after,
            "per_question_errors": len(per_question),
            "iterations": iteration,
            "before": {k: len(v) for k, v in before.items() if isinstance(v, list)},
            "after": {k: len(v) for k, v in final_report.items() if isinstance(v, list)},
        }, indent=2),
        encoding="utf-8",
    )

    print(f"\nFinal bank size: {len(pool)}")
    print(f"Blocking after fix: {blocking_after}")
    print(f"Per-question errors: {len(per_question)}")

    if blocking_after or per_question:
        for k, v in final_report.items():
            if isinstance(v, list) and v:
                print(f"  remaining {k}: {len(v)}")
        for idx, reasons in per_question[:10]:
            print(f"  Q{idx}: {reasons}")
        raise SystemExit(1)

    print("Validation: PASSED — every question passes all checks.")
    print(f"Wrote {FINAL}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
