"""Full production database audit for launch readiness."""
from __future__ import annotations

import re
import sqlite3
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

PROD_DB = Path(__file__).resolve().parents[1] / "albertaprep.db"
issues: list[str] = []
warnings: list[str] = []

AUDITED_COURSE_CODES = (
    "MATH20-1",
    "MATH30-2",
    "BIO30",
    "MATH30-1",
    "CHEM30",
    "PHYS30",
    "SCI30",
    "SCI10",
)

# Explicit allowlist kept for continuity / documentation. Cross-course exact
# stems always warn (never fail); allowlisted pairs are also printed under
# "Accepted curriculum overlaps" without requiring new hardcoding for every
# legitimate Alberta stream overlap (shared topic name is enough).
ACCEPTED_CROSS_COURSE_OVERLAPS: dict[str, frozenset[str]] = {
    # Difference of squares / rational simplification — MATH20-1 & MATH30-2.
    r"Simplify $\dfrac{x^2 - 4}{x - 2}$ for $x \ne 2$.": frozenset(
        {"MATH20-1", "MATH30-2"}
    ),
}

# Same-course near-duplicate thresholds (essentially the same item twice).
STEM_SIMILARITY_FAIL = 0.92
STEM_SIMILARITY_REVIEW = 0.82


def fail(msg: str) -> None:
    issues.append(msg)
    print(f"FAIL: {msg}")


def warn(msg: str) -> None:
    warnings.append(msg)
    print(f"WARN: {msg}")


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def info(msg: str) -> None:
    print(f"INFO: {msg}")


def _normalize_stem(text: str) -> str:
    t = (text or "").lower()
    # Preserve signed numbers before stripping punctuation.
    t = re.sub(r"(?<![a-z0-9])-(\d)", r" neg\1", t)
    t = t.replace("\\", " ")
    t = re.sub(r"[^a-z0-9\s]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _normalize_skill(skill: str | None, topic: str | None) -> str:
    raw = (skill or topic or "").lower()
    raw = re.sub(r"[^a-z0-9\s]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def _token_jaccard(a: str, b: str) -> float:
    wa, wb = set(a.split()), set(b.split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _stem_similarity(a: str, b: str) -> float:
    na, nb = _normalize_stem(a), _normalize_stem(b)
    if not na or not nb:
        return 0.0
    return max(SequenceMatcher(None, na, nb).ratio(), _token_jaccard(na, nb))


def _load_active_questions(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        f"""
        SELECT q.id, q.question_text, q.answer, q.skill_tested, q.outcome_code,
               q.question_type, t.name AS topic, c.code AS course_code
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        JOIN courses c ON t.course_id = c.id
        WHERE c.code IN ({",".join("?" for _ in AUDITED_COURSE_CODES)})
          AND q.is_active = 1
        """,
        AUDITED_COURSE_CODES,
    ).fetchall()

    choices_by_q: dict[int, list[tuple[str, int]]] = defaultdict(list)
    if rows:
        ids = [r["id"] for r in rows]
        # Chunk IN clause for SQLite variable limits
        for i in range(0, len(ids), 400):
            chunk = ids[i : i + 400]
            for ch in conn.execute(
                f"""
                SELECT question_id, choice_text, is_correct
                FROM answer_choices
                WHERE question_id IN ({",".join("?" for _ in chunk)})
                ORDER BY sort_order
                """,
                chunk,
            ):
                choices_by_q[ch["question_id"]].append(
                    (ch["choice_text"] or "", int(ch["is_correct"] or 0))
                )

    items: list[dict] = []
    for r in rows:
        choice_rows = choices_by_q.get(r["id"], [])
        correct = [
            c[0].strip() for c in choice_rows if c[1]
        ] or ([r["answer"].strip()] if r["answer"] else [])
        distractors = {c[0].strip().lower() for c in choice_rows if not c[1]}
        items.append(
            {
                "id": r["id"],
                "text": r["question_text"] or "",
                "answer": (r["answer"] or "").strip(),
                "correct_texts": [c.lower() for c in correct],
                "distractors": distractors,
                "skill": _normalize_skill(r["skill_tested"], r["topic"]),
                "topic": (r["topic"] or "").strip().lower(),
                "outcome": (r["outcome_code"] or "").strip().lower(),
                "course": r["course_code"],
                "type": r["question_type"],
            }
        )
    return items


def _essentially_same_question(a: dict, b: dict) -> bool:
    """True when a student would experience the same item twice in one course.

    Practice variants that change numbers, formulas, or wording enough to alter
    the normalized stem are not treated as duplicates.
    """
    if a["type"] != b["type"]:
        return False

    na, nb = _normalize_stem(a["text"]), _normalize_stem(b["text"])
    if not na or not nb or na != nb:
        return False

    ans_a = set(a["correct_texts"]) | ({a["answer"].lower()} if a["answer"] else set())
    ans_b = set(b["correct_texts"]) | ({b["answer"].lower()} if b["answer"] else set())
    if not ans_a or not ans_b or ans_a.isdisjoint(ans_b):
        return False

    if a["distractors"] and b["distractors"]:
        inter = len(a["distractors"] & b["distractors"])
        union = len(a["distractors"] | b["distractors"])
        if union and inter / union < 0.5:
            return False
    return True


def _is_documented_accepted(text: str, courses: frozenset[str]) -> bool:
    allowed = ACCEPTED_CROSS_COURSE_OVERLAPS.get(text)
    return allowed is not None and courses <= allowed


def _shared_curriculum_skill(items: list[dict]) -> bool:
    """Heuristic: shared topic name and/or normalized skill across courses."""
    topics = {i["topic"] for i in items if i["topic"]}
    skills = {i["skill"] for i in items if i["skill"]}
    if len(topics) == 1:
        return True
    if len(skills) == 1:
        return True
    # high skill token overlap across the set
    if len(skills) >= 2:
        skills_list = list(skills)
        if all(
            _token_jaccard(skills_list[0], s) >= 0.6 for s in skills_list[1:]
        ):
            return True
    return False


def _audit_duplicate_classification(conn: sqlite3.Connection) -> None:
    """
    Classify duplicates:

    1. SAME COURSE + EXACT STEM → ERROR (fail)
    2. CROSS COURSE + EXACT STEM → WARNING (review; do not fail)
    3. CROSS COURSE + different stem, same skill → INFO
    4. SAME COURSE + similar wording → ERROR only if essentially the same question
    """
    items = _load_active_questions(conn)

    print("\n=== Duplicate classification ===")

    # --- 1 & 2: exact stem grouping ---
    by_stem: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        by_stem[it["text"]].append(it)

    same_course_exact = 0
    cross_course_exact_rows: list[tuple[frozenset[str], str, list[dict]]] = []

    for text, group in by_stem.items():
        if len(group) < 2:
            continue
        by_course: dict[str, list[dict]] = defaultdict(list)
        for it in group:
            by_course[it["course"]].append(it)

        for course, course_items in by_course.items():
            if len(course_items) > 1:
                same_course_exact += 1
                ids = ", ".join(str(i["id"]) for i in course_items)
                fail(
                    f"SAME COURSE + EXACT STEM [{course}] "
                    f"ids={ids}: {text[:70]}"
                )

        courses = frozenset(by_course)
        if len(courses) >= 2 and all(len(v) == 1 for v in by_course.values()):
            cross_course_exact_rows.append((courses, text, group))

    # --- 4: same-course similar (non-exact) ---
    by_course_all: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        by_course_all[it["course"]].append(it)

    similar_fail = 0
    for course, course_items in by_course_all.items():
        n = len(course_items)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = course_items[i], course_items[j]
                if a["text"] == b["text"]:
                    continue  # already handled as exact
                sim = _stem_similarity(a["text"], b["text"])
                if sim < STEM_SIMILARITY_REVIEW:
                    continue
                if _essentially_same_question(a, b):
                    similar_fail += 1
                    fail(
                        f"SAME COURSE + ESSENTIALLY SAME [{course}] "
                        f"ids={a['id']},{b['id']} sim={sim:.2f}"
                    )

    # --- 2 & accepted overlaps report ---
    accepted: list[str] = []
    cross_review: list[str] = []

    for courses, text, group in cross_course_exact_rows:
        preview = text if len(text) <= 70 else text[:67] + "..."
        codes = ", ".join(sorted(courses))
        ids = ", ".join(str(i["id"]) for i in group)
        line = f"{codes} | ids={ids} | {preview}"

        documented = _is_documented_accepted(text, courses)
        shared_skill = _shared_curriculum_skill(group)
        if documented or shared_skill:
            reason = "documented allowlist" if documented else "shared topic/skill"
            accepted.append(f"{line} ({reason})")
        cross_review.append(line)
        warn(f"CROSS COURSE + EXACT STEM ({codes}): {preview}")

    print("\n=== Accepted curriculum overlaps ===")
    if accepted:
        for row in accepted:
            ok(row)
        ok(f"{len(accepted)} accepted curriculum overlap(s)")
    else:
        info("None recorded this run")

    print("\n=== Cross-course review report (exact stem) ===")
    if cross_review:
        for row in cross_review:
            print(f"  - {row}")
        warn(
            f"{len(cross_review)} cross-course exact stem(s) for review "
            "(do not fail production readiness)"
        )
    else:
        ok("No cross-course exact stem overlaps")

    # --- 3: cross-course different stem, same skill (sample INFO) ---
    print("\n=== Cross-course same-skill (different stem) ===")
    skill_index: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        if it["skill"]:
            skill_index[it["skill"]].append(it)

    info_count = 0
    shown = 0
    for skill, group in skill_index.items():
        courses = {i["course"] for i in group}
        if len(courses) < 2:
            continue
        # Only count as INFO when stems are not exactly equal across courses
        stems = {i["text"] for i in group}
        if len(stems) == 1:
            continue  # exact handled above
        # Require at least one pair from different courses with similar-enough skill already keyed
        info_count += 1
        if shown < 8:
            codes = ", ".join(sorted(courses))
            info(
                f"CROSS COURSE + SAME SKILL ({codes}): "
                f"{skill[:60] or '(unnamed)'} "
                f"[{len(group)} items, {len(stems)} stems]"
            )
            shown += 1
    if info_count:
        info(
            f"{info_count} cross-course shared-skill group(s) with differing stems "
            "(informational; do not fail)"
        )
    else:
        info("No cross-course same-skill groups with differing stems")

    if same_course_exact == 0 and similar_fail == 0:
        ok("No same-course exact or essentially-same duplicates")


def main() -> int:
    conn = sqlite3.connect(PROD_DB)
    conn.row_factory = sqlite3.Row

    for code, expected in [
        ("MATH20-1", 300),
        ("MATH30-1", 293),
        ("MATH30-2", 300),
        ("BIO30", 300),
        ("CHEM30", 300),
        ("PHYS30", 300),
        ("SCI30", 300),
        ("SCI10", 300),
    ]:
        count = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN courses c ON t.course_id = c.id
            WHERE c.code = ? AND q.is_active = 1
            """,
            (code,),
        ).fetchone()[0]
        if count >= expected:
            ok(f"{code} count = {count}")
        else:
            fail(f"{code} count = {count}, expected >={expected}")

    _audit_duplicate_classification(conn)

    for label, sql in [
        ("user_answers", "SELECT COUNT(*) FROM user_answers ua LEFT JOIN questions q ON ua.question_id=q.id WHERE q.id IS NULL"),
        ("answer_choices", "SELECT COUNT(*) FROM answer_choices ac LEFT JOIN questions q ON ac.question_id=q.id WHERE q.id IS NULL"),
        ("question_history", "SELECT COUNT(*) FROM question_history qh LEFT JOIN questions q ON qh.question_id=q.id WHERE q.id IS NULL"),
        ("quiz_attempts course", "SELECT COUNT(*) FROM quiz_attempts qa LEFT JOIN courses c ON qa.course_id=c.id WHERE qa.course_id IS NOT NULL AND c.id IS NULL"),
    ]:
        n = conn.execute(sql).fetchone()[0]
        if n:
            fail(f"{n} orphan {label}")
        else:
            ok(f"No orphan {label}")

    for code in AUDITED_COURSE_CODES:
        missing_expl = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
            WHERE c.code=? AND q.is_active=1
            AND (q.explanation IS NULL OR LENGTH(TRIM(q.explanation)) < 10)
            """,
            (code,),
        ).fetchone()[0]
        if missing_expl:
            fail(f"{code}: {missing_expl} questions missing explanations")
        else:
            ok(f"{code}: all questions have explanations")

        mc_bad = conn.execute(
            """
            SELECT q.id FROM questions q
            JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
            WHERE c.code=? AND q.is_active=1 AND q.question_type='multiple_choice'
            AND q.id IN (
                SELECT question_id FROM answer_choices GROUP BY question_id
                HAVING SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) != 1
            )
            """,
            (code,),
        ).fetchall()
        if mc_bad:
            fail(f"{code}: {len(mc_bad)} MC questions without exactly one correct choice")
        else:
            ok(f"{code}: all MC have exactly one correct choice")

        nr_bad = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
            WHERE c.code=? AND q.is_active=1 AND q.question_type='numerical_response'
            AND (q.answer IS NULL OR LENGTH(TRIM(q.answer))=0)
            """,
            (code,),
        ).fetchone()[0]
        if nr_bad:
            fail(f"{code}: {nr_bad} NR questions missing answers")
        else:
            ok(f"{code}: all NR have answers")

        wr_bad = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
            WHERE c.code=? AND q.is_active=1 AND q.question_type='written_response'
            AND (q.answer IS NULL OR LENGTH(TRIM(q.answer))<10 OR q.explanation IS NULL OR LENGTH(TRIM(q.explanation))<20)
            """,
            (code,),
        ).fetchone()[0]
        if wr_bad:
            fail(f"{code}: {wr_bad} WR questions missing model answer or rubric")
        else:
            ok(f"{code}: all WR have model answers and rubrics")

    boiler = conn.execute(
        """
        SELECT COUNT(*) FROM questions q
        JOIN topics t ON q.topic_id=t.id JOIN courses c ON t.course_id=c.id
        WHERE c.code='BIO30' AND q.explanation LIKE 'The correct answer is%'
        """
    ).fetchone()[0]
    if boiler:
        fail(f"BIO30: {boiler} boilerplate explanations remain")
    else:
        ok("BIO30: no boilerplate explanations")

    attempts = conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    answers = conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0]
    ok(f"Preserved data: {attempts} quiz attempts, {answers} user answers")

    conn.close()
    print(f"\n=== AUDIT: {len(issues)} issue(s), {len(warnings)} warning(s) ===")
    # Warnings do not fail production readiness.
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
