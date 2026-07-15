"""Full production QA audit for Mathematics 30-2 question pool."""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question, is_numerical_answer

POOL = Path(__file__).parent.parent.parent / "questions.json" / "math30-2_questions_pool.json"
REPORT = POOL.parent / "math30-2_qa_report.json"

TOPIC_OUTCOMES = {
    "Set Theory and Logic": {"LR1", "LR2"},
    "Counting Methods": {"P4", "P5", "P6"},
    "Probability": {"P1", "P2", "P3"},
    "Rational Expressions and Equations": {"RF1", "RF2", "RF3"},
    "Polynomial Functions": {"RF7"},
    "Exponential and Logarithmic Functions": {"RF4", "RF5", "RF6"},
    "Sinusoidal Functions": {"RF8"},
}

TOPIC_UNIT = {
    "Set Theory and Logic": "Logical Reasoning",
    "Counting Methods": "Probability",
    "Probability": "Probability",
    "Rational Expressions and Equations": "Relations and Functions",
    "Polynomial Functions": "Relations and Functions",
    "Exponential and Logarithmic Functions": "Relations and Functions",
    "Sinusoidal Functions": "Relations and Functions",
}

CROSS_SUBJECT_TERMS = [
    "mitosis", "meiosis", "allele", "dna", "photosynthesis", "molar enthalpy",
    "oxidation number", "faraday", "equilibrium constant", "newton's third law",
    "hardy-weinberg", "endocrine", "neuron", "cell division",
]

WEAK_DISTRACTOR_PATTERNS = [
    "none of these", "none of the above", "all of the above",
    "cannot be determined", "not enough information",
]

MAX_PER_TEMPLATE = 3
MAX_PER_SKILL = 2
MAX_PER_MISTAKE = 2
MAX_PER_EXPLANATION = 2


def normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def template_key(q: dict) -> str:
    text = normalize(q["question_text"])
    text = re.sub(r"\d+(?:\.\d+)?", "#", text)
    text = re.sub(r"[^a-z0-9|# ]", "", text)
    return f"{q['topic']}|{text}"


def _float(s: str) -> float:
    return float(str(s).strip().strip("$"))


def verify_nr_answer(q: dict) -> list[str]:
    issues = []
    text = q["question_text"]
    ans = str(q["answer"]).strip().strip("$")

    # Arithmetic sequence term
    m = re.search(
        r"sequence starts at \$(-?\d+(?:\.\d+)?)\$ and each term increases by \$(-?\d+(?:\.\d+)?)\$.*?"
        r"What is the \$(\d+)\$th term",
        text,
    )
    if m:
        start, step, n = float(m.group(1)), float(m.group(2)), int(m.group(3))
        calc = start + (n - 1) * step
        if str(int(calc)) != ans and abs(calc - float(ans)) > 0.01:
            issues.append(f"arithmetic term: expected {calc}, got {ans}")

    # Two-set neither / art only / union
    m = re.search(
        r"group of \$(\d+)\$ people, \$(\d+)\$ enjoy hiking, \$(\d+)\$ enjoy cycling, "
        r"and \$(\d+)\$ enjoy both.*?neither",
        text,
    )
    if m:
        u, a, b, ab = map(int, m.groups())
        calc = u - (a + b - ab)
        if str(calc) != ans:
            issues.append(f"two-set neither: expected {calc}, got {ans}")

    m = re.search(
        r"survey of \$(\d+)\$ students shows \$(\d+)\$ take art, \$(\d+)\$ take drama, "
        r"and \$(\d+)\$ take both.*?art only",
        text,
    )
    if m:
        _, a, _, ab = map(int, m.groups())
        calc = a - ab
        if str(calc) != ans:
            issues.append(f"art only: expected {calc}, got {ans}")

    m = re.search(
        r"\|U\| = (\d+), \|A\| = (\d+), \|B\| = (\d+), and \|A \\cap B\| = (\d+).*?\|A \\cup B\|",
        text,
    )
    if m:
        _, a, b, ab = map(int, m.groups())
        calc = a + b - ab
        if str(calc) != ans:
            issues.append(f"two-set union: expected {calc}, got {ans}")

    # Three-set inclusion-exclusion
    m = re.search(
        r"class of \$(\d+)\$ students: \$(\d+)\$ study French, \$(\d+)\$ study Spanish, "
        r"\$(\d+)\$ study German; \$(\d+)\$ study French and Spanish, \$(\d+)\$ French and German, "
        r"\$(\d+)\$ Spanish and German, and \$(\d+)\$ study all three.*?at least one",
        text,
    )
    if m:
        u, a, b, c, ab, ac, bc, abc = map(int, m.groups())
        union = a + b + c - ab - ac - bc + abc
        if str(union) != ans:
            issues.append(f"three-set union: expected {union}, got {ans}")

    m = re.search(
        r"same class of \$(\d+)\$ students with language counts "
        r"\(\$(\d+)\$ French, \$(\d+)\$ Spanish, \$(\d+)\$ German, overlaps \$(\d+)\$, "
        r"\$(\d+)\$, \$(\d+)\$, \$(\d+)\$\).*?none of the three",
        text,
    )
    if m:
        u, a, b, c, ab, ac, bc, abc = map(int, m.groups())
        union = a + b + c - ab - ac - bc + abc
        calc = u - union
        if str(calc) != ans:
            issues.append(f"three-set neither: expected {calc}, got {ans}")

    m = re.search(
        r"community centre, \$(\d+)\$ members.*? \$(\d+)\$ use the gym, \$(\d+)\$ use the pool, "
        r"and \$(\d+)\$ use both.*?neither",
        text,
    )
    if m:
        u, a, b, ab = map(int, m.groups())
        calc = u - (a + b - ab)
        if str(calc) != ans:
            issues.append(f"context neither: expected {calc}, got {ans}")

    # FCP two-stage
    m = re.search(r"offers \$(\d+)\$ .+ and \$(\d+)\$ .+?How many different .+ combinations", text)
    if m:
        calc = int(m.group(1)) * int(m.group(2))
        if str(calc) != ans:
            issues.append(f"fcp2: expected {calc}, got {ans}")

    m = re.search(
        r"\$(\d+)\$ departure cities, \$(\d+)\$ hotels, and \$(\d+)\$ activity passes",
        text,
    )
    if m:
        calc = int(m.group(1)) * int(m.group(2)) * int(m.group(3))
        if str(calc) != ans:
            issues.append(f"fcp3: expected {calc}, got {ans}")

    m = re.search(r"\$(\d+)\$ characters chosen from \$(\d+)\$ distinct symbols, with repetition", text)
    if m:
        length_m = re.search(r"uses \$(\d+)\$ characters", text)
        if length_m:
            calc = int(m.group(2)) ** int(length_m.group(1))
            if str(calc) != ans:
                issues.append(f"fcp code: expected {calc}, got {ans}")

    # n! arrangements
    m = re.search(r"arrange \$(\d+)\$ distinct books", text)
    if m:
        n = int(m.group(1))
        calc = math.factorial(n)
        if str(calc) != ans:
            issues.append(f"n!: expected {calc}, got {ans}")

    # nPr ranking
    m = re.search(r"rank the top \$(\d+)\$ finishers from \$(\d+)\$ contestants", text)
    if m:
        r, n = int(m.group(1)), int(m.group(2))
        calc = math.factorial(n) // math.factorial(n - r)
        if str(calc) != ans:
            issues.append(f"nPr: expected {calc}, got {ans}")

    # Letter arrangements
    m = re.search(r"arrangements of the letters in ([A-Z]+)", text)
    if m:
        word = m.group(1)
        counts = Counter(word)
        numer = math.factorial(len(word))
        denom = 1
        for c in counts.values():
            denom *= math.factorial(c)
        calc = numer // denom
        if str(calc) != ans:
            issues.append(f"letter perm: {word} expected {calc}, got {ans}")

    # Adjacency restriction
    m = re.search(r"\$(\d+)\$ students line up.*?next to each other", text)
    if m:
        n = int(m.group(1))
        calc = math.factorial(n - 1) * 2
        if str(calc) != ans:
            issues.append(f"adjacency: expected {calc}, got {ans}")

    # Blocked position
    m = re.search(
        r"\$(\d+)\$ people stand in a line, but one specific position \(position \$(\d+)\$",
        text,
    )
    if m:
        n = int(m.group(1))
        calc = math.factorial(n - 1)
        if str(calc) != ans:
            issues.append(f"blocked position: expected {calc}, got {ans}")

    # nCr team
    m = re.search(r"From \$(\d+)\$ candidates, how many ways can a team of \$(\d+)\$", text)
    if m:
        n, r = int(m.group(1)), int(m.group(2))
        calc = math.factorial(n) // (math.factorial(r) * math.factorial(n - r))
        if str(calc) != ans:
            issues.append(f"nCr: expected {calc}, got {ans}")

    # Multi-case combo council
    m = re.search(
        r"select \$(\d+)\$ members from \$(\d+)\$ candidates in Region A "
        r"and \$(\d+)\$ members from \$(\d+)\$ candidates in Region B",
        text,
    )
    if m:
        r1, n1, r2, n2 = map(int, m.groups())
        calc = (math.factorial(n1) // (math.factorial(r1) * math.factorial(n1 - r1))) * \
               (math.factorial(n2) // (math.factorial(r2) * math.factorial(n2 - r2)))
        if str(calc) != ans:
            issues.append(f"combo product: expected {calc}, got {ans}")

    # Handshakes
    m = re.search(r"\$(\d+)\$ people each shake hands once", text)
    if m:
        n = int(m.group(1))
        calc = n * (n - 1) // 2
        if str(calc) != ans:
            issues.append(f"handshakes: expected {calc}, got {ans}")

    # Odds to probability
    m = re.search(r"odds in favour of event \$E\$ are \$(\d+):(\d+)\$.*?What is \$P\(E\)\?", text)
    if m:
        fav, against = int(m.group(1)), int(m.group(2))
        calc = round(fav / (fav + against), 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"odds to P: expected {calc:.4f}, got {ans}")
        except ValueError:
            issues.append(f"non-numeric probability: {ans}")

    # Mutually exclusive union
    m = re.search(
        r"mutually exclusive with \$P\(A\)=([\d.]+)\$ and \$P\(B\)=([\d.]+)\$.*?P\(A \\cup B\)",
        text,
    )
    if m:
        calc = round(float(m.group(1)) + float(m.group(2)), 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"ME union: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Inclusion-exclusion probability
    m = re.search(
        r"\$P\(A\)=([\d.]+)\$, \$P\(B\)=([\d.]+)\$, \$P\(A \\cap B\)=([\d.]+)\$.*?P\(A \\cup B\)",
        text,
    )
    if m and "mutually exclusive" not in text:
        calc = round(float(m.group(1)) + float(m.group(2)) - float(m.group(3)), 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"overlap union: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Independent intersection
    m = re.search(
        r"independent with \$P\(X\)=([\d.]+)\$ and \$P\(Y\)=([\d.]+)\$.*?P\(X \\cap Y\)",
        text,
    )
    if m:
        calc = round(float(m.group(1)) * float(m.group(2)), 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"indep intersect: expected {calc:.4f}, got {ans}")
        except ValueError:
            pass

    # Dependent intersection
    m = re.search(
        r"\$P\(M\)=([\d.]+)\$ and \$P\(N\|M\)=([\d.]+)\$.*?P\(M \\cap N\)",
        text,
    )
    if m:
        calc = round(float(m.group(1)) * float(m.group(2)), 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"dep intersect: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Die probability
    m = re.search(r"fair six-sided die.*?probability of rolling a number (.+?)\?", text)
    if m:
        desc = m.group(1).lower()
        fav_map = {
            "even": 3, "greater than 4": 2, "less than 3": 2, "a 5": 1, "at least 4": 3,
        }
        if desc in fav_map:
            calc = round(fav_map[desc] / 6, 4)
            try:
                if abs(calc - float(ans)) > 0.0002:
                    issues.append(f"dice: expected {calc:.4f}, got {ans}")
            except ValueError:
                pass

    # Marble complement
    m = re.search(r"contains \$(\d+)\$ red marbles and \$(\d+)\$ blue marbles.*?not red", text)
    if m:
        red, blue = int(m.group(1)), int(m.group(2))
        calc = round(blue / (red + blue), 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"marble complement: expected {calc:.4f}, got {ans}")
        except ValueError:
            pass

    # Non-permissible linear
    m = re.search(r"non-permissible value of \$x\$ for \$\\dfrac\{(\d+)\}\{(-?\d+)x \+ (-?\d+)\}\$", text)
    if m:
        a, b = int(m.group(2)), int(m.group(3))
        if a != 0 and (-b) % a == 0:
            calc = -b // a
            if str(calc) != ans:
                issues.append(f"npv linear: expected {calc}, got {ans}")

    m = re.search(r"non-permissible value of \$x\$ for \$\\dfrac\{x \+ \d+\}\{x - (\d+)\}\$", text)
    if m:
        calc = int(m.group(1))
        if str(calc) != ans:
            issues.append(f"npv binomial: expected {calc}, got {ans}")

    # Rational add/mult numerator
    m = re.search(r"Simplify \$\\dfrac\{(\d+)\}\{x\} \+ \\dfrac\{(\d+)\}\{x\}\$.*?numerator", text)
    if m:
        calc = int(m.group(1)) + int(m.group(2))
        if str(calc) != ans:
            issues.append(f"rat add num: expected {calc}, got {ans}")

    m = re.search(r"Simplify \$\\dfrac\{(\d+)\}\{x\} \\cdot \\dfrac\{(\d+)\}\{x\}\$.*?numerator", text)
    if m:
        calc = int(m.group(1)) * int(m.group(2))
        if str(calc) != ans:
            issues.append(f"rat mult num: expected {calc}, got {ans}")

    # Linear model y=mx+b
    m = re.search(r"\$y = ([\d.]+)x \+ (-?[\d.]+)\$.*?when \$x = (\d+)\$", text)
    if m and "log" not in text and "sin" not in text:
        mval, b, x = float(m.group(1)), float(m.group(2)), int(m.group(3))
        calc = mval * x + b
        if "integer" in text.lower():
            if str(int(calc)) != ans and abs(calc - float(ans)) > 0.01:
                issues.append(f"linear eval: expected {calc}, got {ans}")
        elif "hundredth" in text.lower():
            if abs(round(calc, 2) - float(ans)) > 0.01:
                issues.append(f"linear eval: expected {round(calc,2)}, got {ans}")

    # Quadratic vertex form eval
    m = re.search(
        r"\$y = (-?[\d.]+)\(x - (-?[\d.]+)\)\^2 \+ (-?[\d.]+)\$.*?when \$x = (\d+)\$",
        text,
    )
    if m:
        a, h, k, x = float(m.group(1)), float(m.group(2)), float(m.group(3)), int(m.group(4))
        calc = a * (x - h) ** 2 + k
        if str(int(calc)) != ans and abs(calc - float(ans)) > 0.01:
            issues.append(f"quadratic eval: expected {calc}, got {ans}")

    # y-intercept (x-h)^2+k
    m = re.search(r"\$y = \(x - (-?\d+)\)\^2 \+ (-?\d+)\$.*?y\$-intercept", text)
    if m:
        h, k = int(m.group(1)), int(m.group(2))
        calc = h * h + k
        if str(calc) != ans:
            issues.append(f"y-int: expected {calc}, got {ans}")

    # log10 eval
    m = re.search(r"Evaluate \$\\log_\{10\}\(([\d.]+)\)\$", text)
    if m:
        val = float(m.group(1))
        if val > 0:
            calc = round(math.log10(val))
            if str(calc) != ans:
                issues.append(f"log10: expected {calc}, got {ans}")

    # a^x = b
    m = re.search(r"Solve \$(\d+)\^x = (\d+)\$ for \$x\$", text)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a > 0 and b > 0:
            calc = round(math.log(b, a))
            if str(calc) != ans:
                issues.append(f"exp solve: expected {calc}, got {ans}")

    # Compound growth
    m = re.search(
        r"population of \$(\d+)\$ grows at.*?\$P\(t\) = (\d+)\(1 \+ ([\d.]+)\)\^t.*?What is \$P\((\d+)\)",
        text, re.I,
    )
    if m:
        p0, rate, t = int(m.group(2)), float(m.group(3)), int(m.group(4))
        calc = round(p0 * (1 + rate) ** t)
        if str(calc) != ans:
            issues.append(f"growth: expected {calc}, got {ans}")

    m = re.search(
        r"worth \\\$\$(\d+)\$ depreciates at \$(\d+(?:\.\d+)?)\\%.*?V\(t\) = (\d+)\(1 - ([\d.]+)\)\^t.*?V\((\d+)\)",
        text,
    )
    if m:
        p0, rate, t = int(m.group(3)), float(m.group(4)), int(m.group(5))
        calc = round(p0 * (1 - rate) ** t)
        if str(calc) != ans:
            issues.append(f"decay: expected {calc}, got {ans}")

    # y = a * b^x
    m = re.search(r"\$y = (\d+) \\cdot \(([\d.]+)\)\^x\$.*?Round to the nearest hundredth", text)
    if m:
        a, b = int(m.group(1)), float(m.group(2))
        xm = re.search(r"when \$x = (\d+)\$", text)
        if xm:
            calc = round(a * b ** int(xm.group(1)), 2)
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"exp eval: expected {calc}, got {ans}")

    # log model
    m = re.search(r"\$y = (\d+)\\log\(x\) \+ (-?\d+)\$.*?when \$x = (\d+)\$", text)
    if m:
        coef, c, x = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calc = round(coef * math.log10(x) + c, 2)
        if abs(calc - float(ans)) > 0.01:
            issues.append(f"log model: expected {calc}, got {ans}")

    # Half-life
    m = re.search(r"starts at \$(\d+)\$ g and loses half.*?after \$(\d+)\$ periods", text)
    if m:
        init, periods = int(m.group(1)), int(m.group(2))
        calc = init * (0.5 ** periods)
        if calc == int(calc):
            calc_s = str(int(calc))
        else:
            calc_s = f"{calc:.1f}"
        if calc_s != ans and str(round(calc)) != ans:
            issues.append(f"half-life: expected {calc_s}, got {ans}")

    # Sinusoidal amplitude/period/midline
    sm = re.search(r"\$y = (\d+)\\sin\(([\d.]+)x", text)
    if sm and "amplitude" in text.lower():
        if str(int(sm.group(1))) != ans:
            issues.append(f"amplitude: expected {sm.group(1)}, got {ans}")
    if sm and "period rounded" in text.lower():
        b = float(sm.group(2))
        calc = round(2 * math.pi / b, 2)
        try:
            if abs(calc - float(ans)) > 0.02:
                issues.append(f"period: expected {calc}, got {ans}")
        except ValueError:
            pass

    mm = re.search(r"\$y = (\d+)\\sin\(([\d.]+)x.*?\) \+ (-?\d+)\$.*?midline", text)
    if mm:
        calc = int(mm.group(3))
        if str(calc) != ans:
            issues.append(f"midline: expected {calc}, got {ans}")

    # Max/min from amplitude and midline
    m = re.search(r"amplitude \$(\d+)\$ and midline \$y = (-?\d+)\$.*?maximum", text)
    if m:
        calc = int(m.group(2)) + int(m.group(1))
        if str(calc) != ans:
            issues.append(f"max: expected {calc}, got {ans}")

    m = re.search(r"amplitude \$(\d+)\$ and midline \$y = (-?\d+)\$.*?minimum", text)
    if m:
        calc = int(m.group(2)) - int(m.group(1))
        if str(calc) != ans:
            issues.append(f"min: expected {calc}, got {ans}")

    # sin evaluation
    m = re.search(r"\$y = (\d+)\\sin\(([\d.]+)x(?:\) \+ (\d+)|\)$)", text)
    if m and "Evaluate" in text:
        a, b = float(m.group(1)), float(m.group(2))
        d = float(m.group(3)) if m.group(3) else 0
        xm = re.search(r"at \$x = ([\d.]+)\$", text)
        if xm:
            x = float(xm.group(1))
            calc = round(a * math.sin(b * x) + d)
            if str(calc) != ans:
                issues.append(f"sin eval: expected {calc}, got {ans}")

    m = re.search(r"\$y = (\d+)\\sin\(x\) \+ (\d+)\$", text)
    if m and "radians" in text:
        a, d = int(m.group(1)), int(m.group(2))
        xm = re.search(r"\$x = ([\d.]+)\$ radians", text)
        if xm:
            calc = round(a * math.sin(float(xm.group(1))) + d)
            if str(calc) != ans:
                issues.append(f"sin(x) eval: expected {calc}, got {ans}")

    return issues


def audit_pool(pool: list) -> dict:
    report = {k: [] for k in [
        "schema_errors", "mc_key_errors", "mc_duplicate_choices", "nr_numeric_errors",
        "nr_calc_errors", "duplicate_stems", "duplicate_templates", "invalid_outcomes",
        "unit_mismatches", "weak_distractors", "implausible_distractors",
        "boilerplate_explanations", "repeated_common_mistakes", "repeated_skills",
        "repeated_explanations", "ambiguous_wording", "curriculum_flags", "grading_ambiguity",
        "sequence_nr_banned",
    ]}

    stems = defaultdict(list)
    templates = defaultdict(list)

    for i, q in enumerate(pool):
        reasons = validate_question(q, i)
        if reasons:
            report["schema_errors"].append({"index": i, "reasons": reasons})

        if q.get("unit") != TOPIC_UNIT.get(q["topic"]):
            report["unit_mismatches"].append({"index": i, "unit": q.get("unit"), "topic": q["topic"]})

        oc = q.get("outcome_code", "")
        if oc not in TOPIC_OUTCOMES.get(q["topic"], set()):
            report["invalid_outcomes"].append({"index": i, "outcome": oc, "topic": q["topic"]})

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["mc_key_errors"].append({"index": i, "answer": q.get("answer", "")[:80]})
            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                report["mc_duplicate_choices"].append({"index": i})
            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                t = c["text"].lower().strip()
                if any(p in t for p in WEAK_DISTRACTOR_PATTERNS):
                    report["weak_distractors"].append({"index": i, "distractor": c["text"][:60]})
                if len(c["text"].strip()) < 3:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"]})

        if q["question_type"] == "Numerical Response":
            if not is_numerical_answer(q.get("answer")):
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            if re.search(r"record all (?:\d+ )?digits|digits in order|sequence code", text := q["question_text"], re.I):
                report["sequence_nr_banned"].append({"index": i})
            if "record" not in q["question_text"].lower() and "express" not in q["question_text"].lower() and "round" not in q["question_text"].lower():
                report["grading_ambiguity"].append({"index": i})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)

        expl = q.get("explanation", "")
        if expl.startswith("The correct answer is") or len(expl) < 20:
            report["boilerplate_explanations"].append({"index": i})

        combined = (q["question_text"] + expl + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

        if "valid in context" in q["question_text"].lower() and q["question_type"] == "Numerical Response":
            report["ambiguous_wording"].append({"index": i, "reason": "context judgment in NR"})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > MAX_PER_TEMPLATE:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs})

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [
        {"text": t[:80], "count": c}
        for t, c in cm.items() if c > MAX_PER_MISTAKE
    ]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [{"text": t[:80], "count": c} for t, c in sk.items() if c > MAX_PER_SKILL]

    ex = Counter(q["explanation"] for q in pool)
    report["repeated_explanations"] = [{"text": t[:80], "count": c} for t, c in ex.items() if c > MAX_PER_EXPLANATION]

    return report


def count_blocking(report: dict) -> int:
    keys = [
        "schema_errors", "mc_key_errors", "mc_duplicate_choices", "nr_numeric_errors",
        "nr_calc_errors", "duplicate_stems", "duplicate_templates", "invalid_outcomes",
        "unit_mismatches", "weak_distractors", "implausible_distractors",
        "boilerplate_explanations", "ambiguous_wording", "curriculum_flags",
        "grading_ambiguity", "sequence_nr_banned", "repeated_common_mistakes",
        "repeated_skills", "repeated_explanations",
    ]
    return sum(len(report.get(k, [])) for k in keys)


def summarize(report: dict) -> None:
    for k, v in report.items():
        if isinstance(v, list) and v:
            print(f"{k}: {len(v)}")
            for item in v[:5]:
                print(f"  {item}")


if __name__ == "__main__":
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    report = audit_pool(pool)
    print(f"Pool size: {len(pool)}")
    summarize(report)
    print(f"Total blocking issues: {count_blocking(report)}")
    REPORT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
