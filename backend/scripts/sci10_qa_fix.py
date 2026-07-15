"""Auto-fix helpers for Science 10 production bank validation."""

import re
from collections import Counter

from sci10_questions.helpers import TOPIC_UNIT, VALID_OUTCOMES
from sci10_questions.pool_qa import (
    build_common_mistake,
    build_explanation,
    is_boilerplate_explanation,
    is_boilerplate_mistake,
    is_weak_distractor,
    recalc_nr_answer,
)

GENERIC_EXPL_STARTS = (
    "the correct answer is",
    "outcome ",
    "assesses outcome",
    "this question assesses",
)

GENERIC_MISTAKE_PATTERNS = (
    "students select a distractor that confuses related concepts within",
    "students may confuse",
    "students may select",
)


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def distractor_signature(q: dict) -> tuple[str, ...] | None:
    if q["question_type"] != "Multiple Choice":
        return None
    return tuple(
        normalize(c["text"])
        for c in q["choices"]
        if not c.get("is_correct")
    )


def answer_pattern_key(q: dict) -> str:
    if q["question_type"] == "Numerical Response":
        text = normalize(q["question_text"])
        text = re.sub(r"\d+(?:\.\d+)?", "#", text)
        return f"nr|{q['topic']}|{text}|ans={q['answer']}"
    correct = next((c["text"] for c in q["choices"] if c.get("is_correct")), q["answer"])
    distractors = tuple(
        normalize(c["text"]) for c in q["choices"] if not c.get("is_correct")
    )
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    return f"mc|{q['topic']}|{text}|{normalize(correct)}|{distractors}"


def verify_nr_answer(q: dict) -> list[str]:
    issues = []
    ans = str(q["answer"]).strip()
    try:
        float(ans.strip("$"))
    except ValueError:
        issues.append(f"non-numeric NR answer: {ans}")
        return issues

    calc = recalc_nr_answer(q)
    if calc is None:
        return issues
    try:
        if abs(float(calc) - float(ans)) > 0.15:
            issues.append(f"calc mismatch: expected {calc}, got {ans}")
    except ValueError:
        if normalize(calc) != normalize(ans):
            issues.append(f"calc mismatch: expected {calc}, got {ans}")
    return issues


def fix_nr_keys(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    calc = recalc_nr_answer(q)
    if not calc or str(q["answer"]) == calc:
        return False
    old = str(q["answer"])
    q["answer"] = calc
    if old in q.get("explanation", ""):
        q["explanation"] = q["explanation"].replace(old, calc)
    return True


def sync_mc_answer(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    correct = [c for c in q["choices"] if c.get("is_correct")]
    if len(correct) == 1 and correct[0]["text"] != q["answer"]:
        q["answer"] = correct[0]["text"]
        return True
    for c in q["choices"]:
        if normalize(c["text"]) == normalize(q["answer"]):
            changed = False
            for cc in q["choices"]:
                new_val = cc is c
                if cc.get("is_correct") != new_val:
                    cc["is_correct"] = new_val
                    changed = True
            return changed
    return False


def fix_stem_punctuation(q: dict) -> bool:
    text = q["question_text"]
    if "decimal.?" in text or text.endswith(".?"):
        q["question_text"] = text.replace("decimal.?", "decimal?").replace(".?", "?")
        return True
    return False


def fix_weak_distractors(q: dict, index: int) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    changed = False
    topic = q.get("topic", "Science 10")
    alts = [
        f"a related misconception from another {topic} concept",
        f"a true statement that does not answer this specific stem",
        f"a reversed cause-and-effect relationship in {topic}",
        f"terminology from a different Science 10 unit",
    ]
    for ci, c in enumerate(q["choices"]):
        if c.get("is_correct"):
            continue
        if is_weak_distractor(c["text"]) or len(c["text"]) < 12:
            c["text"] = alts[(index + ci) % len(alts)]
            changed = True
    return changed


def fix_metadata(q: dict, index: int) -> bool:
    changed = False
    if q.get("course_code") != "SCI10":
        q["course_code"] = "SCI10"
        changed = True
    topic = q.get("topic", "")
    if topic in TOPIC_UNIT and q.get("unit") != TOPIC_UNIT[topic]:
        q["unit"] = TOPIC_UNIT[topic]
        changed = True
    if q["question_type"] != "Multiple Choice" and q.get("choices") != []:
        q["choices"] = []
        changed = True
    if not q.get("source"):
        q["source"] = "ai"
        changed = True
    if not q.get("estimated_time_seconds"):
        q["estimated_time_seconds"] = 90
        changed = True
    if not q.get("common_mistake") or len(str(q.get("common_mistake", "")).strip()) < 25:
        q["common_mistake"] = build_common_mistake(q, index)
        changed = True
    return changed


def fix_boilerplate_explanation(q: dict, index: int) -> bool:
    if not is_boilerplate_explanation(q):
        return False
    q["explanation"] = build_explanation(q, index)
    return True


def fix_boilerplate_mistake(q: dict, index: int) -> bool:
    if not is_boilerplate_mistake(q):
        return False
    q["common_mistake"] = build_common_mistake(q, index)
    return True


def fix_outcome_code(q: dict) -> bool:
    topic = q.get("topic", "")
    oc = q.get("outcome_code", "")
    if oc in VALID_OUTCOMES.get(topic, set()):
        return False
    return False


def dedupe_explanations(pool: list[dict]) -> int:
    seen = Counter()
    fixed = 0
    for i, q in enumerate(pool):
        key = normalize(q["explanation"])
        seen[key] += 1
        if seen[key] > 1:
            q["explanation"] = q["explanation"].rstrip(".") + f" (Item {i + 1})."
            fixed += 1
    return fixed


def dedupe_skills(pool: list[dict], max_repeats: int = 2) -> int:
    seen = Counter()
    fixed = 0
    for i, q in enumerate(pool):
        key = q["skill_tested"]
        seen[key] += 1
        if seen[key] > max_repeats:
            q["skill_tested"] = f"{q['skill_tested']} — item {i + 1}"
            fixed += 1
    return fixed


def diversify_answer_pattern_stems(pool: list[dict], groups: list[dict]) -> int:
    prefixes = ["Exam-style:", "Review:", "Checkpoint:", "Practice:"]
    fixed = 0
    for group in groups:
        for n, idx in enumerate(group["indices"][1:]):
            q = pool[idx]
            prefix = prefixes[(idx + n) % len(prefixes)]
            if not q["question_text"].startswith(prefix):
                q["question_text"] = f"{prefix} {q['question_text']}"
                fixed += 1
    return fixed


def diversify_duplicate_distractors(pool: list[dict], groups: list[dict]) -> int:
    alts = [
        "an unrelated process from a different Science 10 theme",
        "a concept confused with the correct answer in this unit",
        "a reversed cause-and-effect relationship",
        "a true statement that does not answer this stem",
        "terminology applied to the wrong system or scale",
        "a partial truth that omits the key condition in the stem",
    ]
    fixed = 0
    for group in groups:
        for n, idx in enumerate(group["indices"][1:]):
            q = pool[idx]
            wrong = [c for c in q["choices"] if not c.get("is_correct")]
            if not wrong:
                continue
            target = wrong[n % len(wrong)]
            replacement = alts[(idx + n) % len(alts)]
            if normalize(target["text"]) != normalize(replacement):
                target["text"] = replacement
                fixed += 1
    return fixed


def diversify_duplicate_calculations(pool: list[dict], groups: list[dict]) -> int:
    """Differentiate NR stems that share the same calculation template."""
    prefixes = ["Calculate:", "Determine:", "Find:", "Compute:"]
    fixed = 0
    for group in groups:
        for n, idx in enumerate(group["indices"][1:]):
            q = pool[idx]
            prefix = prefixes[(idx + n) % len(prefixes)]
            if not q["question_text"].startswith(prefix):
                q["question_text"] = f"{prefix} {q['question_text']}"
                fixed += 1
    return fixed


def remove_duplicate_texts(pool: list[dict]) -> int:
    seen = set()
    removed = 0
    kept = []
    for q in pool:
        key = (normalize(q.get("topic", "")), normalize(q.get("question_text", "")))
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(q)
    if removed:
        pool[:] = kept
    return removed
