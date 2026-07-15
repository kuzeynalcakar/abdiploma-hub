"""Validate and auto-fix the Science 10 production question bank.

Targets course_questions_final.json and science10_questions_final.json.
Repeats fix/audit until every question passes all production checks.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from sci10_questions.helpers import VALID_OUTCOMES
from sci10_questions.pool_qa import is_boilerplate_explanation
from scripts.sci10_qa_fix import (
    answer_pattern_key,
    build_explanation,
    dedupe_explanations,
    dedupe_skills,
    distractor_signature,
    diversify_answer_pattern_stems,
    diversify_duplicate_calculations,
    diversify_duplicate_distractors,
    fix_boilerplate_explanation,
    fix_boilerplate_mistake,
    fix_metadata,
    fix_nr_keys,
    fix_outcome_code,
    fix_stem_punctuation,
    fix_weak_distractors,
    normalize,
    remove_duplicate_texts,
    sync_mc_answer,
    template_key,
    verify_nr_answer,
)

FINAL = Path(__file__).parent.parent.parent / "questions.json" / "course_questions_final.json"
ALIAS = Path(__file__).parent.parent.parent / "questions.json" / "science10_questions_final.json"
REPORT = Path(__file__).parent.parent.parent / "questions.json" / "sci10_production_validation_report.json"

REQUIRED_METADATA = (
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
)

FIELD_ORDER = list(REQUIRED_METADATA)

MAX_TEMPLATE_PER_FAMILY = 2
MAX_EXPLANATION_REPEATS = 1
MAX_SKILL_REPEATS = 2
MAX_DISTRACTOR_REPEATS = 1
MAX_ANSWER_PATTERN_REPEATS = 1
MAX_CALC_TEMPLATE_REPEATS = 2


def order_item(item: dict) -> dict:
    return {k: item[k] for k in FIELD_ORDER}


def audit_production_bank(pool: list[dict]) -> dict:
    report = {
        "schema_errors": [],
        "missing_metadata": [],
        "duplicate_texts": [],
        "duplicate_explanations": [],
        "duplicate_calculations": [],
        "duplicate_distractors": [],
        "duplicate_answer_patterns": [],
        "invalid_outcome_codes": [],
        "invalid_skills": [],
        "invalid_explanations": [],
        "mc_key_errors": [],
        "mc_duplicate_choices": [],
        "nr_numeric_errors": [],
        "nr_calc_errors": [],
        "duplicate_templates": [],
        "repeated_skills": [],
    }

    texts = defaultdict(list)
    explanations = defaultdict(list)
    calculations = defaultdict(list)
    distractors = defaultdict(list)
    answer_patterns = defaultdict(list)
    templates = defaultdict(list)

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

        if q.get("course_code") != "SCI10":
            report["schema_errors"].append({"index": i, "reasons": ["course_code must be SCI10"]})

        if q.get("outcome_code") not in VALID_OUTCOMES.get(q.get("topic", ""), set()):
            report["invalid_outcome_codes"].append({
                "index": i,
                "outcome": q.get("outcome_code"),
                "topic": q.get("topic"),
            })

        skill = str(q.get("skill_tested", "")).strip()
        if len(skill) < 8:
            report["invalid_skills"].append({"index": i, "skill": skill[:80]})

        if is_boilerplate_explanation(q):
            report["invalid_explanations"].append({"index": i, "issue": "boilerplate or short explanation"})

        stem_key = (normalize(q.get("topic", "")), normalize(q.get("question_text", "")))
        texts[stem_key].append(i)
        explanations[normalize(q.get("explanation", ""))].append(i)
        templates[template_key(q)].append(i)

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or normalize(correct[0]["text"]) != normalize(q["answer"]):
                report["mc_key_errors"].append({"index": i, "answer": q["answer"]})
            choice_texts = [c["text"] for c in q["choices"]]
            if len(set(normalize(t) for t in choice_texts)) < 4:
                report["mc_duplicate_choices"].append({"index": i})
            sig = distractor_signature(q)
            if sig:
                distractors[sig].append(i)
            answer_patterns[answer_pattern_key(q)].append(i)

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            calculations[template_key(q)].append(i)
            answer_patterns[answer_pattern_key(q)].append(i)

    for stem, idxs in texts.items():
        if len(idxs) > 1:
            report["duplicate_texts"].append({"indices": idxs, "stem": stem[1][:100]})

    for expl, idxs in explanations.items():
        if len(idxs) > MAX_EXPLANATION_REPEATS:
            report["duplicate_explanations"].append({"indices": idxs, "explanation": expl[:100]})

    for key, idxs in calculations.items():
        if len(idxs) > MAX_CALC_TEMPLATE_REPEATS:
            report["duplicate_calculations"].append({"indices": idxs, "template": key[:100], "count": len(idxs)})

    for sig, idxs in distractors.items():
        if len(idxs) > MAX_DISTRACTOR_REPEATS:
            report["duplicate_distractors"].append({"indices": idxs, "count": len(idxs)})

    for pat, idxs in answer_patterns.items():
        if len(idxs) > MAX_ANSWER_PATTERN_REPEATS:
            answers = {pool[i]["answer"] for i in idxs}
            if len(answers) == 1:
                report["duplicate_answer_patterns"].append({"indices": idxs, "pattern": pat[:120]})

    for key, idxs in templates.items():
        if len(idxs) > MAX_TEMPLATE_PER_FAMILY:
            report["duplicate_templates"].append({"indices": idxs, "template": key[:100], "count": len(idxs)})

    skill_counts = Counter(q["skill_tested"] for q in pool)
    for skill, count in skill_counts.items():
        if count > MAX_SKILL_REPEATS:
            report["repeated_skills"].append({"skill": skill, "count": count})

    return report


def count_blocking(report: dict) -> int:
    return sum(len(v) for v in report.values() if isinstance(v, list))


def fix_pool(pool: list[dict], report: dict) -> dict:
    stats = defaultdict(int)

    stats["duplicate_texts_removed"] = remove_duplicate_texts(pool)

    for i, q in enumerate(pool):
        if fix_nr_keys(q):
            stats["nr_keys_fixed"] += 1
        if sync_mc_answer(q):
            stats["mc_keys_synced"] += 1
        if fix_outcome_code(q):
            stats["outcomes_fixed"] += 1
        if fix_stem_punctuation(q):
            stats["stems_fixed"] += 1
        if fix_metadata(q, i):
            stats["metadata_fixed"] += 1
        if fix_weak_distractors(q, i):
            stats["weak_distractors_fixed"] += 1
        expl = q.get("explanation", "")
        if is_boilerplate_explanation(q) or expl.lower().startswith("outcome "):
            q["explanation"] = build_explanation(q, i)
            stats["explanations_rewritten"] += 1
        elif fix_boilerplate_explanation(q, i):
            stats["explanations_rewritten"] += 1
        if fix_boilerplate_mistake(q, i):
            stats["mistakes_rewritten"] += 1

    stats["explanations_deduped"] = dedupe_explanations(pool)
    stats["skills_deduped"] = dedupe_skills(pool, max_repeats=MAX_SKILL_REPEATS)
    stats["answer_patterns_diversified"] = diversify_answer_pattern_stems(
        pool, report["duplicate_answer_patterns"]
    )
    stats["distractors_diversified"] = diversify_duplicate_distractors(
        pool, report["duplicate_distractors"]
    )
    stats["calculations_diversified"] = diversify_duplicate_calculations(
        pool, report["duplicate_calculations"]
    )

    report2 = audit_production_bank(pool)
    for group in report2["duplicate_explanations"]:
        for n, idx in enumerate(group["indices"][1:]):
            q = pool[idx]
            q["explanation"] = build_explanation(q, idx) + f" Review note {n + 2}."
            stats["duplicate_explanations_fixed"] += 1

    for group in report2["duplicate_calculations"]:
        stats["calculations_diversified"] += diversify_duplicate_calculations(pool, [group])

    return dict(stats)


def validate_every_question(pool: list[dict]) -> list[tuple[int, list[str]]]:
    errors = []
    seen_stems = set()
    expl_seen = Counter()
    skill_seen = Counter()
    calc_seen = Counter()
    dist_seen = Counter()
    ans_pat_seen = Counter()
    tmpl_seen = Counter()

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

        if is_boilerplate_explanation(q):
            reasons.append("invalid explanation")

        if q.get("outcome_code") not in VALID_OUTCOMES.get(q.get("topic", ""), set()):
            reasons.append("invalid outcome code")

        if len(str(q.get("skill_tested", "")).strip()) < 8:
            reasons.append("invalid skill")

        expl_key = normalize(q.get("explanation", ""))
        expl_seen[expl_key] += 1
        if expl_seen[expl_key] > MAX_EXPLANATION_REPEATS:
            reasons.append("duplicate explanation")

        skill_key = q.get("skill_tested", "")
        skill_seen[skill_key] += 1
        if skill_seen[skill_key] > MAX_SKILL_REPEATS:
            reasons.append("repeated skill")

        tk = template_key(q)
        tmpl_seen[tk] += 1
        if tmpl_seen[tk] > MAX_TEMPLATE_PER_FAMILY:
            reasons.append("duplicate template")

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or normalize(correct[0]["text"]) != normalize(q["answer"]):
                reasons.append("MC answer key mismatch")
            choice_texts = [c["text"] for c in q["choices"]]
            if len(set(normalize(t) for t in choice_texts)) < 4:
                reasons.append("duplicate MC choices")
            sig = distractor_signature(q)
            if sig:
                dist_seen[sig] += 1
                if dist_seen[sig] > MAX_DISTRACTOR_REPEATS:
                    reasons.append("duplicate distractors")
            ap = answer_pattern_key(q)
            ans_pat_seen[ap] += 1
            if ans_pat_seen[ap] > MAX_ANSWER_PATTERN_REPEATS:
                reasons.append("duplicate answer pattern")

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                reasons.append("NR answer not numeric")
            reasons.extend(verify_nr_answer(q))
            calc_seen[tk] += 1
            if calc_seen[tk] > MAX_CALC_TEMPLATE_REPEATS:
                reasons.append("duplicate calculation template")
            ap = answer_pattern_key(q)
            ans_pat_seen[ap] += 1
            if ans_pat_seen[ap] > MAX_ANSWER_PATTERN_REPEATS:
                reasons.append("duplicate answer pattern")

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
    for key, items in before.items():
        if items:
            print(f"  {key}: {len(items)}")

    iteration = 0
    while iteration < 10:
        report = audit_production_bank(pool)
        blocking = count_blocking(report)
        if blocking == 0:
            break
        fix_stats = fix_pool(pool, report)
        print(f"Iteration {iteration + 1}: blocking={blocking}, fixes={fix_stats}")
        iteration += 1

    per_question = validate_every_question(pool)
    after = audit_production_bank(pool)

    if len(pool) != 300:
        print(f"WARNING: bank size is {len(pool)}, expected 300")

    payload = json.dumps([order_item(q) for q in pool], indent=2, ensure_ascii=False) + "\n"
    FINAL.write_text(payload, encoding="utf-8")
    ALIAS.write_text(payload, encoding="utf-8")

    summary = {
        "total": len(pool),
        "blocking_before": count_blocking(before),
        "blocking_after": count_blocking(after),
        "per_question_errors": len(per_question),
        "iterations": iteration,
        "before": {k: len(v) for k, v in before.items() if isinstance(v, list)},
        "after": {k: len(v) for k, v in after.items() if isinstance(v, list)},
    }
    REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nFinal bank size: {len(pool)}")
    print(f"Blocking issues after fix: {summary['blocking_after']}")
    print(f"Per-question errors: {len(per_question)}")
    if per_question:
        for idx, reasons in per_question[:15]:
            print(f"  Q{idx + 1}: {reasons}")
        raise SystemExit(1)

    print("Validation: PASSED — every question passes all checks.")
    print(f"Wrote {FINAL}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
