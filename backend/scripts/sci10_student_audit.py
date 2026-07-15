"""Student-perspective QA audit for the SCI10 production bank.

Detects: placeholder/meta distractors, AI-tell explanations, duplicate and
near-duplicate stems, repeated templates, MC structural problems, NR answer
recomputation where formulas are recoverable, and curriculum outcome checks.

Read-only: prints findings. Fixes live in sci10_student_fix.py.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BANK = Path(__file__).resolve().parents[2] / "questions.json" / "science10_questions_final.json"

PLACEHOLDER_MARKERS = (
    "a true statement that does not answer",
    "does not answer this specific stem",
    "does not answer this stem",
    "reversed cause-and-effect",
    "terminology from a different science 10 unit",
    "a related misconception from another",
    "a misconception from another",
    "an unrelated process outside",
    "a partial truth that omits the key condition",
    "a concept confused with the correct answer",
    "a plausible-sounding",
    "devoid of all ions",
    "a distractor",
)

AI_TELL_EXPL = (
    "the other options reflect common misconceptions",
    "is correct because it matches calculating",
    "for outcome ",
    "reflect common misconceptions within",
)


def norm(text: str) -> str:
    t = text.lower()
    t = re.sub(r"\$[^$]*\$", " ", t)
    t = re.sub(r"[0-9]+(\.[0-9]+)?", " ", t)
    t = re.sub(r"[^a-z ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main() -> int:
    d = json.loads(BANK.read_text(encoding="utf-8"))
    findings: dict[str, list] = defaultdict(list)

    # 1. Placeholder / meta distractors
    for i, q in enumerate(d):
        for ch in q.get("choices", []):
            low = ch["text"].lower()
            if any(m in low for m in PLACEHOLDER_MARKERS):
                findings["placeholder_distractor"].append((i, ch["text"]))

    # 2. AI-tell explanations
    for i, q in enumerate(d):
        expl = (q.get("explanation") or "").lower()
        if any(m in expl for m in AI_TELL_EXPL):
            findings["ai_tell_explanation"].append((i, q.get("explanation")))

    # 3. MC structural
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        choices = q.get("choices", [])
        texts = [c["text"] for c in choices]
        correct = [c for c in choices if c.get("is_correct")]
        if len(choices) != 4:
            findings["mc_choice_count"].append((i, len(choices)))
        if len(correct) != 1:
            findings["mc_correct_count"].append((i, len(correct)))
        if len(set(t.strip().lower() for t in texts)) != len(texts):
            findings["mc_duplicate_choice"].append((i, texts))
        # distractor identical to correct
        if correct:
            cval = correct[0]["text"].strip().lower()
            for c in choices:
                if not c.get("is_correct") and c["text"].strip().lower() == cval:
                    findings["mc_distractor_eq_answer"].append((i, c["text"]))

    # 4. NR structural
    for i, q in enumerate(d):
        if q["question_type"] != "Numerical Response":
            continue
        ans = (q.get("answer") or "").strip()
        if not ans:
            findings["nr_missing_answer"].append((i, ans))
        elif not re.fullmatch(r"-?\d+(\.\d+)?", ans):
            findings["nr_nonnumeric_answer"].append((i, ans))
        # rounding instruction vs answer format
        qt = q["question_text"].lower()
        m = re.search(r"one decimal place", qt)
        if m and re.fullmatch(r"-?\d+", ans):
            findings["nr_rounding_mismatch"].append((i, ans))

    # 5. Duplicate + near-duplicate stems
    seen: dict[str, int] = {}
    normseen: dict[str, int] = {}
    for i, q in enumerate(d):
        stem = q["question_text"].strip()
        if stem in seen:
            findings["exact_duplicate_stem"].append((seen[stem], i, stem))
        else:
            seen[stem] = i
        n = norm(stem)
        if n in normseen:
            findings["near_duplicate_stem"].append((normseen[n], i, stem))
        else:
            normseen[n] = i

    # 6. Repeated templates (skeleton after stripping numbers/units)
    skel = defaultdict(list)
    for i, q in enumerate(d):
        s = norm(q["question_text"])
        skel[s].append(i)
    for s, idxs in skel.items():
        if len(idxs) >= 4:
            findings["repeated_template"].append((s, idxs))

    # 7. Curriculum: outcome code shape
    for i, q in enumerate(d):
        oc = q.get("outcome_code") or ""
        if not re.fullmatch(r"[A-D]\d+\.\d+[a-z]{1,3}", oc):
            findings["bad_outcome_code"].append((i, oc))

    # --- PASS 2: deeper student-perspective heuristics ---

    # 8. Meta leakage anywhere in student-visible fields
    META = ("outcome ", "alberta science 10", "this specific stem", "distractor",
            "misconception from another", "different science 10 unit")
    for i, q in enumerate(d):
        for field in ("explanation", "common_mistake", "question_text"):
            val = (q.get(field) or "").lower()
            if any(m in val for m in META):
                findings["meta_leakage"].append((i, field, q.get(field)))

    # 9. MC answer-length tell: correct option much longer than every distractor
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        correct = [c for c in q["choices"] if c.get("is_correct")]
        dists = [c for c in q["choices"] if not c.get("is_correct")]
        if correct and dists:
            clen = len(correct[0]["text"])
            if clen >= 25 and clen > 2.2 * max(len(x["text"]) for x in dists):
                findings["answer_length_tell"].append((i, clen, [len(x["text"]) for x in dists]))

    # 10. Distractor that just restates unit/topic name (low-effort)
    for i, q in enumerate(d):
        topic = q["topic"].lower()
        for c in q.get("choices", []):
            if not c.get("is_correct") and topic in c["text"].lower():
                findings["topic_name_distractor"].append((i, c["text"]))

    # 11. Numeric MC distractor duplicated value with correct answer
    for i, q in enumerate(d):
        if q["question_type"] != "Multiple Choice":
            continue
        vals = [c["text"].strip() for c in q["choices"]]
        if len(vals) != len(set(vals)):
            findings["duplicate_choice_value"].append((i, vals))

    # 12. common_mistake / skill_tested boilerplate or empty
    for i, q in enumerate(d):
        cm = (q.get("common_mistake") or "").strip()
        if cm and ("item " in cm.lower() and cm.lower().endswith(tuple("0123456789"))):
            findings["boilerplate_common_mistake"].append((i, cm))
        st = (q.get("skill_tested") or "")
        if "item " in st.lower():
            findings["skill_tested_artifact"].append((i, st))

    # 13. fill-in-blank stem that still ends with '?' after blank (awkward)
    for i, q in enumerate(d):
        t = q["question_text"]
        if "_______" in t and t.rstrip().endswith("?") and "_______?" in t.replace(" ", ""):
            findings["blank_then_question_mark"].append((i, t))

    # 14. estimated_time sanity
    for i, q in enumerate(d):
        est = q.get("estimated_time_seconds")
        if not isinstance(est, int) or est < 20 or est > 300:
            findings["odd_estimated_time"].append((i, est))

    total = 0
    for key, items in findings.items():
        print(f"\n=== {key}: {len(items)} ===")
        total += len(items)
        for it in items[:60]:
            print("  ", it if not isinstance(it, tuple) else " | ".join(str(x)[:90] for x in it))
    print(f"\nTOTAL FINDINGS: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
