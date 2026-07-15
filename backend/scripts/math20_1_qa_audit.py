"""Full production QA audit for Mathematics 20-1 question pool."""

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.question_validator import validate_question

POOL = Path(__file__).parent.parent.parent / "questions.json" / "math20-1_questions_pool.json"
REPORT = POOL.parent / "math20-1_qa_report.json"

TOPIC_OUTCOMES = {
    "Sequences and Series": {"RF9", "RF10"},
    "Trigonometry": {"T1", "T2", "T3"},
    "Quadratic Functions": {"RF3", "RF4"},
    "Quadratic Equations": {"RF1", "RF5"},
    "Radical Expressions and Equations": {"AN2", "AN3"},
    "Rational Expressions and Equations": {"AN4", "AN5", "AN6"},
    "Absolute Value and Reciprocal Functions": {"AN1", "RF2", "RF11"},
    "Systems of Equations": {"RF6"},
    "Linear and Quadratic Inequalities": {"RF7", "RF8"},
}

TOPIC_UNIT = {
    "Sequences and Series": "Relations and Functions",
    "Trigonometry": "Trigonometry",
    "Quadratic Functions": "Relations and Functions",
    "Quadratic Equations": "Relations and Functions",
    "Radical Expressions and Equations": "Algebra and Number",
    "Rational Expressions and Equations": "Algebra and Number",
    "Absolute Value and Reciprocal Functions": "Relations and Functions",
    "Systems of Equations": "Relations and Functions",
    "Linear and Quadratic Inequalities": "Relations and Functions",
}

WEAK_DISTRACTOR_PATTERNS = [
    "none of these", "none of the above", "all of the above",
    "cannot be determined", "not enough information",
]

CROSS_SUBJECT_TERMS = [
    "mitosis", "meiosis", "allele", "dna", "photosynthesis",
    "molar enthalpy", "oxidation number", "faraday", "equilibrium constant",
    "newton's third law", "momentum", "photoelectric", "half-life",
    "cell division", "hardy-weinberg", "endocrine", "neuron",
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
    topic = q["topic"]

    # Arithmetic t_n
    m = re.search(
        r"arithmetic sequence.*?\$t_1 = (-?\d+)\$ and \$d = (-?\d+)\$.*?What is \$t_\{(\d+)\}",
        text, re.S,
    )
    if m:
        t1, d, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calc = t1 + (n - 1) * d
        if str(calc) != ans:
            issues.append(f"arithmetic t_n: expected {calc}, got {ans}")

    # Arithmetic S_n
    m = re.search(
        r"first \$(\d+)\$ terms of the arithmetic series with \$t_1 = (\d+)\$ and \$d = (\d+)",
        text,
    )
    if m:
        n, t1, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calc = n * (2 * t1 + (n - 1) * d) // 2
        if str(calc) != ans:
            issues.append(f"arithmetic S_n: expected {calc}, got {ans}")

    # Arithmetic find n
    m = re.search(
        r"\$t_1 = (-?\d+)\$, common difference \$d = (-?\d+)\$, and \$t_n = (-?\d+)\$.*?value of \$n",
        text,
    )
    if m:
        t1, d, tn = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if d != 0 and (tn - t1) % d == 0:
            calc = 1 + (tn - t1) // d
            if str(calc) != ans:
                issues.append(f"arithmetic n: expected {calc}, got {ans}")

    # Geometric t_n
    m = re.search(
        r"geometric sequence has \$t_1 = (-?\d+)\$ and common ratio \$r = (-?\d+)\$.*?What is \$t_\{(\d+)\}",
        text,
    )
    if m:
        t1, r, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calc = t1 * (r ** (n - 1))
        if str(calc) != ans:
            issues.append(f"geometric t_n: expected {calc}, got {ans}")

    # Geometric S_n
    m = re.search(
        r"first \$(\d+)\$ terms of the geometric series with \$t_1 = (\d+)\$ and \$r = (-?\d+)\$",
        text,
    )
    if m:
        n, t1, r = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if r != 1:
            calc = t1 * (1 - r ** n) // (1 - r)
            if str(calc) != ans:
                issues.append(f"geometric S_n: expected {calc}, got {ans}")

    # Infinite geometric series
    m = re.search(
        r"first term \$t_1 = ([\d.]+)\$ and common ratio \$r = ([\d.]+)\$.*?sum to infinity",
        text,
    )
    if m:
        t1, r = float(m.group(1)), float(m.group(2))
        calc = round(t1 / (1 - r), 2)
        try:
            if abs(calc - float(ans)) > 0.02:
                issues.append(f"infinite series: expected {calc:.2f}, got {ans}")
        except ValueError:
            issues.append(f"non-numeric infinite series answer: {ans}")

    # Reference angle
    m = re.search(r"reference angle for \$(\d+)\^\\circ\$", text)
    if m:
        theta = int(m.group(1)) % 360
        if theta <= 90:
            calc = theta
        elif theta <= 180:
            calc = 180 - theta
        elif theta <= 270:
            calc = theta - 180
        else:
            calc = 360 - theta
        if str(calc) != ans:
            issues.append(f"reference angle: expected {calc}, got {ans}")

    # sin from point
    m = re.search(r"\$P\((-?\d+), (-?\d+)\)\$.*?What is \$\\sin\\theta\$", text)
    if m:
        x, y = int(m.group(1)), int(m.group(2))
        r = math.hypot(x, y)
        calc = round(y / r, 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"sin theta: expected {calc:.4f}, got {ans}")
        except ValueError:
            pass

    # cos from point
    m = re.search(r"\$P\((-?\d+), (-?\d+)\)\$.*?What is \$\\cos\\theta\$", text)
    if m:
        x, y = int(m.group(1)), int(m.group(2))
        r = math.hypot(x, y)
        calc = round(x / r, 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"cos theta: expected {calc:.4f}, got {ans}")
        except ValueError:
            pass

    # Exact trig
    m = re.search(
        r"exact value of \$\\(sin|cos)\\theta\$ for \$\\theta = (\d+)\^\\circ\$",
        text,
    )
    if m:
        ratio, angle = m.group(1), int(m.group(2))
        ref = angle % 90 if angle % 90 else (90 if angle % 180 else 0)
        if angle > 90:
            ref_angles = {30: 30, 45: 45, 60: 60, 120: 60, 135: 45, 150: 30,
                          210: 30, 225: 45, 240: 60, 300: 60, 315: 45, 330: 30}
            ref = ref_angles.get(angle, ref)
        exact = {30: (0.5, math.sqrt(3)/2), 45: (math.sqrt(2)/2, math.sqrt(2)/2),
                 60: (math.sqrt(3)/2, 0.5)}
        q = 1 if angle <= 90 else 2 if angle <= 180 else 3 if angle <= 270 else 4
        ref_val = 30 if ref == 30 else 45 if ref == 45 else 60
        s, c = exact.get(ref_val, (0, 0))
        val = s if ratio == "sin" else c
        signs = {1: (1, 1), 2: (1, -1), 3: (-1, -1), 4: (-1, 1)}
        sign = signs[q][0 if ratio == "sin" else 1]
        calc = round(sign * val, 4)
        try:
            if abs(calc - float(ans)) > 0.0002:
                issues.append(f"exact trig: expected {calc:.4f}, got {ans}")
        except ValueError:
            pass

    # Cosine law side
    m = re.search(
        r"\$a = (\d+)\$, \$b = (\d+)\$, and \$\\angle C = (\d+)\^\\circ\$.*?Find side \$c\$",
        text,
    )
    if m:
        a, b, ang = float(m.group(1)), float(m.group(2)), float(m.group(3))
        calc = round(math.sqrt(a**2 + b**2 - 2*a*b*math.cos(math.radians(ang))), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"cosine law: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Sine law side b
    m = re.search(
        r"\$a = (\d+)\$, \$\\angle A = (\d+)\^\\circ\$, and \$\\angle B = (\d+)\^\\circ\$.*?Find side \$b\$",
        text,
    )
    if m:
        a, A, B = float(m.group(1)), float(m.group(2)), float(m.group(3))
        calc = round(a * math.sin(math.radians(B)) / math.sin(math.radians(A)), 1)
        try:
            if abs(calc - float(ans)) > 0.15:
                issues.append(f"sine law: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Vertex x from vertex form
    m = re.search(
        r"\$f\(x\) = (-?\d+)\(x - \((-?\d+)\)\)\^2 \+ (-?\d+)\$.*?x\$-coordinate of the vertex",
        text,
    )
    if m:
        p = int(m.group(2))
        if str(p) != ans:
            issues.append(f"vertex x: expected {p}, got {ans}")

    # Discriminant intercept count
    m = re.search(
        r"How many \$x\$-intercepts does \$y = (-?\d+)x\^2 \+ (-?\d+)x \+ (-?\d+)\$",
        text,
    )
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        disc = b*b - 4*a*c
        calc = 0 if disc < 0 else 1 if disc == 0 else 2
        if str(calc) != ans:
            issues.append(f"intercept count: expected {calc}, got {ans}")

    # Axis of symmetry
    m = re.search(
        r"\$f\(x\) = (-?\d+)x\^2 \+ (-?\d+)x \+ (-?\d+)\$.*?axis of symmetry is \$x = k\$",
        text,
    )
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        calc = round(-b / (2 * a), 2)
        try:
            if abs(calc - float(ans)) > 0.01:
                issues.append(f"axis: expected {calc:.2f}, got {ans}")
        except ValueError:
            pass

    # Factor root product
    m = re.search(
        r"Factor \$x\^2 \+ (-?\d+)x \+ (-?\d+)\$.*?product of the two roots",
        text,
    )
    if m:
        b, c = int(m.group(1)), int(m.group(2))
        # x^2 + bx + c = (x-r1)(x-r2), product = c
        if str(c) != ans:
            issues.append(f"root product: expected {c}, got {ans}")

    # Quadratic larger root (monic)
    m = re.search(r"Solve \$x\^2 \+ (-?\d+)x \+ (-?\d+) = 0\$.*?larger root", text)
    if m:
        b, c = int(m.group(1)), int(m.group(2))
        disc = b*b - 4*c
        if disc >= 0:
            r1 = (-b + math.sqrt(disc)) / 2
            r2 = (-b - math.sqrt(disc)) / 2
            calc = int(max(r1, r2)) if abs(max(r1, r2) - int(max(r1, r2))) < 1e-9 else round(max(r1, r2), 2)
            try:
                if str(calc) != ans and abs(float(calc) - float(ans)) > 0.01:
                    issues.append(f"larger root: expected {calc}, got {ans}")
            except ValueError:
                pass

    # Simplify sqrt coefficient
    m = re.search(
        r"Simplify \$\\sqrt\{(\d+)\}\$.*?What is the value of \$a\$.*?coefficient",
        text,
    )
    if m:
        n = int(m.group(1))
        coeff = 1
        r = n
        for p in [2, 3, 5, 7, 11, 13]:
            while r % (p * p) == 0:
                coeff *= p
                r //= p * p
        if str(coeff) != ans:
            issues.append(f"sqrt coeff: expected {coeff}, got {ans}")

    # Like radical sum coefficient
    m = re.search(
        r"Simplify \$(\d+)\\sqrt\{(\d+)\} \+ (\d+)\\sqrt\{\2\}\$.*?coefficient of \$\\sqrt\{\2\}",
        text,
    )
    if m:
        calc = int(m.group(1)) + int(m.group(3))
        if str(calc) != ans:
            issues.append(f"radical sum: expected {calc}, got {ans}")

    # Radical equation sqrt(x+a)=b
    m = re.search(r"Solve \$\\sqrt\{x \+ (\d+)\} = (\d+)\$ for \$x\$", text)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        calc = b*b - a
        if str(calc) != ans:
            issues.append(f"radical eq: expected {calc}, got {ans}")

    # Radical eq sqrt(x-a)+b=c
    m = re.search(r"Solve \$\\sqrt\{x - (\d+)\} \+ (\d+) = (\d+)\$ for \$x\$", text)
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        inner = c - b
        if inner > 0:
            calc = inner**2 + a
            if str(calc) != ans:
                issues.append(f"radical eq2: expected {calc}, got {ans}")

    # Non-permissible linear
    m = re.search(
        r"non-permissible value of \$x\$ for \$\\dfrac\{1\}\{(-?\d+)x \+ (-?\d+)\}\$",
        text,
    )
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a != 0 and (-b % a) == 0:
            calc = -b // a
            if str(calc) != ans:
                issues.append(f"non-permissible: expected {calc}, got {ans}")

    # Non-permissible binomial x-r
    m = re.search(
        r"non-permissible value of \$x\$ for \$\\dfrac\{x \+ 1\}\{x - (\d+)\}\$",
        text,
    )
    if m:
        calc = int(m.group(1))
        if str(calc) != ans:
            issues.append(f"non-permissible binomial: expected {calc}, got {ans}")

    # Rational add numerator
    m = re.search(
        r"Simplify \$\\dfrac\{(\d+)\}\{x \+ (-?\d+)\} \+ \\dfrac\{(\d+)\}\{x \+ \2\}\$.*?numerator",
        text,
    )
    if m:
        calc = int(m.group(1)) + int(m.group(3))
        if str(calc) != ans:
            issues.append(f"rational add: expected {calc}, got {ans}")

    # Rational multiply numerator
    m = re.search(
        r"Simplify \$\\dfrac\{(\d+)\}\{x\} \\cdot \\dfrac\{(\d+)\}\{x\}\$.*?numerator",
        text,
    )
    if m:
        calc = int(m.group(1)) * int(m.group(2))
        if str(calc) != ans:
            issues.append(f"rational mult: expected {calc}, got {ans}")

    # Rational divide
    m = re.search(
        r"Simplify \$\\dfrac\{(\d+)\}\{x\} \\div \\dfrac\{(\d+)\}\{x\}\$.*?numerical value",
        text,
    )
    if m:
        n, d = int(m.group(1)), int(m.group(2))
        if d != 0 and n % d == 0:
            calc = n // d
            if str(calc) != ans:
                issues.append(f"rational div: expected {calc}, got {ans}")

    # Rational equation a/(x-k)=b
    m = re.search(r"Solve \$\\dfrac\{(\d+)\}\{x - (-?\d+)\} = (\d+)\$ for \$x\$", text)
    if m:
        a, k, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if b != 0:
            calc = a / b + k
            if calc == int(calc):
                calc = int(calc)
            if str(calc) != ans:
                issues.append(f"rational eq: expected {calc}, got {ans}")

    # Absolute value larger solution
    m = re.search(
        r"Solve \$\|(-?\d+)x \+ (-?\d+)\| = (\d+)\$.*?larger solution",
        text,
    )
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        x1 = (c - b) / a
        x2 = (-c - b) / a
        calc = int(max(x1, x2)) if max(x1, x2) == int(max(x1, x2)) else max(x1, x2)
        try:
            if str(calc) != ans and abs(float(calc) - float(ans)) > 0.01:
                issues.append(f"abs val: expected {calc}, got {ans}")
        except ValueError:
            pass

    # Vertical asymptote
    m = re.search(
        r"\$f\(x\) = (-?\d+)x \+ (-?\d+)\$.*?vertical asymptote.*?Record the integer",
        text,
    )
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a != 0 and (-b % a) == 0:
            calc = -b // a
            if str(calc) != ans:
                issues.append(f"asymptote: expected {calc}, got {ans}")

    # System intersection x
    m = re.search(
        r"\$y = (-?\d+)x \+ (-?\d+)\$ and \$y = (-?\d+)x \+ (-?\d+)\$.*?x\$-coordinate",
        text,
    )
    if m:
        m1, b1, m2, b2 = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        if m1 != m2:
            x = (b2 - b1) / (m1 - m2)
            if x == int(x):
                if str(int(x)) != ans:
                    issues.append(f"system x: expected {int(x)}, got {ans}")

    # |val| absolute value
    m = re.search(r"Evaluate \$\\left\|(-?\d+)\\right\|\$|Evaluate \$\|(-?\d+)\|\$", text)
    if m:
        v = int(m.group(1) or m.group(2))
        if str(abs(v)) != ans:
            issues.append(f"|x|: expected {abs(v)}, got {ans}")

    # Distance on number line
    m = re.search(r"distance between \$(-?\d+)\$ and \$(-?\d+)\$ on a number line", text)
    if m:
        calc = abs(int(m.group(1)) - int(m.group(2)))
        if str(calc) != ans:
            issues.append(f"distance: expected {calc}, got {ans}")

    # Inequality boundary root
    m = re.search(
        r"Find the larger root of \$x\^2 \+ (-?\d+)x \+ (-?\d+) = 0\$",
        text,
    )
    if m and topic == "Linear and Quadratic Inequalities":
        b, c = int(m.group(1)), int(m.group(2))
        disc = b*b - 4*c
        if disc >= 0:
            r1 = (-b + math.sqrt(disc)) / 2
            r2 = (-b - math.sqrt(disc)) / 2
            calc = int(max(r1, r2))
            if str(calc) != ans:
                issues.append(f"boundary root: expected {calc}, got {ans}")

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
        "unit_mismatches": [],
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

        if q.get("unit") != TOPIC_UNIT.get(q["topic"]):
            report["unit_mismatches"].append({"index": i, "unit": q.get("unit"), "topic": q["topic"]})

        oc = q.get("outcome_code", "")
        if oc not in TOPIC_OUTCOMES.get(q["topic"], set()):
            report["invalid_outcomes"].append({"index": i, "outcome": oc, "topic": q["topic"]})

        if q["question_type"] == "Multiple Choice":
            correct = [c for c in q["choices"] if c.get("is_correct")]
            if len(correct) != 1 or correct[0]["text"] != q["answer"]:
                report["mc_key_errors"].append({"index": i, "answer": q.get("answer", "")[:60]})

            texts = [normalize(c["text"]) for c in q["choices"]]
            if len(texts) != len(set(texts)):
                report["mc_duplicate_choices"].append({"index": i})

            for c in q["choices"]:
                if c.get("is_correct"):
                    continue
                t = c["text"].lower().strip()
                if any(p in t for p in WEAK_DISTRACTOR_PATTERNS):
                    report["weak_distractors"].append({"index": i, "distractor": c["text"][:60]})
                if len(c["text"].strip()) < 5:
                    report["weak_distractors"].append({"index": i, "distractor": c["text"], "reason": "too short"})

        if q["question_type"] == "Numerical Response":
            try:
                float(str(q["answer"]).strip().strip("$"))
            except ValueError:
                report["nr_numeric_errors"].append({"index": i, "answer": q["answer"]})
            for issue in verify_nr_answer(q):
                report["nr_calc_errors"].append({"index": i, "issue": issue})
            if "record" not in q["question_text"].lower() and "express" not in q["question_text"].lower():
                report["grading_ambiguity"].append({"index": i, "reason": "no recording instruction"})

        stems[normalize(q["question_text"])].append(i)
        templates[template_key(q)].append(i)

        expl = q.get("explanation", "")
        if expl.startswith("The correct answer is") or len(expl) < 25:
            report["boilerplate_explanations"].append({"index": i})

        combined = (q["question_text"] + q["explanation"] + q["common_mistake"]).lower()
        for term in CROSS_SUBJECT_TERMS:
            if term in combined:
                report["curriculum_flags"].append({"index": i, "term": term})

        if q["question_type"] == "Multiple Choice":
            if "which of the following" in q["question_text"].lower() and "could be" not in q["question_text"].lower():
                pass  # ok
            if re.search(r"\bor\b.*\bor\b.*\bor\b", q["question_text"], re.I):
                report["ambiguous_wording"].append({"index": i, "reason": "multiple or clauses"})

    for stem, idxs in stems.items():
        if len(idxs) > 1:
            report["duplicate_stems"].append({"indices": idxs, "stem": stem[:100]})

    for tk, idxs in templates.items():
        if len(idxs) > MAX_PER_TEMPLATE:
            report["duplicate_templates"].append({"key": tk[:80], "count": len(idxs), "indices": idxs})

    cm = Counter(q["common_mistake"] for q in pool)
    report["repeated_common_mistakes"] = [
        {"text": t[:80], "count": c, "indices": [i for i, q in enumerate(pool) if q["common_mistake"] == t][:6]}
        for t, c in cm.items() if c > MAX_PER_MISTAKE
    ]

    sk = Counter(q["skill_tested"] for q in pool)
    report["repeated_skills"] = [
        {"text": t[:80], "count": c}
        for t, c in sk.items() if c > MAX_PER_SKILL
    ]

    ex = Counter(q["explanation"] for q in pool)
    report["repeated_explanations"] = [
        {"text": t[:80], "count": c}
        for t, c in ex.items() if c > MAX_PER_EXPLANATION
    ]

    return report


def count_blocking(report: dict) -> int:
    keys = [
        "schema_errors", "mc_key_errors", "mc_duplicate_choices",
        "nr_numeric_errors", "nr_calc_errors", "duplicate_stems",
        "duplicate_templates", "invalid_outcomes", "unit_mismatches",
        "weak_distractors", "implausible_distractors", "boilerplate_explanations",
        "ambiguous_wording", "curriculum_flags", "grading_ambiguity",
        "repeated_common_mistakes", "repeated_skills", "repeated_explanations",
    ]
    return sum(len(report.get(k, [])) for k in keys)


def summarize(report: dict) -> None:
    for k, v in report.items():
        if isinstance(v, list) and v:
            print(f"{k}: {len(v)}")
            for item in v[:8]:
                print(f"  {item}")


if __name__ == "__main__":
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    report = audit_pool(pool)
    print(f"Pool size: {len(pool)}")
    summarize(report)
    print(f"Total blocking issues: {count_blocking(report)}")
    REPORT.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"Report: {REPORT}")
