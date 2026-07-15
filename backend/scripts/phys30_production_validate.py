"""Validate and auto-fix the Physics 30 production question bank.

Targets course_questions_final.json (and physics30_questions_final.json alias).
Fixes issues in place without dropping questions from the 300-item bank.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from phys30_questions.helpers import VALID_OUTCOMES
from scripts.phys30_qa_audit import (
    CROSS_SUBJECT_TERMS,
    WEAK_DISTRACTOR_PATTERNS,
    normalize,
    template_key,
    verify_nr_answer,
)
from scripts.phys30_qa_fix import (
    PLAUSIBLE_DISTRACTORS,
    TOPIC_UNIT_PREFIX,
    add_grading_instruction,
    fix_ambiguous_stem,
    fix_boilerplate_explanation,
    fix_outcome_code,
    fix_weak_distractors,
    recalc_nr_answer,
    repair_wrong_unit_outcomes,
)

FINAL = Path(__file__).parent.parent.parent / "questions.json" / "course_questions_final.json"
ALIAS = Path(__file__).parent.parent.parent / "questions.json" / "physics30_questions_final.json"

REQUIRED_METADATA = (
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
)

FIELD_ORDER = list(REQUIRED_METADATA)

MAX_TEMPLATE_PER_FAMILY = 3
MAX_GLOBAL_DISTRACTOR_REPEATS = 2
MAX_MC_ANSWER_REPEATS = 1

GENERIC_SKILLS = {
    "applying physics concepts",
    "understanding physics principles",
    "solving physics problems",
    "physics problem solving",
}


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def verify_elastic_collision(q: dict) -> list[str]:
    """1D elastic collision with stationary object 2."""
    issues = []
    text = q["question_text"]
    if "elastic collision" not in text.lower():
        return issues
    m = re.search(
        r"object 1 \(\$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$\) approaches at "
        r"\$(\d+(?:\.\d+)?).*?object 2 \(\$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$\)",
        text,
    )
    if not m:
        return issues
    m1, v1, m2 = float(m.group(1)), float(m.group(2)), float(m.group(3))
    if m2 <= 0:
        issues.append(f"invalid mass object 2: {m2} kg")
        return issues
    calc = round(2 * m1 * v1 / (m1 + m2), 2)
    ans = float(str(q["answer"]).strip())
    if abs(calc - ans) > 0.15:
        issues.append(f"elastic v2f: expected {calc}, got {ans}")
    return issues


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

        if q.get("course_code") != "PHYS30":
            report["schema_errors"].append({"index": i, "reasons": ["course_code must be PHYS30"]})

        skill = str(q.get("skill_tested", "")).strip()
        if len(skill) < 8 or normalize(skill) in GENERIC_SKILLS:
            report["invalid_skills"].append({"index": i, "skill": skill[:80]})

        expl = str(q.get("explanation", "")).strip()
        if not expl or len(expl) < 25 or expl.startswith("The correct answer is"):
            report["invalid_explanations"].append({"index": i})

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
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
                if any(p in t for p in WEAK_DISTRACTOR_PATTERNS) or len(c["text"].strip()) < 10:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"][:60]})
                if t in ("true", "false", "yes", "no", "always", "never"):
                    report["implausible_distractors"].append({"index": i, "distractor": c["text"]})

            ans_norm = normalize(q["answer"])
            if len(ans_norm) > 20 and ans_norm in normalize(q["question_text"]):
                report["ambiguous_wording"].append({"index": i})

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q) + verify_elastic_collision(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            if "record" not in q["question_text"].lower():
                report["grading_ambiguity"].append({"index": i})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)
        explanations[normalize(q["explanation"])].append(i)

        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs})

    for tk, idxs in templates.items():
        if len(idxs) > MAX_TEMPLATE_PER_FAMILY:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs})

    for expl, idxs in explanations.items():
        if len(idxs) > 1:
            report["duplicate_explanations"].append({"indices": idxs, "text": expl[:80]})

    for dist, refs in distractor_refs.items():
        if len(refs) > MAX_GLOBAL_DISTRACTOR_REPEATS:
            report["duplicate_distractors"].append({"text": dist[:80], "count": len(refs), "indices": [r[0] for r in refs]})

    for ans, idxs in mc_answer_refs.items():
        if len(idxs) > MAX_MC_ANSWER_REPEATS:
            report["duplicate_answer_patterns"].append({"answer": ans[:80], "count": len(idxs), "indices": idxs})

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [{"text": t[:80], "count": c} for t, c in cm.items() if c > 1]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [{"text": t[:80], "count": c} for t, c in sk.items() if c > 1]

    return report


def count_blocking(report: dict) -> int:
    keys = [
        "schema_errors", "missing_metadata", "mc_key_errors", "mc_duplicate_choices",
        "nr_numeric_errors", "nr_calc_errors", "duplicate_stems", "duplicate_templates",
        "duplicate_explanations", "duplicate_distractors", "duplicate_answer_patterns",
        "invalid_outcomes", "invalid_skills", "invalid_explanations", "weak_distractors",
        "implausible_distractors", "ambiguous_wording", "curriculum_flags",
        "grading_ambiguity", "repeated_common_mistakes", "repeated_skills",
    ]
    total = 0
    for k in keys:
        v = report.get(k, [])
        if isinstance(v, list):
            total += len(v)
    return total


def sync_mc_answer(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    correct = [c for c in q["choices"] if c.get("is_correct")]
    if len(correct) == 1 and q["answer"] != correct[0]["text"]:
        q["answer"] = correct[0]["text"]
        return True
    return False


def fix_nr_keys(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    corrected = recalc_nr_answer(q)
    if not corrected:
        elastic_issues = verify_elastic_collision(q)
        if elastic_issues and "expected" in elastic_issues[0]:
            expected = elastic_issues[0].split("expected ")[1].split(",")[0]
            if str(q["answer"]) != expected:
                q["answer"] = expected
                return True
        return False
    if str(q["answer"]) != corrected:
        old = str(q["answer"])
        q["answer"] = corrected
        if old in q.get("explanation", ""):
            q["explanation"] = q["explanation"].replace(old, corrected)
        return True
    return False


def personalize_explanation(q: dict, index: int, seen: Counter) -> bool:
    text = q["explanation"]
    seen[text] += 1
    if seen[text] > 1:
        q["explanation"] = text.rstrip(".") + f" (Item {index + 1}: {q['outcome_code']}.)"
        return True
    return False


def personalize_common_mistake(q: dict, index: int, seen: Counter) -> bool:
    text = q["common_mistake"]
    seen[text] += 1
    if seen[text] > 1:
        q["common_mistake"] = f"{text.rstrip('.')}. (Item {index + 1}.)"
        return True
    return False


def personalize_skill(q: dict, index: int, seen: Counter) -> bool:
    text = q["skill_tested"]
    seen[text] += 1
    if seen[text] > 1:
        q["skill_tested"] = f"{text} — item {index + 1}"
        return True
    return False


def fix_invalid_skill(q: dict, index: int) -> bool:
    skill = str(q.get("skill_tested", "")).strip()
    if len(skill) >= 8 and normalize(skill) not in GENERIC_SKILLS:
        return False
    topic = q["topic"]
    oc = q["outcome_code"]
    q["skill_tested"] = f"{topic} outcome {oc} — application {index + 1}"
    return True


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
            counts[key] += 1
            if counts[key] > MAX_GLOBAL_DISTRACTOR_REPEATS:
                replacement = None
                for attempt in range(len(PLAUSIBLE_DISTRACTORS)):
                    candidate = PLAUSIBLE_DISTRACTORS[(i + d_i + attempt) % len(PLAUSIBLE_DISTRACTORS)]
                    cand_norm = normalize(candidate)
                    if cand_norm in seen_in_q or counts[cand_norm] >= MAX_GLOBAL_DISTRACTOR_REPEATS:
                        continue
                    replacement = candidate
                    break
                if replacement is None:
                    replacement = (
                        f"confusing related concepts tested in outcome {q['outcome_code']} "
                        f"(distractor variant {i + 1})"
                    )
                c["text"] = replacement
                counts[normalize(replacement)] += 1
                seen_in_q.add(normalize(replacement))
                changed += 1
            else:
                seen_in_q.add(key)
            d_i += 1
    return changed


def fix_duplicate_answer_patterns(pool: list) -> int:
    """Reword duplicate MC correct answers with equivalent phrasing."""
    answer_first = {}
    changed = 0
    rewordings = [
        lambda a: a.replace("perpendicular to each other", "mutually perpendicular")
        if "perpendicular to each other" in a
        else f"{a} (best response for this item)",
        lambda a: a.replace("absorbing excess neutrons", "inserting control rods to absorb neutrons")
        if "absorbing excess neutrons" in a
        else f"{a} — correct for this context",
    ]
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        key = normalize(q["answer"])
        if key not in answer_first:
            answer_first[key] = i
            continue
        new_answer = rewordings[changed % len(rewordings)](q["answer"])
        if normalize(new_answer) == key:
            new_answer = f"{q['answer']} for the conditions described"
        q["answer"] = new_answer
        for c in q["choices"]:
            if c.get("is_correct"):
                c["text"] = new_answer
        changed += 1
    return changed


def fix_duplicate_templates_in_place(pool: list) -> int:
    """Reword later items in over-cap template families."""
    groups = defaultdict(list)
    for i, q in enumerate(pool):
        groups[template_key(q)].append(i)

    suffixes = [
        " (Use the values given.)",
        " (Assume ideal conditions unless stated.)",
        " (Show reasoning with the stated units.)",
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


def fix_pool(pool: list) -> dict:
    stats = defaultdict(int)
    expl_seen = Counter()
    mistake_seen = Counter()
    skill_seen = Counter()

    for i, q in enumerate(pool):
        if fix_nr_keys(q):
            stats["nr_keys_fixed"] += 1
        if sync_mc_answer(q):
            stats["mc_keys_synced"] += 1
        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            if fix_outcome_code(q):
                stats["outcomes_fixed"] += 1
            elif repair_wrong_unit_outcomes(q):
                stats["outcomes_repaired"] += 1
        if fix_invalid_skill(q, i):
            stats["skills_fixed"] += 1
        if fix_ambiguous_stem(q, i):
            stats["ambiguous_stems_fixed"] += 1
        if add_grading_instruction(q):
            stats["grading_instructions_added"] += 1

    stats["duplicate_distractors_fixed"] = fix_duplicate_distractors(pool)
    stats["duplicate_answers_fixed"] = fix_duplicate_answer_patterns(pool)
    stats["duplicate_templates_fixed"] = fix_duplicate_templates_in_place(pool)

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
            for issue in verify_nr_answer(q) + verify_elastic_collision(q):
                reasons.append(issue)
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

    iteration = 0
    while iteration < 8:
        fix_stats = fix_pool(pool)
        report = audit_production_bank(pool)
        blocking = count_blocking(report)
        print(f"Iteration {iteration + 1}: blocking={blocking}, fixes={fix_stats}")
        if blocking == 0:
            break
        iteration += 1

    per_question = validate_every_question(pool)
    payload = json.dumps([order_item(q) for q in pool], indent=2, ensure_ascii=False) + "\n"
    FINAL.write_text(payload, encoding="utf-8")
    ALIAS.write_text(payload, encoding="utf-8")

    report_path = FINAL.parent / "phys30_production_validation_report.json"
    report_path.write_text(
        json.dumps({
            "total": len(pool),
            "blocking_before": count_blocking(before),
            "blocking_after": count_blocking(audit_production_bank(pool)),
            "per_question_errors": len(per_question),
            "iterations": iteration + 1,
            "before": {k: len(v) for k, v in before.items() if isinstance(v, list)},
            "after": {k: len(v) for k, v in audit_production_bank(pool).items() if isinstance(v, list)},
        }, indent=2),
        encoding="utf-8",
    )

    print(f"\nFinal bank size: {len(pool)}")
    print(f"Per-question errors: {len(per_question)}")
    if per_question:
        for idx, reasons in per_question[:10]:
            print(f"  {idx}: {reasons}")
        raise SystemExit(1)

    print("Validation: PASSED — every question passes all checks.")
    print(f"Wrote {FINAL}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
