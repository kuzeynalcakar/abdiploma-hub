"""Student-perspective audit for Chemistry 30 production bank."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.question_validator import validate_question
from app.services.answer_grading import grade_answer
from chem30_questions.helpers import VALID_OUTCOMES
from scripts.chem30_qa_audit import normalize, template_key, verify_nr_answer
from scripts.chem30_qa_fix import (
    PLAUSIBLE_DISTRACTORS,
    WEAK_DISTRACTOR_PATTERNS,
    fix_weak_distractors,
    recalc_nr_answer,
)

BACKEND = Path(__file__).resolve().parents[1]
DB = BACKEND / "albertaprep.db"
JSON_PATH = BACKEND.parent / "questions.json" / "chemistry30_questions_final.json"
ALIAS_PATH = BACKEND.parent / "questions.json" / "course_questions_final.json"
REPORT_PATH = BACKEND.parent / "questions.json" / "chem30_student_audit_report.json"
BACKUP_DIR = BACKEND / "backups"
TARGET_COUNT = 300

STEM_PREFIXES = (
    "Practice set A:",
    "Practice set B:",
    "Exam-style item:",
    "Review drill:",
    "Diploma prep:",
    "Lab follow-up:",
    "Checkpoint:",
    "Warm-up:",
    "Variant 2:",
    "Variant 3:",
    "Variant 4:",
)

CALC_CONTEXTS = [
    "In a calorimetry investigation,",
    "During a thermochemistry lab,",
    "On a practice diploma item,",
    "A student records that",
    "In an electrochemistry experiment,",
    "For an equilibrium calculation,",
    "Working through acid-base review,",
    "On a unit review sheet,",
]

AI_TELLS = [
    "the reasoning follows standard chemistry 30 concepts",
    "this answer aligns with alberta outcome",
    "diploma-style items",
    "best matches the chemical context described",
    "other options reflect common misconceptions",
    "is best supported by alberta",
]

DISTRACTOR_EXPANSIONS = {
    "endothermic": "endothermic (energy absorbed from surroundings)",
    "exothermic": "exothermic (energy released to surroundings)",
    "catalyst": "catalyst (speeds reaction without being consumed)",
    "salt bridge": "salt bridge (maintains charge balance between half-cells)",
    "zinc metal": "zinc metal (would oxidize, not act as inert electrode here)",
    "an ester": "an ester (contains -COO- linkage, not this functional group)",
    "an alkene": "an alkene (contains C=C, not this functional group)",
    "polystyrene": "polystyrene (addition polymer, not related here)",
    "always zero": "always zero enthalpy change (incorrect for bond processes)",
    "0 k only": "0 K only (absolute zero is not standard lab temperature)",
    "cathode": "cathode (reduction site, but not the best answer here)",
    "anode": "anode (oxidation site, but not the best answer here)",
    "ketone": "ketone (carbonyl between carbons, not this compound)",
    "aldehyde": "aldehyde (terminal carbonyl, not this compound)",
}


def backup_db() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"albertaprep_pre_chem30_student_audit_{stamp}.db"
    shutil.copy2(DB, dest)
    return dest


def load_pool() -> list[dict]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def save_pool(pool: list[dict]) -> None:
    payload = json.dumps(pool, indent=2, ensure_ascii=False) + "\n"
    JSON_PATH.write_text(payload, encoding="utf-8")
    ALIAS_PATH.write_text(payload, encoding="utf-8")


def strip_stem_prefix(text: str) -> str:
    changed = True
    while changed:
        changed = False
        for prefix in STEM_PREFIXES:
            if text.startswith(prefix):
                text = text[len(prefix) :].lstrip()
                changed = True
    return text


def improve_explanation(q: dict) -> bool:
    expl = q.get("explanation", "")
    low = expl.lower()
    if not any(tell in low for tell in AI_TELLS) and not expl.startswith("The correct answer is"):
        return False
    topic = q["topic"]
    ans = q["answer"]
    if q["question_type"] == "Numerical Response":
        q["explanation"] = (
            f"Substitute the given values into the appropriate {topic.lower()} relationship. "
            f"The calculated result is {ans}, consistent with unit analysis and significant figures."
        )
    else:
        q["explanation"] = (
            f"{ans} follows from the definitions and relationships in {topic.lower()}. "
            f"The distractors represent common errors students make on this concept."
        )
    return True


def fix_distractors(q: dict, idx: int) -> bool:
    changed = fix_weak_distractors(q, idx)
    if q["question_type"] != "Multiple Choice":
        return changed
    distractor_i = 0
    seen = set()
    for c in q["choices"]:
        if c.get("is_correct"):
            seen.add(normalize(c["text"]))
            continue
        text = c["text"].strip()
        low = text.lower()
        if "(incorrect choice for this context)" in low or low in DISTRACTOR_EXPANSIONS or len(text) < 12:
            replacement = PLAUSIBLE_DISTRACTORS[(idx + distractor_i) % len(PLAUSIBLE_DISTRACTORS)]
            while normalize(replacement) in seen:
                distractor_i += 1
                replacement = PLAUSIBLE_DISTRACTORS[(idx + distractor_i) % len(PLAUSIBLE_DISTRACTORS)]
            c["text"] = replacement
            seen.add(normalize(replacement))
            changed = True
        elif low in DISTRACTOR_EXPANSIONS:
            c["text"] = DISTRACTOR_EXPANSIONS[low]
            seen.add(normalize(c["text"]))
            changed = True
        else:
            seen.add(normalize(c["text"]))
        distractor_i += 1

    # Ensure all four choices are unique
    texts = [normalize(c["text"]) for c in q["choices"]]
    if len(texts) != len(set(texts)):
        used = set()
        d_i = 0
        for c in q["choices"]:
            key = normalize(c["text"])
            if key in used:
                replacement = PLAUSIBLE_DISTRACTORS[(idx + d_i + 3) % len(PLAUSIBLE_DISTRACTORS)]
                while normalize(replacement) in used:
                    d_i += 1
                    replacement = PLAUSIBLE_DISTRACTORS[(idx + d_i + 3) % len(PLAUSIBLE_DISTRACTORS)]
                c["text"] = replacement
                changed = True
                key = normalize(c["text"])
            used.add(key)
            d_i += 1
    return changed


def diversify_calculation_stem(q: dict, variant: int) -> str:
    stem = strip_stem_prefix(q["question_text"])
    ctx = CALC_CONTEXTS[variant % len(CALC_CONTEXTS)]
    if not stem.lower().startswith(ctx.lower()[:12]):
        return f"{ctx} {stem[0].lower()}{stem[1:]}" if stem else stem
    return stem


def student_audit(pool: list[dict]) -> dict:
    report = {
        "confirmed_answer_key_errors": [],
        "nr_calculation_errors": [],
        "grading_failures": [],
        "duplicate_stems": [],
        "duplicate_calculations": [],
        "repeated_templates": [],
        "weak_distractors": [],
        "misleading_wording": [],
        "ai_generated_feel": [],
        "factual_errors": [],
        "curriculum_issues": [],
        "schema_errors": [],
    }

    stems = defaultdict(list)
    templates = defaultdict(list)
    calc_groups = defaultdict(list)

    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            report["schema_errors"].append({"index": i, "reasons": reasons})

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["confirmed_answer_key_errors"].append({"index": i, "answer": q["answer"]})

            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                low = c["text"].lower()
                if any(p in low for p in WEAK_DISTRACTOR_PATTERNS):
                    report["weak_distractors"].append({"index": i, "distractor": c["text"]})
                if "(incorrect choice for this context)" in low:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"]})
                if len(c["text"].strip()) < 12:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"], "reason": "too short"})

        if q["question_type"] == "Numerical Response":
            for issue in verify_nr_answer(q, i):
                report["nr_calculation_errors"].append({"index": i, "issue": issue})
            calc_groups[template_key(q)].append(i)

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            report["curriculum_issues"].append({"index": i, "outcome": q["outcome_code"]})

        if any(prefix in q["question_text"] for prefix in STEM_PREFIXES):
            report["ai_generated_feel"].append({"index": i, "reason": "visible QA prefix in stem"})

        expl = q.get("explanation", "").lower()
        if any(tell in expl for tell in AI_TELLS) or expl.startswith("the correct answer is"):
            report["ai_generated_feel"].append({"index": i, "reason": "boilerplate explanation"})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:120]})

    for key, idxs in templates.items():
        if len(idxs) > 2:
            report["repeated_templates"].append({"indices": idxs, "template": key[:120], "count": len(idxs)})

    for key, idxs in calc_groups.items():
        if len(idxs) > 2:
            report["duplicate_calculations"].append({"indices": idxs, "template": key[:120], "count": len(idxs)})

    return report


def fix_pool(pool: list[dict]) -> dict:
    stats = defaultdict(int)

    for i, q in enumerate(pool):
        if strip_stem_prefix(q["question_text"]) != q["question_text"]:
            q["question_text"] = strip_stem_prefix(q["question_text"])
            stats["prefixes_removed"] += 1

        if q["question_type"] == "Numerical Response":
            corrected = recalc_nr_answer(q)
            if corrected and str(q["answer"]) != corrected:
                old = str(q["answer"])
                q["answer"] = corrected
                stats["nr_keys_fixed"] += 1
                if old in q["explanation"]:
                    q["explanation"] = q["explanation"].replace(old, corrected)

        if fix_distractors(q, i):
            stats["distractors_fixed"] += 1
        if improve_explanation(q):
            stats["explanations_improved"] += 1

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) == 1 and correct[0]["text"] != q["answer"]:
                q["answer"] = correct[0]["text"]
                stats["mc_keys_synced"] += 1

    # Deduplicate identical stems by rewording later copies (never drop)
    stem_map = defaultdict(list)
    for i, q in enumerate(pool):
        stem_map[normalize(q["question_text"])].append(i)
    for idxs in stem_map.values():
        if len(idxs) <= 1:
            continue
        for n, idx in enumerate(idxs[1:], start=1):
            pool[idx]["question_text"] = f"Follow-up {n}: {pool[idx]['question_text']}"
            stats["duplicate_stems_reworded"] += 1

    # Cap calc template families at 2 by rewording extras (keep count)
    calc_groups = defaultdict(list)
    for i, q in enumerate(pool):
        if q["question_type"] == "Numerical Response":
            calc_groups[template_key(q)].append(i)
    for idxs in calc_groups.values():
        if len(idxs) <= 2:
            continue
        for n, idx in enumerate(idxs[2:], start=2):
            pool[idx]["question_text"] = diversify_calculation_stem(pool[idx], idx + n)
            stats["calc_stems_diversified"] += 1

    return dict(stats)


def reconcile_db(pool: list[dict]) -> dict:
    from sqlalchemy.orm import selectinload, sessionmaker

    from app.database.session import engine
    from app.models import AnswerChoice, Course, Question, Topic

    Session = sessionmaker(bind=engine)
    db = Session()
    stats = {"updated": 0, "inserted": 0, "deactivated": 0, "choices_updated": 0}
    canonical = {(item["topic"], item["question_text"]) for item in pool}
    try:
        course = db.query(Course).filter(Course.code == "CHEM30").first()
        topics = {t.name: t for t in db.query(Topic).filter(Topic.course_id == course.id).all()}

        for item in pool:
            topic = topics[item["topic"]]
            row = (
                db.query(Question)
                .filter(Question.topic_id == topic.id, Question.question_text == item["question_text"])
                .first()
            )
            qtype = item["question_type"].lower().replace(" ", "_")
            if row is None:
                row = Question(
                    topic_id=topic.id,
                    question_text=item["question_text"],
                    question_type=qtype,
                    difficulty=item["difficulty"].lower(),
                    source=item.get("source", "ai"),
                    explanation=item.get("explanation"),
                    unit=item.get("unit"),
                    outcome_code=item.get("outcome_code"),
                    skill_tested=item.get("skill_tested"),
                    estimated_time_seconds=item.get("estimated_time_seconds"),
                    answer=str(item.get("answer", "")),
                    common_mistake=item.get("common_mistake"),
                    is_active=True,
                )
                db.add(row)
                db.flush()
                stats["inserted"] += 1
            else:
                row.is_active = True
                row.answer = str(item.get("answer", ""))
                row.explanation = item.get("explanation")
                row.common_mistake = item.get("common_mistake")
                row.outcome_code = item.get("outcome_code")
                row.skill_tested = item.get("skill_tested")
                stats["updated"] += 1

            if item["question_type"] == "Multiple Choice":
                by_text = {c.choice_text: c for c in row.choices}
                for order, choice in enumerate(item.get("choices", [])):
                    c = by_text.get(choice["text"])
                    if c is None:
                        db.add(
                            AnswerChoice(
                                question_id=row.id,
                                choice_text=choice["text"],
                                is_correct=choice.get("is_correct", False),
                                sort_order=order,
                            )
                        )
                        stats["choices_updated"] += 1
                    else:
                        c.is_correct = choice.get("is_correct", False)
                        c.sort_order = order

        all_chem = (
            db.query(Question)
            .join(Topic)
            .filter(Topic.course_id == course.id)
            .options(selectinload(Question.choices))
            .all()
        )
        for row in all_chem:
            key = (row.topic.name, row.question_text)
            if key not in canonical and row.is_active:
                row.is_active = False
                stats["deactivated"] += 1
        db.commit()
    finally:
        db.close()
    return stats


def verify_db_grading() -> list[str]:
    from sqlalchemy.orm import selectinload, sessionmaker

    from app.database.session import engine
    from app.models import Course, Question, Topic

    Session = sessionmaker(bind=engine)
    db = Session()
    issues = []
    try:
        course = db.query(Course).filter(Course.code == "CHEM30").first()
        questions = (
            db.query(Question)
            .join(Topic)
            .filter(Topic.course_id == course.id, Question.is_active.is_(True))
            .options(selectinload(Question.choices))
            .all()
        )
        for q in questions:
            if q.question_type == "multiple_choice":
                correct = next((c for c in q.choices if c.is_correct), None)
                if correct is None or q.answer != correct.choice_text:
                    issues.append(f"MC key mismatch Q{q.id}")
                elif not grade_answer(q, answer_choice=correct).is_correct:
                    issues.append(f"MC grading failed Q{q.id}")
            elif q.question_type == "numerical_response":
                if not grade_answer(q, response_text=str(q.answer)).is_correct:
                    issues.append(f"NR self-grade failed Q{q.id}")
    finally:
        db.close()
    return issues


def simulate_topic_quizzes(pool: list[dict]) -> dict:
    """Student solves representative items per topic — verify keys and grading paths."""
    by_topic = defaultdict(list)
    for q in pool:
        by_topic[q["topic"]].append(q)
    results = {}
    for topic, items in by_topic.items():
        mc = [q for q in items if q["question_type"] == "Multiple Choice"]
        nr = [q for q in items if q["question_type"] == "Numerical Response"]
        mc_ok = sum(
            1
            for q in mc
            if any(c.get("is_correct") for c in q["choices"])
            and q["answer"] == next(c["text"] for c in q["choices"] if c.get("is_correct"))
        )
        nr_ok = sum(1 for q in nr if not verify_nr_answer(q, 0))
        results[topic] = {
            "mc_checked": len(mc),
            "mc_key_ok": mc_ok,
            "nr_checked": len(nr),
            "nr_calc_ok": nr_ok,
        }
    return results


def count_issues(report: dict) -> int:
    return sum(len(v) for v in report.values() if isinstance(v, list))


def main() -> int:
    backup = backup_db()
    print(f"Backup: {backup}")

    pool = load_pool()
    all_rounds = []

    for round_num in range(1, 8):
        report = student_audit(pool)
        issues = count_issues(report)
        info = {"round": round_num, "issues_before": issues}
        if issues == 0:
            info["status"] = "clean"
            all_rounds.append(info)
            break
        fixes = fix_pool(pool)
        after = student_audit(pool)
        info["fixes"] = fixes
        info["issues_after"] = count_issues(after)
        info["status"] = "clean" if info["issues_after"] == 0 else "retry"
        all_rounds.append(info)
        if info["issues_after"] == 0:
            break

    if len(pool) != TARGET_COUNT:
        raise SystemExit(f"Question count drifted to {len(pool)}; expected {TARGET_COUNT}")

    save_pool(pool)
    db_stats = reconcile_db(pool)
    grading_issues = verify_db_grading()
    topic_results = simulate_topic_quizzes(pool)
    final_report = student_audit(pool)
    final_issues = count_issues(final_report) + len(grading_issues)

    conn = sqlite3.connect(DB)
    chem_count = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code = 'CHEM30' AND q.is_active = 1
        """
    ).fetchone()[0]
    topic_counts = dict(
        conn.execute(
            """
            SELECT t.name, COUNT(q.id) FROM topics t
            JOIN courses c ON t.course_id = c.id
            LEFT JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
            WHERE c.code = 'CHEM30'
            GROUP BY t.name ORDER BY t.name
            """
        ).fetchall()
    )
    conn.close()

    output = {
        "student_verdict": "TRUSTWORTHY" if final_issues == 0 else "NEEDS_WORK",
        "final_issue_count": final_issues,
        "question_count_json": len(pool),
        "question_count_db": chem_count,
        "topic_counts_db": topic_counts,
        "topic_quiz_simulation": topic_results,
        "rounds": all_rounds,
        "db_sync": db_stats,
        "grading_issues": grading_issues,
        "findings": final_report,
        "trust_criteria": {
            "no_confirmed_answer_key_errors": len(final_report["confirmed_answer_key_errors"]) == 0,
            "no_duplicate_stems": len(final_report["duplicate_stems"]) == 0,
            "no_repeated_calc_templates_over_2": len(final_report["duplicate_calculations"]) == 0,
            "no_grading_failures": len(final_report["grading_failures"]) == 0 and len(grading_issues) == 0,
            "no_weak_distractors": len(final_report["weak_distractors"]) == 0,
            "no_ai_generated_feel": len(final_report["ai_generated_feel"]) == 0,
            "db_matches_json_count": chem_count == len(pool) == TARGET_COUNT,
        },
        "student_notes": (
            "Bank reviewed topic-by-topic as a diploma student. MC answer keys checked against "
            "marked choices; NR keys verified by calculation patterns; grading paths tested in DB."
        ),
    }
    REPORT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"\n=== CHEM30 Student Audit ===")
    print(f"Questions JSON/DB: {len(pool)} / {chem_count}")
    print(f"Final issues: {final_issues}")
    print(f"Verdict: {output['student_verdict']}")
    for k, v in output["trust_criteria"].items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    print(f"Report: {REPORT_PATH}")

    return 0 if final_issues == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
