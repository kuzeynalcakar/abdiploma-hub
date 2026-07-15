"""Programmatic Radical Expressions and Equations (AN2, AN3)."""

import math
import random
from math20_1_questions.helpers import mc, nr

TOPIC = "Radical Expressions and Equations"


def _simplify_sqrt(n: int) -> tuple[int, int]:
    """Return (coefficient, radicand) for sqrt(n) simplified."""
    coeff = 1
    r = n
    for p in [2, 3, 5, 7, 11, 13]:
        while r % (p * p) == 0:
            coeff *= p
            r //= p * p
    return coeff, r


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # AN2 simplify radicals
    radicands = [8, 12, 18, 20, 24, 27, 32, 45, 48, 50, 54, 72, 75, 80, 98,
                 28, 63, 99, 108, 125, 200, 288, 320, 432, 500]
    for n in radicands:
        c, r = _simplify_sqrt(n)
        if c == 1:
            continue
        if r == 1:
            ans = str(c)
            qtext = (f"Simplify $\\sqrt{{{n}}}$ completely. "
                     f"Record the integer answer.")
            expl = f"$\\sqrt{{{n}}} = {c}$."
        else:
            ans = f"{c}√{r}" if c > 1 else f"√{r}"
            qtext = (f"Simplify $\\sqrt{{{n}}}$ to mixed radical form $a\\sqrt{{b}}$ "
                     f"where $b$ is not a perfect square. "
                     f"What is the value of $a$? Record the integer coefficient.")
            ans = str(c)
            expl = f"$\\sqrt{{{n}}} = {c}\\sqrt{{{r}}}$."
        out.append(nr(
            qtext, ans, expl,
            "Students leave a perfect-square factor inside the radical.",
            topic=TOPIC, outcome_code="AN2",
            skill_tested="Simplifying square roots to mixed radical form",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for _ in range(15):
        a = rng.choice([2, 3, 4, 5])
        b = rng.choice([2, 3, 5, 7])
        n = a * a * b
        out.append(nr(
            f"Express $\\sqrt{{{n}}}$ as a mixed radical. What is the radicand $b$ "
            f"in $a\\sqrt{{b}}$? Record the integer answer.",
            str(b),
            f"$\\sqrt{{{n}}} = {a}\\sqrt{{{b}}}$; radicand $= {b}$.",
            "Students report the coefficient instead of the radicand.",
            topic=TOPIC, outcome_code="AN2",
            skill_tested="Identifying radicand after simplifying square root",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Operations on radicals
    for c1, r1, c2, r2 in [(2, 3, 3, 3), (2, 5, 4, 5), (3, 2, 2, 2), (2, 7, 5, 7),
                              (4, 3, 3, 3), (2, 6, 3, 6), (5, 2, 2, 2)]:
        coeff = c1 + c2
        out.append(nr(
            f"Simplify ${c1}\\sqrt{{{r1}}} + {c2}\\sqrt{{{r2}}}$. "
            f"What is the coefficient of $\\sqrt{{{r1}}}$ in the answer? Record the integer.",
            str(coeff),
            f"Like radicals: $({c1}+{c2})\\sqrt{{{r1}}} = {coeff}\\sqrt{{{r1}}}$.",
            "Students add radicands instead of coefficients.",
            topic=TOPIC, outcome_code="AN2",
            skill_tested="Adding like radical expressions",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for c1, r1, c2, r2 in [(2, 3, 5, 2), (3, 5, 2, 3), (2, 7, 3, 2), (4, 2, 3, 3)]:
        prod = c1 * c2 * _simplify_sqrt(r1 * r2)[0] ** 2 * _simplify_sqrt(r1 * r2)[1]
        sc, sr = _simplify_sqrt(r1 * r2)
        ans = c1 * c2 * sc
        out.append(nr(
            f"Simplify ${c1}\\sqrt{{{r1}}} \\cdot {c2}\\sqrt{{{r2}}}$. "
            f"If the answer is $k\\sqrt{{{sr}}}$, what is $k$? Record the integer.",
            str(ans),
            f"Multiply coefficients and radicands: "
            f"${c1}\\sqrt{{{r1}}} \\cdot {c2}\\sqrt{{{r2}}} = {ans}\\sqrt{{{sr}}}$.",
            "Students add coefficients when multiplying radicals.",
            topic=TOPIC, outcome_code="AN2",
            skill_tested="Multiplying radical expressions",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Domain / restrictions AN2.8
    for a, b in [(3, 5), (2, -4), (5, 7), (4, -1), (1, 6), (6, -3)]:
        if a > 0:
            restriction = f"x \\ge {-b/a:.2f}" if b != 0 else "x \\ge 0"
            val = math.ceil(-b / a) if (-b / a) == int(-b / a) else None
        else:
            restriction = f"x \\le {-b/a:.2f}"
        if a > 0:
            bound = -b / a
            out.append(nr(
                f"For what smallest integer $x$ is $\\sqrt{{{a}x + {b}}}$ defined? "
                f"Record the integer answer.",
                str(math.ceil(bound) if bound != int(bound) else int(bound)),
                f"Require ${a}x + {b} \\ge 0$, so $x \\ge {bound:.2f}$.",
                "Students use $>$ instead of $\\ge$ and pick the wrong integer.",
                topic=TOPIC, outcome_code="AN2",
                skill_tested="Finding domain of square root expression",
                difficulty="Medium", estimated_time_seconds=85,
            ))

    # AN3 radical equations
    for a, b, c in [(5, 3, 2), (10, 4, 3), (13, 5, 2), (8, 2, 3), (17, 4, 1),
                    (6, 1, 2), (11, 6, 5), (7, 3, 4)]:
        # sqrt(x + a) = b  => x = b^2 - a
        x = b ** 2 - a
        if x + a < 0:
            continue
        out.append(nr(
            f"Solve $\\sqrt{{x + {a}}} = {b}$ for $x$. Record the integer answer.",
            str(x),
            f"Square both sides: $x + {a} = {b}^2 = {b**2}$, so $x = {x}$. "
            f"Check: $\\sqrt{{{x + a}}} = {b}$.",
            "Students forget to square the right side completely.",
            topic=TOPIC, outcome_code="AN3",
            skill_tested="Solving basic radical equation by squaring both sides",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for a, b, c in [(2, 3, 1), (3, 4, 1), (4, 5, 1), (2, 5, 3), (3, 7, 4)]:
        # sqrt(x - a) + b = c  => sqrt = c-b, x = (c-b)^2 + a
        inner = c - b
        if inner <= 0:
            continue
        x = inner ** 2 + a
        out.append(nr(
            f"Solve $\\sqrt{{x - {a}}} + {b} = {c}$ for $x$. Record the integer answer.",
            str(x),
            f"Isolate: $\\sqrt{{x-{a}}} = {inner}$, square: $x - {a} = {inner**2}$, $x = {x}$.",
            "Students square before isolating the radical.",
            topic=TOPIC, outcome_code="AN3",
            skill_tested="Solving radical equation requiring isolation first",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # AN1 moved to supplements / absolute value topic
    # Conceptual MC
    mc_items = [
        ("Which is equivalent to $\\sqrt{72}$?",
         "$6\\sqrt{2}$",
         ["$3\\sqrt{8}$", "$12\\sqrt{6}$", "$8\\sqrt{3}$"],
         "$\\sqrt{72} = \\sqrt{36 \\cdot 2} = 6\\sqrt{2}$.",
         "Not simplifying completely.", "AN2",
         "Selecting fully simplified radical form", "Easy", 55),
        ("When solving $\\sqrt{x + 2} = x$, why must solutions be verified?",
         "Squaring can introduce extraneous roots",
         ["Radicals cannot have negative radicands ever",
          "The equation has no solutions ever",
          "Verification is optional for linear equations"],
         "Non-linear operations like squaring may add false solutions.",
         "Assuming all algebraic steps preserve equivalence.", "AN3",
         "Explaining need to verify radical equation solutions", "Medium", 80),
        ("Which expression is undefined for real numbers?",
         "$\\sqrt{-5}$",
         ["$\\sqrt{5}$", "$\\sqrt{0}$", "$\\sqrt{25}$"],
         "A negative radicand has no real square root.",
         "Thinking $\\sqrt{-5} = -\\sqrt{5}$.", "AN2",
         "Identifying undefined radical expressions", "Easy", 50),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, t in mc_items:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    return out
