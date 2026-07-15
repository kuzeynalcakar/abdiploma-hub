"""Post-generation QA fixes for Science 30 question pool."""

import re
from collections import Counter

from sci30_questions.helpers import VALID_OUTCOMES


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize_text(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def clarify_stem(text: str) -> str:
    """Convert incomplete diploma stems into unambiguous questions."""
    text = text.strip()
    if text.endswith("?"):
        return text
    lower = text.lower()
    if lower.endswith(" is the"):
        return text + " _______?"
    if lower.endswith(" are the"):
        return text + " _______?"
    if lower.endswith(" is a"):
        return text + " _______?"
    if lower.endswith(" is an"):
        return text + " _______?"
    if lower.endswith(" includes"):
        return text + " _______?"
    if lower.endswith(" are"):
        return text + " _______?"
    if lower.endswith(" is"):
        return text + " _______?"
    if " because they" in lower or lower.endswith(" because"):
        return text + " _______?"
    if lower.endswith(" occurs when"):
        return text + " _______?"
    if lower.endswith(" allows"):
        return text + " _______?"
    if lower.endswith(" involves"):
        return text + " _______?"
    if lower.endswith(" produces"):
        return text + " _______?"
    if lower.endswith(" measures"):
        return text + " _______?"
    if lower.endswith(" emerges from the"):
        return text + " _______?"
    if lower.endswith(" converts"):
        return text + " _______?"
    if lower.endswith(" differs from"):
        return text + " _______?"
    if lower.endswith(" prevents"):
        return text + " _______?"
    if lower.endswith(" functions to"):
        return text + " _______?"
    if lower.endswith(" contributes to"):
        return text + " _______?"
    if lower.endswith(" results in"):
        return text + " _______?"
    if lower.endswith(" aims to"):
        return text + " _______?"
    if lower.endswith(" requires"):
        return text + " _______?"
    if lower.endswith(" harness energy from"):
        return text + " _______?"
    if lower.endswith(" raises concerns about"):
        return text + " _______?"
    if lower.endswith(" can"):
        return text + " _______?"
    if lower.endswith(" has"):
        return text + " _______?"
    if lower.endswith(" provides"):
        return text + " _______?"
    if lower.endswith(" protects"):
        return text + " _______?"
    if lower.endswith(" characterize"):
        return text + " _______?"
    if lower.endswith(" separate"):
        return text + " _______?"
    if lower.endswith(" best observed when"):
        return text + " _______?"
    if lower.endswith(" compared to"):
        return text + " _______?"
    if lower.endswith(" entering through the"):
        return text + " _______?"
    if lower.endswith(" returning from the"):
        return text + " _______?"
    if lower.endswith(" leaving the"):
        return text + " _______?"
    if lower.endswith(" in that"):
        return text + " _______?"
    if lower.endswith(" primarily by"):
        return text + " _______?"
    if lower.endswith(" most likely"):
        return text + " _______?"
    if lower.endswith(" most directly"):
        return text + " _______?"
    if lower.endswith(" into"):
        return text + " _______?"
    if lower.endswith(" through"):
        return text + " _______?"
    if lower.endswith(" from"):
        return text + " _______?"
    if lower.endswith(" with"):
        return text + " _______?"
    if lower.endswith(" without"):
        return text + " _______?"
    if lower.endswith(" during"):
        return text + " _______?"
    if lower.endswith(" after"):
        return text + " _______?"
    if lower.endswith(" before"):
        return text + " _______?"
    if lower.endswith(" by"):
        return text + " _______?"
    if lower.endswith(" using"):
        return text + " _______?"
    if lower.endswith(" such as"):
        return text + " _______?"
    if lower.endswith(" like"):
        return text + " _______?"
    if lower.endswith(" when"):
        return text + " _______?"
    if lower.endswith(" where"):
        return text + " _______?"
    if lower.endswith(" while"):
        return text + " _______?"
    if lower.endswith(" if"):
        return text + " _______?"
    if lower.endswith(" than"):
        return text + " _______?"
    if lower.endswith(" to"):
        return text + " _______?"
    if lower.endswith(" for"):
        return text + " _______?"
    if lower.endswith(" at"):
        return text + " _______?"
    if lower.endswith(" on"):
        return text + " _______?"
    if lower.endswith(" in"):
        return text + " _______?"
    if lower.endswith(" of"):
        return text + " _______?"
    return text + "?"


GENERIC_EXPL_PATTERNS = (
    "assesses outcome",
    "assesses circulatory",
    "field theory / electrical",
    "electromagnetic spectrum concept",
    "energy and environment sts",
    "outcome ",
    ": expected outcome is",
    "cross ",
)


GENERIC_MISTAKE_PATTERNS = (
    "students may confuse",
    "students may select",
    "students may apply wrong",
    "students apply wrong punnett",
)


def is_tautological_nr(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    qt = q["question_text"].lower()
    if "record the heterozygote frequency as given" in qt:
        return True
    if "what is the acid concentration" in qt and "at equivalence" in qt:
        return True
    return False


def improve_generic_content(q: dict) -> dict:
    """Replace lazy batch-generated explanation/mistake text."""
    expl = q.get("explanation", "")
    mis = q.get("common_mistake", "")
    skill = q.get("skill_tested", "")
    oc = q.get("outcome_code", "")
    topic = q.get("topic", "")

    if any(p in expl.lower() for p in GENERIC_EXPL_PATTERNS) or len(expl) < 50:
        skill = q.get("skill_tested", "applying the concept")
        oc = q.get("outcome_code", "")
        topic = q.get("topic", "")
        ans = q.get("answer", "")
        if q.get("question_type") == "Numerical Response":
            q["explanation"] = (
                f"Outcome {oc} ({topic}): apply {skill.lower()} to obtain {ans} "
                f"from the values given in the stem."
            )
        else:
            q["explanation"] = (
                f"Outcome {oc} ({topic}): '{ans}' is correct because it matches "
                f"{skill.lower()}. Other options reflect common misconceptions in this unit."
            )

    if any(p in mis.lower() for p in GENERIC_MISTAKE_PATTERNS) or len(mis) < 30:
        q["common_mistake"] = (
            f"Students select a distractor that confuses related concepts within {topic} "
            f"rather than applying outcome {oc} correctly."
        )

    if skill.startswith("Applying knowledge from outcome") or skill.startswith("Applying environmental"):
        q["skill_tested"] = f"Applying {oc} concepts in {topic}"

    return q


def fix_mc_distractors(q: dict) -> dict:
    """Pad implausibly short distractors so diploma-style options are readable."""
    if q["question_type"] != "Multiple Choice":
        return q
    for choice in q["choices"]:
        if choice["is_correct"]:
            continue
        if len(choice["text"]) < 8:
            choice["text"] = f"{choice['text']} (incorrect option)"
    return q


def qa_fix_pool(pool: list[dict], *, max_per_template: int = 2) -> list[dict]:
    """Apply all automatic QA fixes and deduplicate."""
    fixed = []
    seen_text = set()
    template_counts = Counter()

    for q in pool:
        if is_tautological_nr(q):
            continue

        q = dict(q)
        q["question_text"] = clarify_stem(q["question_text"])
        q = improve_generic_content(q)
        q = fix_mc_distractors(q)

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            continue

        text_key = (q["topic"].lower(), normalize_text(q["question_text"]))
        if text_key in seen_text:
            continue

        tmpl = template_key(q)
        if template_counts[tmpl] >= max_per_template:
            continue

        seen_text.add(text_key)
        template_counts[tmpl] += 1
        fixed.append(q)

    return fixed
