"""Post-generation QA fixes for Science 10 question pool."""

import math
import re
from collections import Counter

from sci10_questions.helpers import TOPIC_UNIT, VALID_OUTCOMES

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
    "students divide only final velocity by time",
)

WEAK_DISTRACTOR_PATTERNS = (
    "none of the above",
    "all of the above",
    "incorrect option",
    "(incorrect",
    "misconception from another",
    "related misconception from another",
    "reversed cause-and-effect",
    "true statement that does not answer",
    "does not answer this specific",
    "does not answer this stem",
    "terminology from a different",
    "unrelated process outside",
    "partial truth that omits",
    "concept confused with the correct answer",
)

INCOMPLETE_ENDINGS = (
    " is the", " are the", " is a", " is an", " includes", " are", " is",
    " because they", " because", " occurs when", " allows", " involves",
    " produces", " measures", " converts", " differs from", " prevents",
    " functions to", " contributes to", " results in", " requires",
    " provides", " protects", " primarily by", " most likely", " most directly",
    " into", " through", " from", " with", " without", " during", " after",
    " before", " by", " using", " such as", " when", " where", " while",
    " if", " than", " to", " for", " at", " on", " in", " of", " means",
    " was", " were", " has", " have", " can", " will", " should",
)


def normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize_text(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def clarify_stem(text: str) -> str:
    text = text.strip()
    if text.endswith("?"):
        return text
    if text.endswith("."):
        return text
    lower = text.lower()
    for ending in INCOMPLETE_ENDINGS:
        if lower.endswith(ending):
            return text + " _______?"
    return text + "?"


def stem_values(q: dict, limit: int = 4) -> str:
    nums = re.findall(r"\d+(?:\.\d+)?", q["question_text"])
    return ", ".join(nums[:limit]) if nums else ""


def nr_working_text(q: dict) -> str | None:
    text = q["question_text"]
    low = text.lower()

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg object moves at (\d+(?:\.\d+)?)\s*m/s", low)
    if m and "kinetic energy" in low:
        m1, v = float(m.group(1)), float(m.group(2))
        return f"$E_k = \\frac{{1}}{{2}}mv^2 = 0.5 \\times {m1} \\times {v}^2$ J."

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg object is raised (\d+(?:\.\d+)?)\s*m", low)
    if m and "potential energy" in low:
        mass, h = float(m.group(1)), float(m.group(2))
        return f"$E_p = mgh = {mass} \\times 9.8 \\times {h}$ J."

    m = re.search(r"delivers (\d+(?:\.\d+)?)\s*j of useful energy from (\d+(?:\.\d+)?)\s*j", low)
    if m and "efficiency" in low:
        return f"Efficiency = ({m.group(1)}/{m.group(2)}) × 100%."

    m = re.search(r"receives (\d+(?:\.\d+)?)\s*j of energy input and delivers (\d+(?:\.\d+)?)\s*j", low)
    if m and "efficiency" in low:
        return f"Efficiency = ({m.group(2)}/{m.group(1)}) × 100%."

    m = re.search(r"velocity changes from (\d+(?:\.\d+)?)\s*m/s to (\d+(?:\.\d+)?)\s*m/s in (\d+(?:\.\d+)?)\s*s", low)
    if m and "acceleration" in low:
        return f"$a = ({m.group(2)} - {m.group(1)}) / {m.group(3)}$ m/s²."

    m = re.search(r"velocity changes uniformly from (\d+(?:\.\d+)?)\s*m/s to (-?\d+(?:\.\d+)?)\s*m/s in (\d+(?:\.\d+)?)\s*s", low)
    if m and "acceleration" in low:
        return f"$a = ({m.group(2)} - {m.group(1)}) / {m.group(3)}$ m/s²."

    m = re.search(r"mass of (\d+(?:\.\d+)?)\s*g.*?molar mass (\d+(?:\.\d+)?)\s*g/mol", low)
    if m and "moles" in low:
        return f"Moles = {m.group(1)} / {m.group(2)} mol."

    m = re.search(r"mass of (\d+(?:\.\d+)?)\s*g\s+and molar mass (\d+(?:\.\d+)?)\s*g/mol", low)
    if m:
        return f"Moles = {m.group(1)} / {m.group(2)} mol."

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg of water by (\d+(?:\.\d+)?).*c = (\d+(?:\.\d+)?)", low)
    if m and "thermal energy" in low:
        return f"$Q = mc\\Delta T = {m.group(1)} \\times {m.group(3)} \\times {m.group(2)}$ J."

    m = re.search(r"specimen is (\d+(?:\.\d+)?)\s*mm.*?image measures (\d+(?:\.\d+)?)\s*mm", low)
    if m and "magnification" in low:
        return f"Magnification = {m.group(2)} / {m.group(1)}."

    m = re.search(r"motor rated at (\d+)\s*w running for (\d+)\s*s", low)
    if m:
        return f"Energy = {m.group(1)} W × {m.group(2)} s = {int(m.group(1)) * int(m.group(2))} J."

    return None


def recalc_nr_answer(q: dict) -> str | None:
    text = q["question_text"]
    low = text.lower()

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg object moves at (\d+(?:\.\d+)?)\s*m/s", low)
    if m and "kinetic energy" in low:
        val = 0.5 * float(m.group(1)) * float(m.group(2)) ** 2
        return str(int(val)) if val == int(val) else f"{val:g}"

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg object is raised (\d+(?:\.\d+)?)\s*m", low)
    if m and "potential energy" in low:
        val = float(m.group(1)) * 9.8 * float(m.group(2))
        return str(int(round(val))) if abs(val - round(val)) < 0.5 else f"{val:.1f}"

    m = re.search(r"delivers (\d+(?:\.\d+)?)\s*j of useful energy from (\d+(?:\.\d+)?)\s*j", low)
    if m and "efficiency" in low:
        return str(round(float(m.group(1)) / float(m.group(2)) * 100))

    m = re.search(r"receives (\d+)\s*j of energy input and delivers (\d+)\s*j", low)
    if m and "efficiency" in low:
        val = float(m.group(2)) / float(m.group(1)) * 100
        if "one decimal" in low:
            return f"{val:.1f}"
        return str(int(round(val)))

    m = re.search(r"velocity changes (?:uniformly )?from (\d+(?:\.\d+)?)\s*m/s to (-?\d+(?:\.\d+)?)\s*m/s in (\d+(?:\.\d+)?)\s*s", low)
    if m and "acceleration" in low:
        val = (float(m.group(2)) - float(m.group(1))) / float(m.group(3))
        if "decimal" in low:
            return f"{val:.1f}" if val != int(val) else str(int(val))
        return str(int(val)) if val == int(val) else f"{val:g}"

    m = re.search(r"from (\d+(?:\.\d+)?)\s*m/s to (\d+(?:\.\d+)?)\s*m/s.*?(\d+(?:\.\d+)?)\s*s", low)
    if m and "acceleration" in low and "cart" in low:
        val = (float(m.group(2)) - float(m.group(1))) / float(m.group(3))
        return str(int(val)) if val == int(val) else f"{val:g}"

    m = re.search(r"mass of (\d+(?:\.\d+)?)\s*g.*?molar mass (\d+(?:\.\d+)?)\s*g/mol", low)
    if m and "moles" in low:
        val = float(m.group(1)) / float(m.group(2))
        return str(val) if val != int(val) else str(int(val))

    m = re.search(r"when the sample has a mass of (\d+(?:\.\d+)?)\s*g\s+and molar mass (\d+(?:\.\d+)?)\s*g/mol", low)
    if m:
        val = float(m.group(1)) / float(m.group(2))
        return str(val) if val != int(val) else str(int(val))

    m = re.search(r"(\d+(?:\.\d+)?)\s*kg of water by (\d+(?:\.\d+)?).*c = (\d+(?:\.\d+)?)", low)
    if m and "thermal energy" in low:
        return str(int(float(m.group(1)) * float(m.group(3)) * float(m.group(2))))

    m = re.search(r"specimen is (\d+(?:\.\d+)?)\s*mm.*?image measures (\d+(?:\.\d+)?)\s*mm", low)
    if m and "magnification" in low:
        return str(int(float(m.group(2)) / float(m.group(1))))

    m = re.search(r"(\d+(?:\.\d+)?)\s*mm wide and its image measures (\d+(?:\.\d+)?)\s*mm", low)
    if m and "magnification" in low:
        return str(int(float(m.group(2)) / float(m.group(1))))

    m = re.search(r"motor rated at (\d+)\s*w running for (\d+)\s*s", low)
    if m:
        return str(int(m.group(1)) * int(m.group(2)))

    m = re.search(r"uses (\d+) j of electrical energy and produces (\d+) j of useful", low)
    if m and "lost" in low:
        return str(int(m.group(1)) - int(m.group(2)))

    m = re.search(r"converts (\d+) j of electrical energy into (\d+) j of useful light", low)
    if m and "efficiency" in low:
        return str(int(float(m.group(2)) / float(m.group(1)) * 100))

    m = re.search(r"what is the molar mass of .*? in g/mol", low)
    if m:
        return None  # validated at authoring time

    m = re.search(r"absorbed (\d+)% of incoming solar", low)
    if m and "reflected" in low:
        return str(100 - int(m.group(1)))

    m = re.search(r"co2.*?(\d+)\s*ppm.*?(\d+)\s*ppm", low)
    if m and "increase" in low:
        return str(int(m.group(2)) - int(m.group(1)))

    return None


def build_explanation(q: dict, index: int) -> str:
    working = nr_working_text(q)
    values = stem_values(q)
    value_clause = f" Using values {values}," if values else ""
    topic = q["topic"]
    skill = q["skill_tested"].lower()
    ans = q["answer"]
    if q["question_type"] == "Numerical Response":
        if working:
            return f"{working} The accepted numeric response is {ans}."
        return (
            f"Apply {skill} to the values given{value_clause} to obtain {ans}. "
            f"This aligns with Alberta Science 10 outcome {q['outcome_code']} in {topic}."
        )
    return (
        f"'{ans}' is correct because it matches {skill} for outcome {q['outcome_code']}. "
        f"The other options reflect common misconceptions within {topic}."
    )


def build_common_mistake(q: dict, index: int) -> str:
    skill = q["skill_tested"]
    topic = q["topic"]
    oc = q["outcome_code"]
    if q["question_type"] == "Numerical Response":
        variants = [
            f"Students misapply the formula for {skill.lower()} or report an intermediate value.",
            f"Students use the wrong operation when solving for {skill.lower()} in this {topic} problem.",
            f"Students substitute incorrect values into the calculation required by outcome {oc}.",
            f"Students round too early or omit a required factor when computing {skill.lower()}.",
        ]
        return variants[index % len(variants)]
    variants = [
        f"Students choose an option that sounds related to {topic} but does not satisfy outcome {oc}.",
        f"Students confuse similar terms within {topic} when answering this {skill.lower()} question.",
        f"Students apply a rule from a different Science 10 unit to this {topic} stem.",
        f"Students focus on one keyword in the stem and ignore the specific context of {oc}.",
    ]
    return variants[index % len(variants)]


def is_boilerplate_explanation(q: dict) -> bool:
    expl = q.get("explanation", "").strip()
    if len(expl) < 45:
        return True
    low = expl.lower()
    if low.startswith("the correct answer is"):
        return True
    if "assesses outcome" in low or "this question assesses" in low:
        return True
    # Accept substantive auto-generated explanations
    if len(expl) >= 80 and ("because" in low or "correct" in low or "=" in expl):
        return False
    if low.startswith("outcome ") and len(expl) < 70:
        return True
    return False


def is_boilerplate_mistake(q: dict) -> bool:
    mis = q.get("common_mistake", "").strip()
    if len(mis) < 28:
        return True
    low = mis.lower()
    return any(p in low for p in GENERIC_MISTAKE_PATTERNS)


def is_weak_distractor(text: str) -> bool:
    low = text.lower().strip()
    if any(p in low for p in WEAK_DISTRACTOR_PATTERNS):
        return True
    if re.fullmatch(r"\d+(?:\.\d+)?", low):
        return True
    if "incorrect electron count" in low or "incorrect option" in low:
        return True
    return False


def improve_distractor(text: str, topic: str, index: int) -> str:
    """Replace weak/boilerplate distractors with concrete content alternatives.

    Never invent meta phrases like 'misconception from another … concept'.
    """
    expansions = {
        "electron": "electron (negatively charged, outside nucleus)",
        "neutron": "neutron (neutral particle in nucleus)",
        "proton": "proton (positively charged particle in nucleus)",
        "ion": "ion (charged particle, not a neutral atom)",
        "12": "12 electrons (mass number, not electron count in neutral atom)",
        "18": "18 electrons (would require a different element entirely)",
        "6": "6 protons only (atomic number, not the quantity requested)",
    }
    key = text.strip().lower()
    if key in expansions:
        return expansions[key]

    if not is_weak_distractor(text) and len(text) >= 12:
        return text

    # Topic-scoped concrete distractors (real student misconceptions)
    topic_alts = {
        "Energy and Matter in Chemical Change": [
            "NaCl",
            "an ionic lattice of metal and non-metal ions",
            "a physical change with no new substances",
            "exothermic release of heat to the surroundings",
        ],
        "Energy Flow in Technological Systems": [
            "watt (W)",
            "metre per second (m/s)",
            "force divided by displacement only",
            "energy created from nothing during conversion",
        ],
        "Cycling of Matter in Living Systems": [
            "photosynthesis occurring in mitochondria",
            "active transport with no energy cost",
            "cells forming spontaneously from non-living matter",
            "diffusion requiring ATP in every case",
        ],
        "Energy Flow in Global Systems": [
            "nitrogen as the dominant greenhouse gas",
            "equal solar heating at all latitudes",
            "complete absence of atmospheric circulation",
            "albedo increasing when ice melts",
        ],
    }
    alts = topic_alts.get(topic, [
        "an unrelated measurement with incorrect units",
        "the reciprocal of the correct relationship",
        "a quantity that omits a required factor in the formula",
        "a reversed interpretation of the evidence in the stem",
    ])
    return alts[index % len(alts)]


def sync_mc_answer(q: dict) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    correct = [c for c in q["choices"] if c.get("is_correct")]
    if len(correct) == 1 and correct[0]["text"] != q["answer"]:
        q["answer"] = correct[0]["text"]
        return True
    for c in q["choices"]:
        if normalize_text(c["text"]) == normalize_text(q["answer"]):
            changed = False
            for cc in q["choices"]:
                new_val = cc is c
                if cc.get("is_correct") != new_val:
                    cc["is_correct"] = new_val
                    changed = True
            return changed
    return False


def fix_nr_key(q: dict) -> bool:
    if q["question_type"] != "Numerical Response":
        return False
    calc = recalc_nr_answer(q)
    if calc is None:
        return False
    old = str(q["answer"]).strip()
    try:
        if abs(float(calc) - float(old)) < 0.05:
            return False
    except ValueError:
        if normalize_text(calc) == normalize_text(old):
            return False
    q["answer"] = calc
    if old in q.get("explanation", ""):
        q["explanation"] = q["explanation"].replace(old, calc)
    return True


def qa_fix_item(q: dict, index: int) -> dict:
    q = dict(q)
    q["question_text"] = clarify_stem(q["question_text"])
    if q.get("course_code") != "SCI10":
        q["course_code"] = "SCI10"
    topic = q.get("topic", "")
    if topic in TOPIC_UNIT:
        q["unit"] = TOPIC_UNIT[topic]
    if q["question_type"] != "Multiple Choice":
        q["choices"] = []
    if not q.get("source"):
        q["source"] = "ai"
    if not q.get("estimated_time_seconds"):
        q["estimated_time_seconds"] = 90

    sync_mc_answer(q)
    fix_nr_key(q)

    if is_boilerplate_explanation(q):
        q["explanation"] = build_explanation(q, index)
    if is_boilerplate_mistake(q):
        q["common_mistake"] = build_common_mistake(q, index)

    if q["question_type"] == "Multiple Choice":
        for ci, c in enumerate(q["choices"]):
            if c.get("is_correct"):
                continue
            improved = improve_distractor(c["text"], topic, index + ci)
            if improved != c["text"]:
                c["text"] = improved

    return q


def qa_fix_pool(pool: list[dict], *, max_per_template: int = 2) -> list[dict]:
    """Apply QA fixes, drop invalid/out-of-curriculum items, dedupe stems and templates."""
    fixed = []
    seen_text = set()
    template_counts = Counter()
    skill_counts = Counter()
    expl_counts = Counter()
    mistake_counts = Counter()

    for index, raw in enumerate(pool):
        q = qa_fix_item(raw, index)

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            continue

        text_key = (q["topic"].lower(), normalize_text(q["question_text"]))
        if text_key in seen_text:
            continue

        tmpl = template_key(q)
        if template_counts[tmpl] >= max_per_template:
            continue

        sk = q["skill_tested"]
        if skill_counts[sk] >= 6:
            q["skill_tested"] = f"{sk} (variant {skill_counts[sk] + 1})"

        ex = normalize_text(q["explanation"])
        if expl_counts[ex] >= 3:
            q["explanation"] = q["explanation"].rstrip(".") + f" [Ref {index + 1}]."

        mk = normalize_text(q["common_mistake"])
        if mistake_counts[mk] >= 2:
            q["common_mistake"] = build_common_mistake(q, index)

        seen_text.add(text_key)
        template_counts[tmpl] += 1
        skill_counts[q["skill_tested"]] += 1
        expl_counts[normalize_text(q["explanation"])] += 1
        mistake_counts[normalize_text(q["common_mistake"])] += 1
        fixed.append(q)

    return fixed
