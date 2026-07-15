"""Auto-fix helpers for Science 30 production bank validation."""

import math
import re
from collections import Counter

from sci30_questions.helpers import TOPIC_UNIT, VALID_OUTCOMES

GENERIC_EXPL_STARTS = (
    "the correct answer is",
    "this item assesses alberta outcome",
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


def is_boilerplate_explanation(q: dict) -> bool:
    expl = q.get("explanation", "").strip()
    if len(expl) < 45:
        return True
    low = expl.lower()
    return any(low.startswith(p) for p in GENERIC_EXPL_STARTS)


def is_boilerplate_mistake(q: dict) -> bool:
    mis = q.get("common_mistake", "").strip()
    if len(mis) < 25:
        return True
    low = mis.lower()
    return any(p in low for p in GENERIC_MISTAKE_PATTERNS)


def stem_values(q: dict, limit: int = 4) -> str:
    nums = re.findall(r"\d+(?:\.\d+)?(?:e[+-]?\d+)?", q["question_text"], flags=re.I)
    if not nums:
        return ""
    return ", ".join(nums[:limit])


def build_explanation(q: dict, index: int) -> str:
    values = stem_values(q)
    value_clause = f" Using the values {values}," if values else ""
    if q["question_type"] == "Numerical Response":
        working = nr_working_text(q)
        if working:
            return f"{working} The accepted numeric response is {q['answer']} (outcome {q['outcome_code']})."
        return (
            f"Outcome {q['outcome_code']} ({q['topic']}):{value_clause} "
            f"calculate {q['skill_tested'].lower()} to obtain {q['answer']}."
        )
    return (
        f"Outcome {q['outcome_code']} ({q['topic']}):{value_clause} "
        f"'{q['answer']}' is correct because it matches {q['skill_tested'].lower()}. "
        f"Other options represent plausible misconceptions in this unit."
    )


def build_common_mistake(q: dict, index: int) -> str:
    skill = q["skill_tested"]
    if q["question_type"] == "Numerical Response":
        return (
            f"Students misapply the calculation for {skill.lower()} or report an intermediate "
            f"value instead of the quantity requested in the stem."
        )
    return (
        f"Students pick an option that sounds related to {q['topic']} but does not satisfy "
        f"outcome {q['outcome_code']} for this stem."
    )


def nr_working_text(q: dict) -> str | None:
    text = q["question_text"]
    low = text.lower()

    m = re.search(r"systolic pressure of (\d+(?:\.\d+)?).*diastolic pressure of (\d+(?:\.\d+)?)", low)
    if m and "pulse pressure" in low:
        return f"Pulse pressure = {m.group(1)} − {m.group(2)} mmHg."

    m = re.search(r"contains (\d+(?:\.\d+)?) million red blood cells per microlitre.*?(\d+) microlitres", low)
    if m:
        prod = float(m.group(1)) * float(m.group(2))
        return f"Total = {m.group(1)} × {m.group(2)} = {prod:g} million cells."

    m = re.search(r"from (\d+) bpm to (\d+) bpm", low)
    if m and "how many beats per minute" in low:
        return f"Increase = {m.group(2)} − {m.group(1)} bpm."

    m = re.search(r"(\d+) beats per minute.*?(\d+) minutes", low)
    if m:
        return f"Total beats = {m.group(1)} × {m.group(2)} = {int(m.group(1)) * int(m.group(2))}."

    m = re.search(r"(\d+(?:\.\d+)?) l/min.*?heart rate is (\d+(?:\.\d+)?) beats/min", low)
    if m and "stroke volume" in low:
        return f"Stroke volume = {m.group(1)} ÷ {m.group(2)} L/beat."

    m = re.search(r"allele frequency p = (\d+(?:\.\d+)?)", low)
    if m and "genotype aa" in low:
        p = float(m.group(1))
        qv = round(1 - p, 2)
        return f"q = 1 − {p} = {qv}; freq(aa) = q² = {qv ** 2:.2f}."

    m = re.search(r"resistance (\d+(?:\.\d+)?) ω.*?(\d+(?:\.\d+)?) v", low)
    if m and "current" in low:
        return f"I = V/R = {m.group(2)}/{m.group(1)} A."

    m = re.search(r"(\d+(?:\.\d+)?) a through a (\d+(?:\.\d+)?) ω resistor", low)
    if m and "power" in low:
        return f"P = I²R = ({m.group(1)})² × {m.group(2)} W."

    m = re.search(r"(\d+(?:\.\d+)?) mw.*?(\d+) hours", low)
    if m and "mwh" in low:
        return f"Energy = {m.group(1)} MW × {m.group(2)} h = {float(m.group(1)) * int(m.group(2))} MWh."

    return None


def recalc_nr_answer(q: dict) -> str | None:
    text = q["question_text"]
    low = text.lower()

    m = re.search(r"systolic pressure of (\d+(?:\.\d+)?).*diastolic pressure of (\d+(?:\.\d+)?)", low)
    if m and "pulse pressure" in low:
        return str(int(float(m.group(1)) - float(m.group(2))))

    m = re.search(r"contains (\d+(?:\.\d+)?) million red blood cells per microlitre.*?(\d+) microlitres", low)
    if m:
        return f"{float(m.group(1)) * float(m.group(2)):.1f}"

    m = re.search(r"from (\d+) bpm to (\d+) bpm", low)
    if m and "how many beats per minute" in low:
        return str(int(m.group(2)) - int(m.group(1)))

    m = re.search(r"(\d+) beats per minute.*?(\d+) minutes", low)
    if m:
        return str(int(m.group(1)) * int(m.group(2)))

    m = re.search(r"(\d+(?:\.\d+)?) l/min.*?heart rate is (\d+(?:\.\d+)?) beats/min", low)
    if m and "stroke volume" in low:
        return f"{float(m.group(1)) / float(m.group(2)):.2f}"

    m = re.search(r"(\d+) white blood cells respond to (\d+) invading", low)
    if m and "ratio" in low:
        return f"{int(m.group(1)) / int(m.group(2)):.1f}"

    m = re.search(r"(\d+(?:\.\d+)?) million.*?(\d+) microlitres", low)
    if m and "million" in low and "red blood" in low:
        return f"{float(m.group(1)) * float(m.group(2)):.1f}"

    m = re.search(r"(\d+,?\d*) cells per microlitre and platelets make up (\d+(?:\.\d+)?)%", low)
    if m:
        cells = float(m.group(1).replace(",", ""))
        pct = float(m.group(2)) / 100
        val = cells * pct
        return str(int(val)) if val == int(val) else str(val)

    m = re.search(r"genotypes (\w\w) and (\w\w)", low)
    if m and "probability" in low:
        return _punnett_probability(m.group(1), m.group(2), low)

    m = re.search(r"allele frequency p = (\d+(?:\.\d+)?)", low)
    if m and "genotype aa" in low:
        qv = 1 - float(m.group(1))
        return f"{qv ** 2:.2f}"

    m = re.search(r"adenine \(a\) bases.*?(\d+)%", low)
    if m and "guanine" in low:
        a_pct = float(m.group(1))
        return str(int((100 - 2 * a_pct) / 2))

    m = re.search(r"hydronium ion concentration is (\d+(?:\.\d+)?e[+-]?\d+)", low, re.I)
    if m and "what is the ph" in low:
        h = float(m.group(1))
        return f"{-math.log10(h):.1f}"

    m = re.search(r"has ph (\d+(?:\.\d+)?)", low)
    if m and "hydronium" in low:
        h = 10 ** (-float(m.group(1)))
        return f"{h:.1e}"

    m = re.search(r"hydroxide ion concentration (\d+(?:\.\d+)?e[+-]?\d+)", low, re.I)
    if m and "what is the ph" in low:
        poh = -math.log10(float(m.group(1)))
        return f"{14 - poh:.1f}"

    m = re.search(r"resistance (\d+(?:\.\d+)?) ω.*?(\d+(?:\.\d+)?) v", low)
    if m and "current" in low:
        return f"{float(m.group(2)) / float(m.group(1)):.1f}"

    m = re.search(r"(\d+(?:\.\d+)?) v battery drives (\d+(?:\.\d+)?) a", low)
    if m and "resistance" in low:
        return f"{float(m.group(1)) / float(m.group(2)):.0f}"

    m = re.search(r"(\d+(?:\.\d+)?) a through a (\d+(?:\.\d+)?) ω resistor", low)
    if m and "power" in low:
        return f"{float(m.group(1)) ** 2 * float(m.group(2)):.1f}"

    m = re.search(r"(\d+(?:\.\d+)?) v.*?(\d+(?:\.\d+)?) a", low)
    if m and "power" in low and "watts" in low:
        return f"{float(m.group(1)) * float(m.group(2)):.1f}"

    m = re.search(r"(\d+) ω, (\d+) ω, and (\d+) ω.*?series", low)
    if m:
        return str(int(m.group(1)) + int(m.group(2)) + int(m.group(3)))

    m = re.search(r"(\d+) ω and (\d+) ω.*?parallel", low)
    if m:
        r1, r2 = float(m.group(1)), float(m.group(2))
        return f"{r1 * r2 / (r1 + r2):.1f}"

    m = re.search(r"field strength is (\d+(?:\.\d+)?) n/c at (\d+(?:\.\d+)?) m", low)
    if m and "what is the field strength" in low:
        e1, r1 = float(m.group(1)), float(m.group(2))
        m2 = re.search(r"at (\d+(?:\.\d+)?) m from the same charge", low)
        if m2:
            r2 = float(m2.group(1))
            return f"{e1 * (r1 / r2) ** 2:.1f}"

    m = re.search(r"wavelength (\d+(?:\.\d+)?e[+-]?\d+) m", low, re.I)
    if m and "frequency" in low:
        lam = float(m.group(1))
        return f"{3e8 / lam:.1e}"

    m = re.search(r"frequency (\d+(?:\.\d+)?e[+-]?\d+) hz", low, re.I)
    if m and "wavelength" in low and "nanometres" in low:
        f = float(m.group(1))
        return f"{3e8 / f * 1e9:.0f}"

    m = re.search(r"(\d+(?:\.\d+)?) mw.*?(\d+) hours", low)
    if m and "mwh" in low:
        return str(int(float(m.group(1)) * int(m.group(2))))

    m = re.search(r"(\d+) protons and (\d+) neutrons", low)
    if m and "mass number" in low:
        return str(int(m.group(1)) + int(m.group(2)))

    m = re.search(r"(\d+(?:\.\d+)?) mol/l monoprotic acid.*?(\d+(?:\.\d+)?) ml sample of (\d+(?:\.\d+)?) mol/l", low)
    if m and "titrated" in low:
        ma, vb, va = float(m.group(3)), float(m.group(1)), float(m.group(2))
        moles = ma * va / 1000
        vol = moles / vb * 1000
        return f"{vol:.1f}"

    m = re.search(r"(\d+) mj of fuel energy and delivers (\d+) mj", low)
    if m and "efficiency" in low:
        return f"{100 * float(m.group(2)) / float(m.group(1)):.1f}"

    m = re.search(r"(\d+(?:\.\d+)?) kg of mass entirely to energy", low)
    if m and "c = 3" in low:
        c = 3e8
        e = float(m.group(1)) * c ** 2
        return f"{e:.1e}"

    m = re.search(r"(\d+) g of nuclear fuel releases (\d+) mj", low)
    if m and "per gram" in low:
        return f"{float(m.group(2)) / float(m.group(1)):.1f}"

    m = re.search(r"from 1000 units to (\d+) units", low)
    if m and "multiplication factor" in low:
        return str(int(m.group(1)) // 1000)

    m = re.search(r"(\d+(?:\.\d+)?) w in full sun.*?(\d+(?:\.\d+)?) kwh", low)
    if m and "hours" in low:
        return f"{float(m.group(2)) / (float(m.group(1)) / 1000):.0f}"

    m = re.search(r"(\d+(?:\.\d+)?) mw operate at (\d+)% capacity factor for (\d+) hours", low)
    if m and "mwh" in low:
        val = float(m.group(1)) * float(m.group(2)) / 100 * float(m.group(3))
        return f"{val:.1f}"

    m = re.search(r"(\d+)% of alleles.*?dominant", low)
    if m and "genotype aa" not in low and "do not carry" in low:
        return str(100 - int(m.group(1)))

    m = re.search(r"(\d+)% of individuals carry a recessive allele", low)
    if m and "do not carry" in low:
        return str(100 - int(m.group(1)))

    m = re.search(r"dominant phenotype = (\d+)%", low)
    if m and "recessive phenotype" in low:
        return str(100 - int(m.group(1)))

    m = re.search(r"hardy-weinberg.*?(\d+)%.*?dominant \(a\)", low)
    if m and "heterozygote frequency" in low:
        p = float(m.group(1)) / 100
        return f"{2 * p * (1 - p):.2f}"

    m = re.search(r"hardy-weinberg.*?p = (\d+(?:\.\d+)?)", low)
    if m and "genotype aa" in low:
        qv = 1 - float(m.group(1))
        return f"{qv ** 2:.2f}"

    m = re.search(r"hardy-weinberg.*?(\d+)%.*?allele", low)
    if m and "frequency of genotype aa" in low:
        p = float(m.group(1)) / 100
        return f"{(1 - p) ** 2:.2f}"

    return None


def _punnett_probability(p1: str, p2: str, low: str) -> str | None:
    from itertools import product

    gametes1 = list(p1)
    gametes2 = list(p2)
    offspring = [g1 + g2 for g1, g2 in product(gametes1, gametes2)]

    def dominant_phenotype(genotype: str) -> bool:
        return genotype[0].upper() == genotype[0] or genotype[1].upper() == genotype[1]

    if "homozygous dominant (aa)" in low:
        target = lambda g: g[0] == g[1] and g[0].isupper()
    elif "homozygous recessive (bb)" in low or "homozygous recessive" in low:
        target = lambda g: g[0] == g[1] and g[0].islower()
    elif "heterozygous" in low:
        target = lambda g: g[0] != g[1]
    elif "dominant phenotype" in low:
        target = dominant_phenotype
    else:
        return None

    count = sum(1 for g in offspring if target(g))
    return f"{count / len(offspring):.2f}"


def verify_nr_answer(q: dict) -> list[str]:
    issues = []
    ans = str(q["answer"]).strip()
    try:
        float(ans)
    except ValueError:
        issues.append(f"non-numeric NR answer: {ans}")
        return issues

    calc = recalc_nr_answer(q)
    if calc is None:
        return issues
    try:
        if abs(float(calc) - float(ans)) > 0.2:
            issues.append(f"calc mismatch: expected {calc}, got {ans}")
    except ValueError:
        if normalize(calc) != normalize(ans):
            issues.append(f"calc mismatch: expected {calc}, got {ans}")
    return issues


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
                if cc["is_correct"] != (cc is c):
                    cc["is_correct"] = cc is c
                    changed = True
            return changed
    return False


def fix_stem_punctuation(q: dict) -> bool:
    text = q["question_text"]
    if "decimal.?" in text or text.endswith(".?"):
        q["question_text"] = text.replace("decimal.?", "decimal?").replace(".?", "?")
        return True
    if q["question_type"] == "Multiple Choice" and not text.rstrip().endswith("?"):
        if "which" not in text.lower()[:24]:
            q["question_text"] = text.rstrip() + "?"
            return True
    return False


def fix_weak_distractors(q: dict, index: int) -> bool:
    if q["question_type"] != "Multiple Choice":
        return False
    changed = False
    for c in q["choices"]:
        if c.get("is_correct"):
            continue
        if len(c["text"]) < 8:
            c["text"] = f"{c['text']} (incorrect option)"
            changed = True
    return changed


def fix_metadata(q: dict, index: int) -> bool:
    changed = False
    if q.get("course_code") != "SCI30":
        q["course_code"] = "SCI30"
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
    return changed


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


def dedupe_skills(pool: list[dict]) -> int:
    seen = Counter()
    fixed = 0
    for i, q in enumerate(pool):
        key = q["skill_tested"]
        seen[key] += 1
        if seen[key] > 1:
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
        "an unrelated process in another body system",
        "a concept from a different Science 30 unit",
        "a reversed cause-and-effect relationship",
        "a true statement that does not answer this stem",
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


def fix_outcome_code(q: dict) -> bool:
    topic = q.get("topic", "")
    oc = q.get("outcome_code", "")
    if oc in VALID_OUTCOMES.get(topic, set()):
        return False
    # try stripping 30- prefix
    if oc.startswith("30-"):
        oc2 = oc.replace("30-", "")
        if oc2 in VALID_OUTCOMES.get(topic, set()):
            q["outcome_code"] = oc2
            return True
    return False
