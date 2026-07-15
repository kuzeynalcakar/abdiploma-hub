"""Full QA audit of Science 30 question pool."""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question, validate_file
from sci30_questions.helpers import VALID_OUTCOMES

POOL = Path(__file__).parent.parent.parent / "questions.json" / "science30_questions_pool.json"


def safe_print(text: str) -> None:
    """Print audit output without Windows console encoding failures."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize_text(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def audit(pool: list[dict]) -> dict:
    issues = defaultdict(list)

    valid_count, invalid = validate_file(pool)
    for idx, reason in invalid:
        issues["schema"].append((idx, reason))

    for i, q in enumerate(pool):
        topic = q.get("topic", "")
        oc = q.get("outcome_code", "")
        if oc not in VALID_OUTCOMES.get(topic, set()):
            issues["outcome_mismatch"].append((i, topic, oc))

    # MC answer key checks
    for i, q in enumerate(pool):
        if q["question_type"] != "Multiple Choice":
            continue
        texts = [c["text"] for c in q["choices"]]
        correct = [c for c in q["choices"] if c["is_correct"]]
        if len(correct) == 1 and q["answer"] != correct[0]["text"]:
            issues["wrong_key"].append((i, q["answer"], correct[0]["text"]))
        if q["answer"] not in texts:
            issues["answer_not_in_choices"].append((i, q["answer"]))
        if len(set(texts)) < 4:
            issues["duplicate_choices"].append((i, texts))
        # weak distractors: too short or identical start
        wrong = [c["text"] for c in q["choices"] if not c["is_correct"]]
        if any(len(w) < 8 for w in wrong):
            issues["weak_distractor"].append((i, wrong))
        if any(w.lower().startswith("all ") and "only" in w.lower() for w in wrong):
            issues["implausible_distractor"].append((i, wrong))

    # Generic/lazy content from batch generators
    for i, q in enumerate(pool):
        expl = q.get("explanation", "")
        if (
            expl.startswith("Assesses")
            or expl.startswith("This question assesses")
            or "Assesses outcome" in expl
            or expl.startswith("Field theory / electrical energy")
            or expl.startswith("Electromagnetic spectrum concept assessment")
            or expl.startswith("Energy and environment STS")
            or expl.startswith("Assesses circulatory")
            or len(expl) < 45
        ):
            issues["weak_explanation"].append((i, expl[:80]))

        mis = q.get("common_mistake", "")
        if (
            mis.startswith("Students may confuse")
            or mis.startswith("Students may select")
            or mis.startswith("Students may apply wrong")
            or len(mis) < 25
        ):
            issues["weak_common_mistake"].append((i, mis[:80]))

        if q["question_type"] == "Multiple Choice" and q["question_text"].count("?") == 0 and "which" not in q["question_text"].lower()[:20]:
            if not q["question_text"].rstrip().endswith("?"):
                issues["ambiguous_wording"].append((i, q["question_text"][:100]))

    # Suspicious NR - tautological
    for i, q in enumerate(pool):
        if q["question_type"] != "Numerical Response":
            continue
        qt = q["question_text"].lower()
        if "record the heterozygote frequency as given" in qt:
            issues["grading_ambiguity"].append((i, "tautological het freq"))
        if "record as given" in qt or "as stated" in qt:
            issues["grading_ambiguity"].append((i, "record as given"))
        # titration verify questions where answer is just restating given M
        if "what is the acid concentration" in qt and "at equivalence" in qt:
            issues["grading_ambiguity"].append((i, "titration restate"))

    # Template repetition
    tc = Counter(template_key(q) for q in pool)
    for k, c in tc.items():
        if c > 2:
            issues["duplicate_template"].append((k, c))

    # Repeated skills/explanations/mistakes
    for field, threshold in [("skill_tested", 4), ("explanation", 3), ("common_mistake", 3)]:
        fc = Counter(q[field] for q in pool)
        for val, cnt in fc.items():
            if cnt > threshold:
                issues[f"repeated_{field}"].append((val, cnt))

    # Factual spot checks
    for i, q in enumerate(pool):
        qt = q["question_text"].lower()
        ans = q["answer"].lower()
        if "geothermal" in qt and "solar radiation" in ans:
            issues["factual_error"].append((i, "geothermal solar confusion"))
        if "emr speed" in qt and "increases with frequency" in ans:
            issues["factual_error"].append((i, "emr speed frequency"))

    # gen_crosses wrong answers
    for i, q in enumerate(pool):
        if "produces what proportion showing" in q["question_text"]:
            if q["answer"] in ("50% AA and 50% Aa", "100% Bb"):
                issues["wrong_key"].append((i, q["answer"], "check punnett"))

    return dict(issues)


def main():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    safe_print(f"Pool: {len(pool)} questions\n")
    issues = audit(pool)
    total = 0
    for cat in sorted(issues):
        items = issues[cat]
        total += len(items)
        safe_print(f"=== {cat}: {len(items)} ===")
        for item in items[:8]:
            safe_print(f"  {item}")
        if len(items) > 8:
            safe_print(f"  ... and {len(items)-8} more")
        safe_print("")
    safe_print(f"TOTAL ISSUE ENTRIES: {total}")
    if total > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
