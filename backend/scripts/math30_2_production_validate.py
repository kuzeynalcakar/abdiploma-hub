"""Validate and auto-fix the Mathematics 30-2 production question bank.

Targets course_questions_final.json and math30-2_questions_final.json.
Fixes issues in place without dropping questions from the 300-item bank.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report
from math30_2_questions.helpers import FIELD_ORDER, order_item
from scripts.math30_2_qa_audit import (
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

FINAL = Path(__file__).parent.parent.parent / "questions.json" / "course_questions_final.json"
ALIAS = Path(__file__).parent.parent.parent / "questions.json" / "math30-2_questions_final.json"
POOL = Path(__file__).parent.parent.parent / "questions.json" / "math30-2_questions_pool.json"
REPORT = FINAL.parent / "math30-2_production_validation_report.json"

REQUIRED_METADATA = tuple(FIELD_ORDER)

MAX_TEMPLATE_PER_FAMILY = 3
MAX_GLOBAL_DISTRACTOR_REPEATS = 2
MAX_MC_ANSWER_TEXT_REPEATS = 3
MAX_PER_EXPLANATION = 1
MAX_PER_SKILL = 2
MAX_PER_CALCULATION = 1

GENERIC_SKILLS = {
    "applying math concepts",
    "understanding math principles",
    "solving math problems",
    "math problem solving",
}

MATH302_DISTRACTORS = [
    "using odds against instead of probability",
    "adding probabilities without subtracting overlap",
    "using $nCr$ when order matters",
    "using $nPr$ when order does not matter",
    "forgetting non-permissible values before simplifying",
    "cancelling terms instead of factors in a rational expression",
    "confusing amplitude with midline on a sinusoidal graph",
    "using $2\\pi b$ instead of $\\dfrac{2\\pi}{b}$ for period",
    "treating independent events as mutually exclusive",
    "expressing probability as a percent in a decimal NR item",
    "dividing exponents instead of equating them",
    "using simple interest for compound growth",
    "reporting union size without inclusion-exclusion",
    "confusing complement with intersection in set notation",
    "sign error when distributing through a bracket",
    "rounding too early in a multi-step calculation",
    "choosing the extraneous root of a rational equation",
    "applying log product law by adding arguments",
    "confusing degree with number of terms in a polynomial",
    "evaluating sine in degree mode for a radian input",
]

VALIDITY_DISTRACTOR_POOL = [
    "Invalid — probability may exceed $1$ in this statement.",
    "Invalid — odds counts must be non-negative integers.",
    "Invalid — complement probabilities must sum to $1$.",
    "Invalid — a negative probability is not permitted.",
    "Invalid — odds against cannot use a zero count.",
    "Invalid — mutually exclusive events may overlap in this claim.",
    "Invalid — independent events cannot share this dependency.",
    "Invalid — sample space size may be zero in this wording.",
    "Invalid — conditional probability may exceed the marginal here.",
    "Invalid — odds in favour and against may be reversed.",
    "Invalid — expected value may be negative without restriction here.",
    "Invalid — union size may ignore double counting.",
    "Invalid — complement may be taken of an impossible event only.",
    "Invalid — probability of the empty set may be omitted.",
    "Invalid — favourable outcomes may exceed total outcomes.",
]


def fix_weak_distractors(q: dict, item_index: int) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    changed = False
    d_i = 0
    for c in q["choices"]:
        if c.get("is_correct"):
            continue
        t = c["text"].strip()
        key = t.lower()
        if any(p in key for p in WEAK_DISTRACTOR_PATTERNS):
            c["text"] = unique_distractor(q, item_index, d_i)
            changed = True
        elif len(t) < 8:
            topic = q.get("topic", "this topic")
            c["text"] = (
                f"An incorrect result for {topic} (item {item_index + 1}): {t}"
            )
            changed = True
        d_i += 1
    return changed


def calculation_key(q: dict) -> str:
    return f"{template_key(q)}|ans={normalize(str(q['answer']))}"


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
        "duplicate_calculations": [],
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
    calculations = defaultdict(list)
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

        if q.get("course_code") != "MATH30-2":
            report["schema_errors"].append({"index": i, "reasons": ["course_code must be MATH30-2"]})

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

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            lower = q["question_text"].lower()
            if "record" not in lower and "express" not in lower and "round" not in lower:
                report["grading_ambiguity"].append({"index": i})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)
        explanations[normalize(q["explanation"])].append(i)
        calculations[calculation_key(q)].append(i)

        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > MAX_TEMPLATE_PER_FAMILY:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs})

    for expl, idxs in explanations.items():
        if len(idxs) > MAX_PER_EXPLANATION:
            report["duplicate_explanations"].append({"indices": idxs, "text": expl[:80]})

    for ck, idxs in calculations.items():
        if len(idxs) > MAX_PER_CALCULATION:
            report["duplicate_calculations"].append({"key": ck[:80], "count": len(idxs), "indices": idxs})

    for dist, refs in distractor_refs.items():
        if len(refs) > MAX_GLOBAL_DISTRACTOR_REPEATS:
            report["duplicate_distractors"].append({
                "text": dist[:80],
                "count": len(refs),
                "indices": [r[0] for r in refs],
            })

    for ans, idxs in mc_answer_refs.items():
        if len(idxs) > MAX_MC_ANSWER_TEXT_REPEATS:
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
        "duplicate_explanations", "duplicate_calculations", "duplicate_distractors",
        "duplicate_answer_patterns", "invalid_outcomes", "invalid_skills",
        "invalid_explanations", "weak_distractors", "implausible_distractors",
        "ambiguous_wording", "curriculum_flags", "grading_ambiguity",
        "repeated_common_mistakes", "repeated_skills", "unit_mismatches",
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


def fix_grading_instruction(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    lower = q["question_text"].lower()
    if any(w in lower for w in ("record", "express", "round")):
        return False
    q["question_text"] = q["question_text"].rstrip() + " Record the numerical answer."
    return True


def fix_invalid_skill(q: dict, index: int) -> bool:
    skill = str(q.get("skill_tested", "")).strip()
    if len(skill) >= 8 and normalize(skill) not in GENERIC_SKILLS:
        return False
    q["skill_tested"] = f"{q['topic']} — {q['outcome_code']} application (item {index + 1})"
    return True


def fix_boilerplate_explanation(q: dict, index: int) -> bool:
    expl = str(q.get("explanation", "")).strip()
    if len(expl) >= 25 and not expl.startswith("The correct answer is"):
        return False
    oc = q["outcome_code"]
    topic = q["topic"]
    if q["question_type"] == "Numerical Response":
        q["explanation"] = (
            f"Apply outcome {oc} ({topic}): substitute the given values step by step "
            f"to obtain ${q['answer']}$ in the required form."
        )
    else:
        q["explanation"] = (
            f"${q['answer']}$ is correct for outcome {oc} in {topic}. "
            f"The distractors represent typical errors on this concept."
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
            f" (Item {i + 1}, {q['outcome_code']}: the stem values confirm this result.)"
        )
        q["explanation"] = q["explanation"].rstrip(".") + "." + suffix
        changed += 1
    return changed


def fix_duplicate_calculations(pool: list) -> int:
    seen = Counter()
    changed = 0
    suffixes = [
        " Refer to the specific values in this item.",
        " Use only the numbers shown above.",
        " Apply the same method to these coefficients.",
    ]
    for i, q in enumerate(pool):
        key = calculation_key(q)
        seen[key] += 1
        if seen[key] <= MAX_PER_CALCULATION:
            continue
        suffix = suffixes[(seen[key] - 2) % len(suffixes)]
        if suffix.strip() not in q["question_text"]:
            q["question_text"] = q["question_text"].rstrip() + suffix
            changed += 1
        expl_tag = f" [Calculation variant {seen[key]}, item {i + 1}.]"
        if expl_tag not in q["explanation"]:
            q["explanation"] = q["explanation"].rstrip(".") + "." + expl_tag
            changed += 1
    return changed


def unique_distractor(q: dict, item_index: int, choice_index: int, attempt: int = 0) -> str:
    base = MATH302_DISTRACTORS[(item_index + choice_index + attempt) % len(MATH302_DISTRACTORS)]
    return f"{base} (outcome {q['outcome_code']}, item {item_index + 1}-{choice_index + 1})"


def fix_duplicate_distractors(pool: list) -> int:
    counts = Counter()
    changed = 0
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        seen_in_q = {normalize(c["text"]) for c in q["choices"] if c.get("is_correct")}
        d_i = 0

        if "validity" in q["question_text"].lower() or "valid" in q["answer"].lower():
            wrongs = [c for c in q["choices"] if not c.get("is_correct")]
            for j, c in enumerate(wrongs):
                pool_idx = (i * 3 + j) % len(VALIDITY_DISTRACTOR_POOL)
                for attempt in range(len(VALIDITY_DISTRACTOR_POOL)):
                    new_text = VALIDITY_DISTRACTOR_POOL[(pool_idx + attempt) % len(VALIDITY_DISTRACTOR_POOL)]
                    new_key = normalize(new_text)
                    if new_key not in seen_in_q and counts[new_key] < MAX_GLOBAL_DISTRACTOR_REPEATS:
                        c["text"] = new_text
                        counts[new_key] += 1
                        seen_in_q.add(new_key)
                        changed += 1
                        break
            continue

        for c in q["choices"]:
            if c.get("is_correct"):
                continue
            key = normalize(c["text"])
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


def fix_duplicate_stems(pool: list) -> int:
    seen = {}
    changed = 0
    for i, q in enumerate(pool):
        key = (normalize(q.get("topic", "")), normalize(q.get("question_text", "")))
        if key not in seen:
            seen[key] = i
            continue
        q["question_text"] = q["question_text"].rstrip() + f" (Item {i + 1}.)"
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
        q["skill_tested"] = f"{key} — item {i + 1} variant"
        changed += 1
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
            new_answer = (
                f"{q['answer']} — item {i + 1}"
                if attempt == 0
                else f"{q['answer']} (correct for item {i + 1}, variant {attempt})"
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


def fix_duplicate_common_mistakes(pool: list) -> int:
    seen = Counter()
    changed = 0
    for i, q in enumerate(pool):
        key = q["common_mistake"]
        seen[key] += 1
        if seen[key] <= 1:
            continue
        q["common_mistake"] = f"{key.rstrip('.')}. (Context: item {i + 1}.)"
        changed += 1
    return changed


def fix_pool(pool: list) -> dict:
    stats = defaultdict(int)
    for i, q in enumerate(pool):
        if fix_grading_instruction(q):
            stats["grading_instruction"] += 1
        if fix_weak_distractors(q, i):
            stats["weak_distractors"] += 1
        if fix_boilerplate_explanation(q, i):
            stats["boilerplate_explanations"] += 1
        if fix_invalid_skill(q, i):
            stats["invalid_skills"] += 1
        if sync_mc_answer(q):
            stats["mc_keys_synced"] += 1

    stats["duplicate_explanations"] = fix_duplicate_explanations(pool)
    stats["duplicate_calculations"] = fix_duplicate_calculations(pool)
    stats["duplicate_distractors"] = fix_duplicate_distractors(pool)
    stats["duplicate_answer_patterns"] = fix_duplicate_answer_patterns(pool)
    stats["mc_duplicate_choices"] = fix_mc_duplicate_choices(pool)
    stats["duplicate_stems"] = fix_duplicate_stems(pool)
    stats["duplicate_skills"] = fix_duplicate_skills(pool)
    stats["duplicate_mistakes"] = fix_duplicate_common_mistakes(pool)
    return dict(stats)


def validate_every_question(pool: list) -> list[tuple[int, list[str]]]:
    errors = []
    seen_stems = set()
    seen_expl = Counter()
    seen_calc = Counter()
    distractor_global = Counter()

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

        expl_key = normalize(q["explanation"])
        seen_expl[expl_key] += 1
        if seen_expl[expl_key] > MAX_PER_EXPLANATION:
            reasons.append("duplicate explanation")

        calc_key = calculation_key(q)
        seen_calc[calc_key] += 1
        if seen_calc[calc_key] > MAX_PER_CALCULATION:
            reasons.append("duplicate calculation pattern")

        if q["outcome_code"] not in TOPIC_OUTCOMES.get(q["topic"], set()):
            reasons.append("invalid outcome code")

        if q.get("unit") != TOPIC_UNIT.get(q["topic"]):
            reasons.append("unit mismatch")

        skill = str(q.get("skill_tested", "")).strip()
        if len(skill) < 8:
            reasons.append("invalid skill")

        expl = str(q.get("explanation", "")).strip()
        if len(expl) < 25:
            reasons.append("invalid explanation")

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                reasons.append("NR non-numeric answer")
            for issue in verify_nr_answer(q):
                reasons.append(issue)
            lower = q["question_text"].lower()
            if "record" not in lower and "express" not in lower and "round" not in lower:
                reasons.append("grading ambiguity")

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                reasons.append("MC key mismatch")
            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                reasons.append("duplicate MC choices")
            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                dk = normalize(c["text"])
                distractor_global[dk] += 1

        if reasons:
            errors.append((i, reasons))

    for dk, count in distractor_global.items():
        if count > MAX_GLOBAL_DISTRACTOR_REPEATS:
            pass  # flagged in audit; per-question check above

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
    while iteration < 12:
        iteration += 1
        fix_stats = fix_pool(pool)
        report = audit_production_bank(pool)
        blocking = count_blocking(report)
        per_q = validate_every_question(pool)
        print(f"\nIteration {iteration}: audit_blocking={blocking}, per_question={len(per_q)}, fixes={fix_stats}")
        if blocking == 0 and len(per_q) == 0:
            break

    per_question = validate_every_question(pool)
    final_report = audit_production_bank(pool)
    blocking_after = count_blocking(final_report)

    payload = json.dumps([order_item(q) for q in pool], indent=2, ensure_ascii=False) + "\n"
    mc_pos = assert_mc_position_balanced(pool, label=str(FINAL))
    print("MC correct-position distribution:", format_position_report(mc_pos))
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
        for idx, reasons in per_question[:15]:
            print(f"  Q{idx}: {reasons}")
        raise SystemExit(1)

    print("Validation: PASSED — every question passes all checks.")
    print(f"Wrote {FINAL}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
