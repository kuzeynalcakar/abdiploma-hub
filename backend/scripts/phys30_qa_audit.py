"""Full production QA audit for Physics 30 question pool."""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question
from phys30_questions.helpers import VALID_OUTCOMES

POOL = Path(__file__).parent.parent.parent / "questions.json" / "physics30_questions_pool.json"

WEAK_DISTRACTOR_PATTERNS = [
    "none of these",
    "none applies",
    "none of the above",
    "the opposite is always true",
    "none of these describes",
    "none of these is correct",
    "incorrect choice for this context",
]

CROSS_SUBJECT_TERMS = [
    "mitosis", "meiosis", "allele", "genotype", "dna replication",
    "oxidation number", "enthalpy", "molar enthalpy", "alkane", "ketone",
    "redox titration", "ph scale", "poh", "faraday's constant",
    "hess's law", "equilibrium constant", "photosynthesis",
]

K_COULOMB = 8.99e9
C_LIGHT = 3.0e8


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def verify_nr_answer(q: dict) -> list[str]:
    issues = []
    text = q["question_text"]
    ans = str(q["answer"]).strip()

    # p = mv
    m = re.search(
        r"mass \$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$ moves at \$(\d+(?:\.\d+)?)\\ \\text\{m/s\}",
        text,
    )
    if m and "momentum" in text.lower():
        calc = round(float(m.group(1)) * float(m.group(2)), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"momentum: expected {calc}, got {ans}")
        except ValueError:
            issues.append(f"non-numeric answer: {ans}")

    # v = p/m
    m = re.search(
        r"mass \$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$ has momentum \$(\d+(?:\.\d+)?)",
        text,
    )
    if m and "speed" in text.lower():
        calc = round(float(m.group(2)) / float(m.group(1)), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"speed from p: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Impulse F*dt
    m = re.search(r"force of \$(\d+(?:\.\d+)?)\\ \\text\{N\}\$ acts.*?for \$(\d+(?:\.\d+)?)\\ \\text\{s\}", text)
    if m and "impulse" in text.lower():
        calc = round(float(m.group(1)) * float(m.group(2)), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"impulse: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Inelastic vf
    m = re.search(
        r"Cart A \(\$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$\) moves at \$(\d+(?:\.\d+)?).*?"
        r"Cart B \(\$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$\)",
        text,
    )
    if m and "stick together" in text.lower():
        m1, v1, m2 = float(m.group(1)), float(m.group(2)), float(m.group(3))
        calc = round(m1 * v1 / (m1 + m2), 2)
        try:
            if abs(calc - float(ans)) > 0.2:
                issues.append(f"inelastic vf: expected {calc}, got {ans}")
        except ValueError:
            pass

    # KE = 0.5*m*v^2
    m = re.search(
        r"\$(\d+(?:\.\d+)?)\\ \\text\{kg\}\$ object moves at \$(\d+(?:\.\d+)?)\\ \\text\{m/s\}",
        text,
    )
    if m and "kinetic energy" in text.lower():
        calc = round(0.5 * float(m.group(1)) * float(m.group(2)) ** 2, 1)
        try:
            if abs(calc - float(ans)) > 0.2:
                issues.append(f"KE: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Coulomb F = kq1q2/r^2 (microcoulombs, cm)
    m = re.search(
        r"\+\$(\d+(?:\.\d+)?)\\ \\mu\\text\{C\}\$ and \$-(\d+(?:\.\d+)?)\\ \\mu\\text\{C\}\$ are "
        r"\$(\d+)\\ \\text\{cm\}",
        text,
    )
    if m and "electric force" in text.lower():
        q1, q2, r_cm = float(m.group(1)), float(m.group(2)), float(m.group(3))
        r_m = r_cm / 100
        calc = round(K_COULOMB * q1 * 1e-6 * q2 * 1e-6 / r_m ** 2, 1)
        try:
            if abs(calc - float(ans)) > 0.5:
                issues.append(f"Coulomb: expected {calc}, got {ans}")
        except ValueError:
            pass

    # E = kQ/r^2
    m = re.search(
        r"charge of \+\$(\d+(?:\.\d+)?)\\ \\mu\\text\{C\}\$.*?at \$(\d+)\\ \\text\{cm\}",
        text,
    )
    if m and "field strength" in text.lower():
        q, r_cm = float(m.group(1)), float(m.group(2))
        r_m = r_cm / 100
        calc = round(K_COULOMB * q * 1e-6 / r_m ** 2)
        try:
            if abs(calc - int(round(float(ans)))) > 2:
                issues.append(f"E-field: expected {calc}, got {ans}")
        except ValueError:
            pass

    # deltaV = Ed
    m = re.search(
        r"electric field of \$(\d+(?:\.\d+)?)\\ \\text\{N/C\}\$.*?separated by \$(\d+(?:\.\d+)?)\\ \\text\{cm\}",
        text,
    )
    if m and "potential difference" in text.lower():
        e_f, d_cm = float(m.group(1)), float(m.group(2))
        calc = round(e_f * d_cm / 100, 1)
        try:
            if abs(calc - float(ans)) > 0.2:
                issues.append(f"deltaV: expected {calc}, got {ans}")
        except ValueError:
            pass

    # F = Bqv
    m = re.search(
        r"charge \+\$(\d+(?:\.\d+)?)\\ \\mu\\text\{C\}\$ moves at \$(\d+(?:\.\d+)?) \\times 10\^5.*?"
        r"\$(\d+(?:\.\d+)?)\\ \\text\{T\}",
        text,
    )
    if m and "magnetic force" in text.lower():
        q, v, b = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e5, float(m.group(3))
        calc = round(b * q * v, 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"Bqv: expected {calc}, got {ans}")
        except ValueError:
            pass

    # v = E/B
    m = re.search(
        r"electric field strength is \$(\d+(?:\.\d+)?)\\ \\text\{N/C\}\$ and.*?magnetic field strength is \$(\d+(?:\.\d+)?)\\ \\text\{T\}",
        text,
    )
    if m and "undeflected" in text.lower():
        calc = round(float(m.group(1)) / float(m.group(2)))
        try:
            if abs(calc - float(ans)) > 1:
                issues.append(f"v=E/B: expected {calc}, got {ans}")
        except ValueError:
            pass

    # I = q/t
    m = re.search(
        r"charge of \$(\d+(?:\.\d+)?)\\ \\text\{C\}\$ passes.*?in \$(\d+(?:\.\d+)?)\\ \\text\{s\}",
        text,
    )
    if m and "current" in text.lower():
        calc = round(float(m.group(1)) / float(m.group(2)), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"current: expected {calc}, got {ans}")
        except ValueError:
            pass

    # F = BIL
    m = re.search(
        r"length \$(\d+(?:\.\d+)?)\\ \\text\{m\}\$ carries current \$(\d+(?:\.\d+)?)\\ \\text\{A\}\$ perpendicular to a \$(\d+(?:\.\d+)?)\\ \\text\{T\}",
        text,
    )
    if m and "force" in text.lower():
        l_m, i_a, b_t = float(m.group(1)), float(m.group(2)), float(m.group(3))
        calc = round(b_t * i_a * l_m, 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"BIL: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Photon E = 1240/lambda nm (not photoelectric Kmax)
    m = re.search(r"wavelength \$(\d+)\\ \\text\{nm\}", text)
    if m and ("photon" in text.lower() or "energy difference" in text.lower()) and "1240" in text:
        if "work function" not in text.lower():
            wl = int(m.group(1))
            calc = round(1240 / wl, 2)
            try:
                if abs(calc - float(ans)) > 0.05:
                    issues.append(f"photon E: expected {calc}, got {ans}")
            except ValueError:
                pass

    # Photoelectric Kmax
    m = re.search(
        r"wavelength \$(\d+)\\ \\text\{nm\}\$.*?work function \$(\d+(?:\.\d+)?)\\ \\text\{eV\}",
        text,
    )
    if m and "kinetic energy" in text.lower():
        wl, phi = int(m.group(1)), float(m.group(2))
        calc = round(1240 / wl - phi, 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"Kmax: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Frequency f = c/lambda
    m = re.search(r"wavelength \$(\d+)\\ \\text\{nm\}", text)
    if m and "frequency" in text.lower() and "1240" not in text:
        wl = int(m.group(1))
        calc = round(C_LIGHT / (wl * 1e-9) / 1e14, 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"frequency: expected {calc}, got {ans}")
        except ValueError:
            pass

    # n = c/v
    m = re.search(r"speed in a medium is \$(\d+(?:\.\d+)?) \\times 10\^8", text)
    if m and "refractive index" in text.lower():
        v = float(m.group(1)) * 1e8
        calc = round(C_LIGHT / v, 2)
        try:
            if abs(calc - float(ans)) > 0.05:
                issues.append(f"n=c/v: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Double slit lambda = x*d/(n*l) - complex, skip if pattern unclear

    # Half-life fraction
    m = re.search(r"After \$(\d+)\$ half-lives", text)
    if m and ("fraction" in text.lower() or "percentage" in text.lower() or "activity" in text.lower()):
        n = int(m.group(1))
        frac = (0.5) ** n
        if "percentage" in text.lower():
            calc = round(frac * 100, 2)
        elif "decimal" in text.lower():
            calc = round(frac, 4)
        else:
            calc = frac
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"half-life: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Mass defect MeV
    m = re.search(r"mass defect \\Delta m = (\d+(?:\.\d+)?)\\ \\text\{u\}", text)
    if m and "mev" in text.lower():
        dm = float(m.group(1))
        calc = round(dm * 931.5, 2)
        try:
            if abs(calc - float(ans)) > 0.1:
                issues.append(f"mass defect: expected {calc}, got {ans}")
        except ValueError:
            pass

    return issues


def audit_pool(pool: list) -> dict:
    report = {
        "schema_errors": [],
        "mc_key_errors": [],
        "mc_duplicate_choices": [],
        "nr_numeric_errors": [],
        "nr_calc_errors": [],
        "duplicate_stems": [],
        "duplicate_templates": [],
        "invalid_outcomes": [],
        "weak_distractors": [],
        "implausible_distractors": [],
        "boilerplate_explanations": [],
        "repeated_common_mistakes": [],
        "repeated_skills": [],
        "repeated_explanations": [],
        "ambiguous_wording": [],
        "curriculum_flags": [],
        "grading_ambiguity": [],
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
                report["mc_key_errors"].append({"index": i, "answer": q["answer"][:60]})

            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                report["mc_duplicate_choices"].append({"index": i})

            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                t = c["text"].lower().strip()
                if any(p in t for p in WEAK_DISTRACTOR_PATTERNS):
                    report["weak_distractors"].append({"index": i, "distractor": c["text"][:60]})
                if len(c["text"].strip()) < 10:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"], "reason": "too short"})
                if t in ("true", "false", "yes", "no", "always", "never"):
                    report["implausible_distractors"].append({"index": i, "distractor": c["text"]})

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip())
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            if "record" not in q["question_text"].lower() and "express" not in q["question_text"].lower():
                report["grading_ambiguity"].append({"index": i, "reason": "no recording instruction"})

        if q["outcome_code"] not in VALID_OUTCOMES.get(q["topic"], set()):
            report["invalid_outcomes"].append({"index": i, "outcome": q["outcome_code"], "topic": q["topic"]})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)

        expl = q["explanation"]
        if expl.startswith("The correct answer is") or (len(expl) < 40):
            report["boilerplate_explanations"].append({"index": i})

        if q["question_type"] == "Multiple Choice":
            ans_norm = normalize(q["answer"])
            stem = normalize(q["question_text"])
            if len(ans_norm) > 20 and ans_norm in stem:
                report["ambiguous_wording"].append({"index": i, "reason": "full answer in stem"})

        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > 3:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs[:8]})

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [{"text": t[:80], "count": c} for t, c in cm.items() if c > 1]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [{"text": t[:80], "count": c} for t, c in sk.items() if c > 1]

    ex = Counter(q["explanation"] for q in pool)
    report["repeated_explanations"] = [{"text": t[:80], "count": c} for t, c in ex.items() if c > 1]

    return report


def count_blocking_issues(report: dict) -> int:
    blocking_keys = [
        "schema_errors", "mc_key_errors", "mc_duplicate_choices",
        "nr_numeric_errors", "nr_calc_errors", "duplicate_stems",
        "duplicate_templates", "invalid_outcomes", "weak_distractors",
        "implausible_distractors", "boilerplate_explanations",
        "ambiguous_wording", "curriculum_flags", "grading_ambiguity",
        "repeated_common_mistakes", "repeated_skills", "repeated_explanations",
    ]
    return sum(len(report.get(k, [])) for k in blocking_keys)


def summarize(report: dict) -> None:
    for k, v in report.items():
        if isinstance(v, list) and v:
            print(f"{k}: {len(v)}")
            for item in v[:12]:
                print(f"  {item}")


if __name__ == "__main__":
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    report = audit_pool(pool)
    print(f"Pool size: {len(pool)}")
    summarize(report)
    print(f"Total blocking issues: {count_blocking_issues(report)}")
    out = POOL.parent / "phys30_qa_report.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Report: {out}")
