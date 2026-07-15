"""Audit Biology 30 question types against Alberta diploma best practices."""

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
INPUT = HERE / "biology30_questions_final.json"

WR_STEM_VERBS = re.compile(
    r"\b("
    r"explain|describe|justify|compare|contrast|evaluate|discuss|"
    r"analyze|analyse|interpret|recommend|support(?:\s+a\s+claim)?|"
    r"advantages?|disadvantages?"
    r")\b",
    re.I,
)

# Predict/analyze in skill_tested often means application, not constructed response.
PREDICT_STEM = re.compile(r"\b(predict|predicting)\b", re.I)

RECALL_MC = re.compile(
    r"^(?:what is|what are|which of the following|the primary|the main|"
    r"the function of|the role of|the site of|the product of|"
    r"the stage of|the hormone that|the enzyme that|the structure that|"
    r"the cell type that|the process that|the term for|define |identify the )",
    re.I,
)

BOILERPLATE_EXPL = re.compile(r"^The correct answer is ", re.I)

# NR answers that are probabilities, counts, percentages, sequences — keep NR.
# Validator only accepts numeric strings for NR.

# MC questions that are really "pick the one phrase" without reasoning distractors
SENTENCE_ANSWER_MC = 55  # chars threshold for long keyed answers


def classify_question(index: int, q: dict) -> tuple[str | None, str]:
    """Return (proposed_type_or_None, reason). None = keep current type."""
    current = q["question_type"]
    text = q["question_text"]
    skill = q.get("skill_tested", "")
    answer = str(q.get("answer", ""))

    if current == "Written Response":
        return None, "already written response"

    if WR_STEM_VERBS.search(text):
        return "Written Response", f"stem requires constructed response ({WR_STEM_VERBS.search(text).group(0)})"

    if current == "Numerical Response":
        if BOILERPLATE_EXPL.match(q.get("explanation", "")):
            # Boilerplate NR often masks reasoning/application items.
            if re.search(
                r"\b(explain|describe|why|how|compare|predict|determine the relationship|"
                r"explain why|account for|interpret)\b",
                text,
                re.I,
            ):
                return (
                    "Written Response",
                    "NR item requires biological reasoning, not a single numeric response",
                )
            if "order" in text.lower() or "sequence" in text.lower():
                return (
                    "Written Response",
                    "sequencing question needs constructed response, not numeric code",
                )
        # Keep objective numeric NR
        return None, "objective numeric/single-value response"

    # Multiple Choice
    if RECALL_MC.search(text) and len(answer) < SENTENCE_ANSWER_MC:
        # Pure recall with short answer — better as NR if numeric, else keep MC or WR
        if _is_numeric_answer(answer):
            return (
                "Numerical Response",
                "recall question with single numeric answer suits NR format",
            )
        # Short non-numeric recall (e.g. stage name, hormone name) — validator requires
        # numeric for NR, so keep MC unless it's a sentence requiring justification.
        return None, "recall MC with discrete answer — MC tests discrimination"

    if len(answer) >= SENTENCE_ANSWER_MC and re.search(
        r"\b(most likely|because|would|mechanism|pathway|effect|result|consequence)\b",
        text,
        re.I,
    ):
        return (
            "Written Response",
            "MC keyed to a full explanatory statement — constructed response expected",
        )

    if re.search(r"\b(how|why)\b", text, re.I) and "?" not in text:
        # Incomplete stem but asks how/why implicitly
        if len(answer) >= 40:
            return (
                "Written Response",
                "how/why reasoning cannot be reduced to selecting one phrase",
            )

    if re.search(r"\b(STS|ethical|economic|ecological|social)\b", text, re.I) and current == "Multiple Choice":
        return (
            "Written Response",
            "STS/evaluative question requires constructed response",
        )

    if PREDICT_STEM.search(text):
        # Prediction of specific outcome with plausible distractors — keep MC
        return None, "prediction with discrete outcomes — MC appropriate"

    return None, "MC format appropriately tests reasoning among alternatives"


def _is_numeric_answer(value) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    text = str(value).strip().strip("$").strip().rstrip("%")
    try:
        float(text)
        return True
    except ValueError:
        return False


def main() -> None:
    items = json.loads(INPUT.read_text(encoding="utf-8"))
    print(f"Total: {len(items)}")
    print("Current:", Counter(q["question_type"] for q in items))

    changes = []
    for i, q in enumerate(items):
        proposed, reason = classify_question(i, q)
        if proposed and proposed != q["question_type"]:
            changes.append((i, q["question_type"], proposed, reason, q["question_text"][:90]))

    print(f"\nProposed changes: {len(changes)}")
    by_transition = Counter((a, b) for _, a, b, _, _ in changes)
    print("Transitions:", dict(by_transition))

    proposed_counts = Counter(q["question_type"] for q in items)
    for _, old, new, _, _ in changes:
        proposed_counts[old] -= 1
        proposed_counts[new] += 1
    print("Proposed:", dict(proposed_counts))

    for i, old, new, reason, stem in changes:
        print(f"\n[{i}] {old} -> {new}")
        print(f"  Why: {reason}")
        print(f"  Q: {stem}")


if __name__ == "__main__":
    main()
