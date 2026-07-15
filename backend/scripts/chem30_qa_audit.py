"""Full production QA audit for Chemistry 30 question pool."""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from chem30_questions.helpers import VALID_OUTCOMES

POOL = Path(__file__).parent.parent.parent / "questions.json" / "chemistry30_questions_pool.json"

WEAK_DISTRACTOR_PATTERNS = [
    "none of these",
    "none applies",
    "none of the above",
    "the opposite is always true",
    "none of these describes",
    "none of these is correct",
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

GENERIC_MISTAKE_PATTERNS = [
    "students forget to multiply all three factors",
    "students report total energy instead of per-mole",
    "students subtract instead of add step enthalpies",
    "students invert useful and total energy",
    "students add potentials or subtract in wrong order",
    "students forget faraday constant",
    "students use concentration directly as ph",
    "students confuse poh with",
]


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def verify_nr_answer(q: dict, index: int) -> list[str]:
    issues = []
    text = q["question_text"]
    ans = str(q["answer"]).strip()

    # Q = mcΔT joules
    m = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{g\}\$.*?(?:absorbs|of water|sample).*?"
        r"(?:specific heat|using \$c = )(\d+(?:\.\d+)?).*?"
        r"(?:rises? by|changes temperature by|temperature rise of|heated by) \$?(\d+(?:\.\d+)?)",
        text,
        re.I | re.S,
    )
    if m and "calculate heat" in text.lower() or (m and "calculate $q$" in text.lower()):
        mass, c, dt = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if "kj" in text.lower():
            calc = round(mass * c * dt / 1000, 2)
            try:
                if abs(calc - float(ans)) > 0.05:
                    issues.append(f"NR calc Q kJ: expected {calc}, got {ans}")
            except ValueError:
                issues.append(f"NR answer not numeric: {ans}")
        elif "joules" in text.lower() or "record as a whole number" in text.lower():
            calc = round(mass * c * dt)
            try:
                if abs(calc - float(ans)) > 1:
                    issues.append(f"NR calc Q J: expected {calc}, got {ans}")
            except ValueError:
                issues.append(f"NR answer not numeric: {ans}")

    # Simpler Q=mcΔT with explicit values
    m2 = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{g\}\$ of water.*?\$(\d+(?:\.\d+)?)\\ \\text\{J\}\$.*?c = (\d+(?:\.\d+)?)",
        text,
        re.S,
    )
    if m2 and "temperature change" in text.lower():
        mass, qj, c = float(m2.group(1)), float(m2.group(2)), float(m2.group(3))
        calc = round(qj / (mass * c), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"NR calc deltaT: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Molar enthalpy
    m3 = re.search(r"\$(\d+(?:\.\d+)?)\\ \\text\{mol\}\$.*?releases \$(\d+(?:\.\d+)?)\\ \\text\{kJ\}\$", text)
    if m3 and "molar enthalpy" in text.lower():
        mol, energy = float(m3.group(1)), float(m3.group(2))
        calc = round(energy / mol)
        try:
            if int(float(ans)) != calc:
                issues.append(f"NR molar enthalpy: expected {calc}, got {ans}")
        except ValueError:
            issues.append(f"NR answer not numeric: {ans}")

    # Hess's law
    m4 = re.search(r"\\Delta H_1 = ([+-]?\d+).*\\Delta H_2 = ([+-]?\d+)", text)
    if m4 and "net" in text.lower():
        net = int(m4.group(1)) + int(m4.group(2))
        if str(net) != ans:
            issues.append(f"NR Hess: expected {net}, got {ans}")

    # Efficiency
    m5 = re.search(r"delivers \$(\d+(?:\.\d+)?).*?from \$(\d+(?:\.\d+)?)", text)
    if m5 and "efficiency" in text.lower():
        u, t = float(m5.group(1)), float(m5.group(2))
        calc = round(u / t * 100)
        if str(calc) != ans:
            issues.append(f"NR efficiency: expected {calc}, got {ans}")

    # E°cell
    m6 = re.search(
        r"E°_\{cathode\} = ([+-]?\d+(?:\.\d+)?).*?E°_\{anode\} = ([+-]?\d+(?:\.\d+)?)",
        text,
    )
    if m6:
        cath, an = float(m6.group(1)), float(m6.group(2))
        calc = round(cath - an, 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"NR Ecell: expected {calc:.2f}, got {ans}")
        except ValueError:
            issues.append(f"NR answer not numeric: {ans}")

    # Faraday moles e-
    m7 = re.search(r"current of \$(\d+(?:\.\d+)?)\\ \\text\{A\}\$ flows for \$(\d+)\s*\\", text)
    if m7 and "moles of electrons" in text.lower():
        i_val, t_val = float(m7.group(1)), float(m7.group(2))
        calc = round(i_val * t_val / 96500, 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"NR moles e-: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # Redox titration mmol
    m8 = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{mL\}\$.*?concentration\s*\$(\d+(?:\.\d+)?)\\ \\text\{mol/L\}\$",
        text,
    )
    if m8 and "millimoles" in text.lower():
        vol, conc = float(m8.group(1)), float(m8.group(2))
        calc = round(vol * conc, 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"NR mmol: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # Kc A+B<->C
    m9 = re.search(
        r"\[\\text\{A\}\] = ([\d.]+).*?\[\\text\{B\}\] = ([\d.]+).*?\[\\text\{C\}\] = ([\d.]+)",
        text,
    )
    if m9 and "A}(g) + \\text{B}" in text:
        a, b, c = float(m9.group(1)), float(m9.group(2)), float(m9.group(3))
        calc = round(c / (a * b), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"NR Kc AB: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Kc 2A<->B
    m10 = re.search(
        r"\[\\text\{A\}\] = ([\d.]+).*?\[\\text\{B\}\] = ([\d.]+)",
        text,
    )
    if m10 and "2\\text{A}" in text:
        a, b = float(m10.group(1)), float(m10.group(2))
        calc = round(b / (a * a), 2)
        try:
            if abs(calc - float(ans)) > 0.02:
                issues.append(f"NR Kc 2A: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # pH from concentration
    m11 = re.search(r"\[\\text\{H\}_3\\text\{O\}\^\+\] = ([0-9.e+\-]+)", text)
    if m11 and "calculate the ph" in text.lower():
        conc = float(m11.group(1))
        calc = round(-math.log10(conc), 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"NR pH: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # pOH to pH
    m12 = re.search(r"pH = (\d+(?:\.\d+)?)", text)
    if m12 and "what is the poh" in text.lower():
        ph = float(m12.group(1))
        calc = round(14.0 - ph, 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"NR pOH: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # Percent ionization
    m13 = re.search(
        r"initial concentration \$(\d+(?:\.\d+)?).*?\[\\text\{H\}_3\\text\{O\}\^\+\] = (\d+(?:\.\d+)?)",
        text,
    )
    if m13 and "percent ionization" in text.lower():
        c0, h = float(m13.group(1)), float(m13.group(2))
        calc = round(h / c0 * 100)
        if str(calc) != ans:
            issues.append(f"NR % ion: expected {calc}, got {ans}")

    # Molar mass alkane
    m14 = re.search(r"C_\{(\d+)\}\$H_\{(\d+)\}\$", text)
    if m14 and "molar mass" in text.lower():
        c, h = int(m14.group(1)), int(m14.group(2))
        calc = c * 12 + h
        if str(calc) != ans:
            issues.append(f"NR molar mass: expected {calc}, got {ans}")

    # Alkane H count
    m15 = re.search(r"C_\$(\d+)\$H_\$(\d+)\$", text)
    if m15 and "how many hydrogen" in text.lower():
        h = int(m15.group(2))
        if str(h) != ans:
            issues.append(f"NR H count: expected {h}, got {ans}")

    # Ka/Kb mantissa
    m16 = re.search(r"K_a = ([0-9.e+\-]+)", text)
    if m16 and "mantissa" in text.lower():
        ka = float(m16.group(1))
        kb = 1e-14 / ka
        coeff = float(f"{kb:.1e}".split("e")[0])
        try:
            if abs(coeff - float(ans)) > 0.05:
                issues.append(f"NR Kb mantissa: expected {coeff:.1f}, got {ans}")
        except ValueError:
            pass

    # Oxidation number in formula prompts - skip auto verify (context dependent)

    return issues


def audit_pool(pool: list) -> dict:
    report = {
        "schema_errors": [],
        "mc_key_errors": [],
        "nr_numeric_errors": [],
        "nr_calc_errors": [],
        "duplicate_stems": [],
        "duplicate_templates": [],
        "invalid_outcomes": [],
        "weak_distractors": [],
        "boilerplate_explanations": [],
        "repeated_common_mistakes": [],
        "repeated_skills": [],
        "repeated_explanations": [],
        "ambiguous_wording": [],
        "curriculum_flags": [],
    }

    stems = defaultdict(list)
    templates = defaultdict(list)

    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            report["schema_errors"].append({"index": i, "reasons": reasons})

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["mc_key_errors"].append({"index": i, "answer": q["answer"]})

            for c in q["choices"]:
                if not c.get("is_correct"):
                    t = c["text"].lower()
                    if any(p in t for p in WEAK_DISTRACTOR_PATTERNS):
                        report["weak_distractors"].append({"index": i, "distractor": c["text"]})
                    if len(c["text"].strip()) < 5:
                        report["weak_distractors"].append({"index": i, "distractor": c["text"], "reason": "too short"})

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            calc_issues = verify_nr_answer(q, i)
            for issue in calc_issues:
                report["nr_calc_errors"].append({"index": i, "issue": issue})

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            report["invalid_outcomes"].append({"index": i, "outcome": q["outcome_code"], "topic": q["topic"]})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)

        expl = q["explanation"]
        if expl.startswith("The correct answer is") or (expl.endswith("is correct.") and len(expl) < 90):
            report["boilerplate_explanations"].append({"index": i, "explanation": expl[:80]})

        if q["common_mistake"].lower() in [p for p in GENERIC_MISTAKE_PATTERNS]:
            pass

        # Ambiguous: answer appears in question stem as obvious
        if q["question_type"] == "Multiple Choice" and q["answer"].lower() in normalize(q["question_text"]):
            if len(q["answer"]) > 15:
                report["ambiguous_wording"].append({"index": i, "reason": "answer text in stem"})

        # Curriculum: biology terms in chem pool
        bio_terms = ["mitosis", "meiosis", "dna", "neuron", "photosystem", "allele", "genotype"]
        combined = (q["question_text"] + q["explanation"]).lower()
        for term in bio_terms:
            if term in combined and term not in ("photosynthesis", "cellular respiration"):
                report["curriculum_flags"].append({"index": i, "term": term})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > 3:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs[:8]})

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [{"text": t, "count": c} for t, c in cm.items() if c > 1]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [{"text": t, "count": c} for t, c in sk.items() if c > 1]

    exp_full = Counter(q["explanation"] for q in pool)
    report["repeated_explanations"] = [{"text": t[:80], "count": c} for t, c in exp_full.items() if c > 1]

    return report


def summarize(report: dict) -> int:
    total = 0
    for k, v in report.items():
        if isinstance(v, list) and v:
            n = len(v)
            total += n
            print(f"{k}: {n}")
            if k in ("nr_calc_errors", "duplicate_stems", "mc_key_errors", "schema_errors",
                     "duplicate_templates", "weak_distractors", "boilerplate_explanations",
                     "repeated_common_mistakes", "repeated_skills", "repeated_explanations",
                     "invalid_outcomes", "ambiguous_wording"):
                for item in v[:15]:
                    print(f"  {item}")
    return total


if __name__ == "__main__":
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    report = audit_pool(pool)
    print(f"Pool size: {len(pool)}")
    total = summarize(report)
    print(f"Total issue entries: {total}")
    out = Path(__file__).parent.parent.parent / "questions.json" / "chem30_qa_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report: {out}")
