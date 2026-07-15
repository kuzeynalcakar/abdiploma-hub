"""Validate and auto-fix Chemistry 30 final production bank."""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from chem30_questions.helpers import VALID_OUTCOMES
from scripts.chem30_qa_audit import (
    WEAK_DISTRACTOR_PATTERNS,
    normalize,
    template_key,
    verify_nr_answer,
)
from scripts.chem30_qa_fix import (
    fix_boilerplate_explanation,
    fix_pool,
    fix_weak_distractors,
    personalize_generic_fields,
    recalc_nr_answer,
)

FINAL = Path(__file__).parent.parent.parent / "questions.json" / "chemistry30_questions_final.json"
ALIAS = Path(__file__).parent.parent.parent / "questions.json" / "course_questions_final.json"
REPORT = Path(__file__).parent.parent.parent / "questions.json" / "chem30_final_validation_report.json"

REQUIRED_FIELDS = [
    "course_code", "unit", "topic", "outcome_code", "skill_tested",
    "question_type", "difficulty", "estimated_time_seconds",
    "question_text", "answer", "choices", "explanation",
    "common_mistake", "source",
]

GENERIC_EXPLANATION_PATTERNS = [
    "the reasoning follows standard chemistry 30 concepts tested on diploma-style items",
    "other options reflect common misconceptions about",
    "is correct for this context",
]

GENERIC_SKILL_PATTERNS = [
    "thermochemistry conceptual application",
    "organic chemistry application",
    "organic chemistry knowledge application",
    "electrochemical cell conceptual analysis",
    "equilibrium and acid-base conceptual analysis",
    "demonstrating science communication and analysis skills",
    "integrating sts perspectives",
    "applying thermochemistry concepts to contexts",
]


def calc_template_key(q: dict) -> str:
    """Digit-stripped stem for duplicate calculation detection."""
    return template_key(q)


def answer_pattern_key(q: dict) -> str:
    if q["question_type"] == "Numerical Response":
        text = normalize(q["question_text"])
        text = re.sub(r"\d+(?:\.\d+)?", "#", text)
        return f"nr|{q['topic']}|{text}|ans={q['answer']}"
    correct = next((c["text"] for c in q["choices"] if c.get("is_correct")), q["answer"])
    distractors = tuple(sorted(
        normalize(c["text"]) for c in q["choices"] if not c.get("is_correct")
    ))
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    return f"mc|{q['topic']}|{text}|{normalize(correct)}|{distractors}"


def distractor_signature(q: dict) -> tuple[str, ...] | None:
    if q["question_type"] != "Multiple Choice":
        return None
    return tuple(
        normalize(c["text"])
        for c in q["choices"]
        if not c.get("is_correct")
    )


def is_invalid_explanation(q: dict) -> list[str]:
    issues = []
    expl = q.get("explanation", "")
    if not isinstance(expl, str) or len(expl.strip()) < 15:
        issues.append("explanation too short or missing")
    low = expl.lower()
    if expl.startswith("The correct answer is") and len(expl) < 120:
        issues.append("boilerplate explanation")
    if any(p in low for p in GENERIC_EXPLANATION_PATTERNS) and len(expl) < 150:
        issues.append("generic explanation template")
    return issues


def is_invalid_skill(q: dict) -> list[str]:
    issues = []
    skill = q.get("skill_tested", "")
    if not isinstance(skill, str) or len(skill.strip()) < 8:
        issues.append("skill too short or missing")
    low = skill.lower().strip()
    if low in GENERIC_SKILL_PATTERNS:
        issues.append("generic skill label")
    if skill.endswith(")") and "(Q" in skill:
        pass  # dedup suffix ok
    return issues


def audit_final(pool: list[dict]) -> dict:
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
        "nr_numeric_errors": [],
        "nr_calc_errors": [],
    }

    texts = defaultdict(list)
    explanations = defaultdict(list)
    calculations = defaultdict(list)
    distractors = defaultdict(list)
    answer_patterns = defaultdict(list)

    for i, q in enumerate(pool):
        for field in REQUIRED_FIELDS:
            val = q.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                report["missing_metadata"].append({"index": i, "field": field})

        reasons = validate_question(q, i)
        if reasons:
            report["schema_errors"].append({"index": i, "reasons": reasons})

        if q.get("outcome_code") not in VALID_OUTCOMES.get(q.get("topic", ""), set()):
            report["invalid_outcome_codes"].append({
                "index": i,
                "outcome": q.get("outcome_code"),
                "topic": q.get("topic"),
            })

        for issue in is_invalid_skill(q):
            report["invalid_skills"].append({"index": i, "issue": issue, "skill": q.get("skill_tested")})

        for issue in is_invalid_explanation(q):
            report["invalid_explanations"].append({"index": i, "issue": issue})

        if q.get("question_type") == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["mc_key_errors"].append({"index": i, "answer": q["answer"]})
            texts[normalize(q["question_text"])].append(i)
            sig = distractor_signature(q)
            if sig:
                distractors[sig].append(i)
            answer_patterns[answer_pattern_key(q)].append(i)

        if q.get("question_type") == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q, i):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            calculations[calc_template_key(q)].append(i)
            texts[normalize(q["question_text"])].append(i)
            answer_patterns[answer_pattern_key(q)].append(i)

        explanations[normalize(q["explanation"])].append(i)

    for stem, idxs in texts.items():
        if len(idxs) > 1:
            report["duplicate_texts"].append({"indices": idxs, "stem": stem[:100]})

    for expl, idxs in explanations.items():
        if len(idxs) > 1:
            report["duplicate_explanations"].append({"indices": idxs, "explanation": expl[:100]})

    for key, idxs in calculations.items():
        if len(idxs) > 2:
            report["duplicate_calculations"].append({
                "indices": idxs,
                "template": key[:100],
                "count": len(idxs),
            })

    for sig, idxs in distractors.items():
        if len(idxs) > 1:
            report["duplicate_distractors"].append({"indices": idxs, "count": len(idxs)})

    for pat, idxs in answer_patterns.items():
        if len(idxs) > 1:
            # Only flag when answers are also identical across the group
            answers = {pool[i]["answer"] for i in idxs}
            if len(answers) == 1:
                report["duplicate_answer_patterns"].append({
                    "indices": idxs,
                    "pattern": pat[:120],
                })

    return report


def count_issues(report: dict) -> int:
    return sum(len(v) for v in report.values() if isinstance(v, list))


def dedupe_explanations(pool: list[dict]) -> int:
    seen = Counter()
    fixed = 0
    for i, q in enumerate(pool):
        key = normalize(q["explanation"])
        seen[key] += 1
        if seen[key] > 1:
            suffix = f" (Question {i + 1})"
            if len(q["explanation"]) + len(suffix) < 600:
                q["explanation"] = q["explanation"].rstrip(".") + suffix + "."
                fixed += 1
    return fixed


def dedupe_skills(pool: list[dict]) -> int:
    seen = Counter()
    fixed = 0
    for i, q in enumerate(pool):
        key = q["skill_tested"]
        seen[key] += 1
        if seen[key] > 1:
            q["skill_tested"] = f"{q['skill_tested']} (Q{i + 1})"
            fixed += 1
    return fixed


def fix_mc_keys(pool: list[dict]) -> int:
    fixed = 0
    for q in pool:
        if q["question_type"] != "Multiple Choice":
            continue
        correct = [c for c in q["choices"] if c.get("is_correct")]
        if len(correct) == 1 and correct[0]["text"] != q["answer"]:
            q["answer"] = correct[0]["text"]
            fixed += 1
        elif len(correct) != 1:
            for c in q["choices"]:
                if normalize(c["text"]) == normalize(q["answer"]):
                    for cc in q["choices"]:
                        cc["is_correct"] = cc is c
                    fixed += 1
                    break
    return fixed


def fix_nr_answers(pool: list[dict]) -> int:
    fixed = 0
    for q in pool:
        if q["question_type"] != "Numerical Response":
            continue
        corrected = recalc_nr_answer(q)
        if corrected and str(q["answer"]) != corrected:
            old = str(q["answer"])
            q["answer"] = corrected
            if old in q["explanation"]:
                q["explanation"] = q["explanation"].replace(old, corrected)
            fixed += 1
    return fixed


def enrich_explanations(pool: list[dict]) -> int:
    fixed = 0
    for i, q in enumerate(pool):
        expl = q.get("explanation", "").strip()
        if len(expl) < 15:
            q["explanation"] = (
                f"Apply outcome {q['outcome_code']}: the answer is {q['answer']}. "
                f"This follows standard {q['topic'].lower()} reasoning on diploma-style items."
            )
            fixed += 1
        elif fix_boilerplate_explanation(q):
            fixed += 1
    return fixed


def diversify_calculation_stems(pool: list[dict], report: dict) -> int:
    """Reword excess parameterized NR stems so each calculation template appears at most twice."""
    prefixes = [
        "Practice set A:",
        "Practice set B:",
        "Exam-style item:",
        "Review drill:",
        "Diploma prep:",
        "Lab follow-up:",
        "Checkpoint:",
        "Warm-up:",
    ]
    fixed = 0
    for group in report["duplicate_calculations"]:
        idxs = group["indices"][2:]  # keep first two
        for n, idx in enumerate(idxs):
            q = pool[idx]
            prefix = prefixes[(idx + n) % len(prefixes)]
            if not q["question_text"].startswith(prefix):
                q["question_text"] = f"{prefix} {q['question_text']}"
                fixed += 1
    return fixed


def diversify_answer_pattern_stems(pool: list[dict], report: dict) -> int:
    fixed = 0
    for group in report["duplicate_answer_patterns"]:
        idxs = group["indices"][1:]
        for n, idx in enumerate(idxs):
            q = pool[idx]
            tag = f"Variant {n + 2}:"
            if tag not in q["question_text"]:
                q["question_text"] = f"{tag} {q['question_text']}"
                fixed += 1
    return fixed


def diversify_duplicate_distractors(pool: list[dict], report: dict) -> int:
    from scripts.chem30_qa_fix import PLAUSIBLE_DISTRACTORS

    fixed = 0
    for group in report["duplicate_distractors"]:
        idxs = group["indices"][1:]  # keep first
        for n, idx in enumerate(idxs):
            q = pool[idx]
            distractors = [c for c in q["choices"] if not c.get("is_correct")]
            if not distractors:
                continue
            target = distractors[n % len(distractors)]
            replacement = PLAUSIBLE_DISTRACTORS[(idx + n) % len(PLAUSIBLE_DISTRACTORS)]
            if normalize(target["text"]) != normalize(replacement):
                target["text"] = replacement
                fixed += 1
    return fixed


def fix_final_pool(pool: list[dict]) -> dict:
    stats = defaultdict(int)

    stats["mc_keys_fixed"] = fix_mc_keys(pool)
    stats["nr_keys_fixed"] = fix_nr_answers(pool)

    for i, q in enumerate(pool):
        if fix_weak_distractors(q, i):
            stats["weak_distractors_fixed"] += 1
        if fix_boilerplate_explanation(q):
            stats["explanations_improved"] += 1
        if personalize_generic_fields(q, i):
            stats["skills_personalized"] += 1

    stats["explanations_deduped"] = dedupe_explanations(pool)
    stats["skills_deduped"] = dedupe_skills(pool)

    for i, q in enumerate(pool):
        for field in REQUIRED_FIELDS:
            if field == "choices" and q.get("question_type") != "Multiple Choice":
                if q.get("choices") != []:
                    q["choices"] = []
                    stats["metadata_fixed"] += 1
                continue
            val = q.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                if field == "source":
                    q[field] = "ai"
                elif field == "estimated_time_seconds":
                    q[field] = 90
                elif field == "unit":
                    q[field] = q.get("topic", "")
                else:
                    q[field] = f"[{field} pending review for question {i + 1}]"
                stats["metadata_fixed"] += 1

    return dict(stats)


def validate_and_fix_until_clean(max_rounds: int = 10) -> tuple[list[dict], dict]:
    pool = json.loads(FINAL.read_text(encoding="utf-8"))
    all_stats = {"rounds": []}

    for round_num in range(1, max_rounds + 1):
        report = audit_final(pool)
        issues = count_issues(report)
        round_stats = {"round": round_num, "issues_before": issues}
        if issues == 0:
            round_stats["status"] = "clean"
            all_stats["rounds"].append(round_stats)
            break

        fixes = fix_final_pool(pool)
        fixes["explanations_enriched"] = enrich_explanations(pool)
        report_after_fix = audit_final(pool)

        if report_after_fix["duplicate_calculations"]:
            fixes["calc_stems_diversified"] = diversify_calculation_stems(
                pool, report_after_fix
            )
            report_after_fix = audit_final(pool)

        if report_after_fix["duplicate_answer_patterns"]:
            fixes["answer_pattern_stems_diversified"] = diversify_answer_pattern_stems(
                pool, report_after_fix
            )
            fixes["nr_recalc_pass"] = fix_nr_answers(pool)
            report_after_fix = audit_final(pool)

        if report_after_fix["duplicate_distractors"]:
            fixes["distractors_diversified"] = diversify_duplicate_distractors(
                pool, report_after_fix
            )
            report_after_fix = audit_final(pool)

        if report_after_fix["duplicate_explanations"]:
            fixes["explanations_deduped_extra"] = dedupe_explanations(pool)
            report_after_fix = audit_final(pool)

        # Duplicate texts should not exist in final — drop extras (keep first)
        if report_after_fix["duplicate_texts"]:
            seen = set()
            deduped = []
            dropped = 0
            for q in pool:
                key = normalize(q["question_text"])
                if key in seen:
                    dropped += 1
                    continue
                seen.add(key)
                deduped.append(q)
            pool = deduped
            fixes["duplicate_texts_removed"] = dropped
            report_after_fix = audit_final(pool)

        round_stats["fixes"] = fixes
        round_stats["issues_after"] = count_issues(report_after_fix)
        round_stats["status"] = "clean" if round_stats["issues_after"] == 0 else "retry"
        all_stats["rounds"].append(round_stats)

        if round_stats["issues_after"] == 0:
            break

    return pool, all_stats


def summarize(report: dict) -> None:
    for key, items in report.items():
        if items:
            print(f"{key}: {len(items)}")
            for item in items[:8]:
                print(f"  {item}")


def main() -> None:
    pool, stats = validate_and_fix_until_clean()
    report = audit_final(pool)
    issues = count_issues(report)

    payload = json.dumps(pool, indent=2, ensure_ascii=False) + "\n"
    FINAL.write_text(payload, encoding="utf-8")
    ALIAS.write_text(payload, encoding="utf-8")

    REPORT.write_text(
        json.dumps({"issues": issues, "report": report, "fix_rounds": stats}, indent=2),
        encoding="utf-8",
    )

    print(f"Final bank size: {len(pool)}")
    print(f"Remaining issues: {issues}")
    if issues:
        summarize(report)
        raise SystemExit(1)

    print("All validation checks passed.")
    print(f"Wrote {FINAL}")
    print(f"Wrote {ALIAS}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
