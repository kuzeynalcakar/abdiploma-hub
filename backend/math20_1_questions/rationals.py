"""Programmatic Rational Expressions and Equations (AN4, AN5, AN6)."""

import random
from math20_1_questions.helpers import mc, nr

TOPIC = "Rational Expressions and Equations"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # AN4 non-permissible values
    for a in [2, 3, 4, 5, -2, -3]:
        for b in [1, 2, 3, -1, -4, 5]:
            if a == 0:
                continue
            npv = -b / a
            if npv != int(npv):
                continue
            out.append(nr(
                f"State the non-permissible value of $x$ for "
                f"$\\dfrac{{1}}{{{a}x + {b}}}$. Record the integer answer.",
                str(int(npv)),
                f"Denominator $= 0$ when ${a}x + {b} = 0$, so $x = {int(npv)}$.",
                "Students set numerator equal to zero instead.",
                topic=TOPIC, outcome_code="AN4",
                skill_tested="Determining non-permissible value for linear denominator",
                difficulty="Easy", estimated_time_seconds=60,
            ))

    for r in [2, 3, -2, 4, -3, 5]:
        out.append(nr(
            f"State the non-permissible value of $x$ for "
            f"$\\dfrac{{x + 1}}{{x - {r}}}$. Record the integer answer.",
            str(r),
            f"Denominator zero when $x = {r}$.",
            "Students solve $x + 1 = 0$ instead.",
            topic=TOPIC, outcome_code="AN4",
            skill_tested="Finding non-permissible value for binomial denominator",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # AN4 simplify
    for a in [2, 3, 4, 5, 6]:
        sq = a ** 2
        out.append(mc(
            f"Simplify $\\dfrac{{x^2 - {sq}}}{{x - {a}}}$ for $x \\ne {a}$.",
            f"$x + {a}$",
            [f"$x - {a}$", f"$x + {sq}$", f"$\\dfrac{{x - {a}}}{{{a}}}$"],
            f"Factor: $\\dfrac{{(x-{a})(x+{a})}}{{x-{a}}} = x+{a}$.",
            "Cancelling terms instead of factors.",
            topic=TOPIC, outcome_code="AN4",
            skill_tested="Simplifying rational expression by factoring numerator",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # AN5 operations
    for d in [2, 3, 4, 5, 6, 7]:
        n1, n2 = rng.randint(1, 5), rng.randint(1, 5)
        num = n1 + n2
        out.append(nr(
            f"Simplify $\\dfrac{{{n1}}}{{x}} + \\dfrac{{{n2}}}{{x}}$ for $x \\ne 0$. "
            f"What is the numerator of the result? Record the integer answer.",
            str(num),
            f"Common denominator: $\\dfrac{{{n1}+{n2}}}{{x}} = \\dfrac{{{num}}}{{x}}$.",
            "Students add denominators.",
            topic=TOPIC, outcome_code="AN5",
            skill_tested="Adding rational expressions with common denominator",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for a, b, c in [(1, 2, 1), (2, 3, 1), (1, 3, 2), (3, 4, 1), (2, 5, 3),
                    (1, 4, 3), (3, 5, 2), (2, 7, 5)]:
        #  a/(x-b) + c/(x-b) style via different setup
        out.append(nr(
            f"Simplify $\\dfrac{{{a}}}{{x + {b}}} + \\dfrac{{{c}}}{{x + {b}}}$. "
            f"What is the numerator? Record the integer answer.",
            str(a + c),
            f"$\\dfrac{{{a}+{c}}}{{x+{b}}} = \\dfrac{{{a+c}}}{{x+{b}}}$.",
            "Adding denominators instead of numerators.",
            topic=TOPIC, outcome_code="AN5",
            skill_tested="Adding rational expressions with same binomial denominator",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for n1, n2 in [(2, 3), (3, 4), (2, 5), (4, 3), (5, 2), (3, 5)]:
        prod = n1 * n2
        out.append(nr(
            f"Simplify $\\dfrac{{{n1}}}{{x}} \\cdot \\dfrac{{{n2}}}{{x}}$ for $x \\ne 0$. "
            f"What is the numerator of the result? Record the integer answer.",
            str(prod),
            f"Multiply numerators and denominators: $\\dfrac{{{prod}}}{{x^2}}$.",
            "Students add instead of multiply.",
            topic=TOPIC, outcome_code="AN5",
            skill_tested="Multiplying rational expressions",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for n, d in [(6, 2), (10, 5), (12, 3), (15, 5), (8, 4), (9, 3), (20, 4)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{n}}}{{x}} \\div \\dfrac{{{d}}}{{x}}$ for $x \\ne 0$. "
            f"What is the simplified numerical value? Record the integer answer.",
            str(n // d),
            f"Division: $\\dfrac{{{n}}}{{x}} \\cdot \\dfrac{{x}}{{{d}}} = \\dfrac{{{n}}}{{{d}}} = {n // d}$.",
            "Students divide denominators only.",
            topic=TOPIC, outcome_code="AN5",
            skill_tested="Dividing rational expressions with monomial denominators",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # AN6 rational equations
    for a, b, c in [(3, 2, 5), (4, 1, 3), (5, 3, 4), (2, 1, 4), (6, 2, 4),
                    (8, 3, 5), (5, 2, 7), (7, 4, 3)]:
        # (x + a)/(x - b) = c  => x + a = c(x-b) => x + a = cx - cb => x - cx = -cb - a
        # x(1-c) = -cb - a
        if c == 1:
            continue
        x = (-c * (-b) - a) / (1 - c) if False else None
        # simpler: a/x = b  => x = a/b
        pass

    for num, den in [(6, 2), (8, 4), (9, 3), (10, 5), (12, 4), (15, 3), (14, 7)]:
        out.append(nr(
            f"Solve $\\dfrac{{{num}}}{{x}} = {den // num if num != 0 else 1}$ for $x$. "
            f"Record the integer answer.",
            str(num // den if den != 0 else num),
            f"Cross-multiply or multiply both sides by $x$.",
            "Students invert the fraction incorrectly.",
            topic=TOPIC, outcome_code="AN6",
            skill_tested="Solving simple rational equation",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    # Fix rational equations properly: a/(x-k) = b
    for a, k, b in [(2, 3, 4), (3, 1, 2), (4, 2, 3), (5, -1, 2), (2, 5, 1),
                    (6, 2, 3), (3, 4, 1), (8, 1, 4), (4, -2, 2), (5, 3, 2)]:
        # a/(x-k)=b => a = b(x-k) => x = a/b + k
        if b == 0:
            continue
        x = a / b + k
        if x == k:
            continue
        if x != int(x):
            x_int = round(x)
            if abs(x - x_int) > 0.01:
                continue
            x = x_int
        else:
            x = int(x)
        out.append(nr(
            f"Solve $\\dfrac{{{a}}}{{x - {k}}} = {b}$ for $x$. Record the integer answer.",
            str(x),
            f"${a} = {b}(x - {k})$, so $x - {k} = {a/b:g}$, $x = {x}$.",
            "Students forget to multiply all terms when clearing denominator.",
            topic=TOPIC, outcome_code="AN6",
            skill_tested="Solving rational equation with binomial denominator",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # MC conceptual
    mc_items = [
        ("Simplifying $\\dfrac{x^2 - 9}{x - 3}$ gives $x + 3$. What is the non-permissible value?",
         "$x = 3$",
         ["$x = -3$", "$x = 9$", "There is no restriction"],
         "The original denominator $x - 3$ cannot equal zero.",
         "Using the simplified form and forgetting the original restriction.", "AN4",
         "Identifying non-permissible value after simplification", "Medium", 80),
        ("Which operation requires finding a lowest common denominator first?",
         "Adding $\\dfrac{2}{x+1} + \\dfrac{3}{x-2}$",
         ["Multiplying $\\dfrac{1}{x} \\cdot \\dfrac{2}{x}$",
          "Dividing $\\dfrac{5}{x} \\div \\dfrac{5}{x}$",
          "Simplifying $\\dfrac{x}{x}$"],
         "Unlike denominators $x+1$ and $x-2$ need an LCD before adding.",
         "Assuming all rational operations need an LCD.", "AN5",
         "Recognizing when LCD is required for rational operations", "Medium", 75),
        ("A value that makes a denominator zero in a rational equation is:",
         "A non-permissible value that must be excluded",
         ["Always a valid solution", "Always the only solution",
          "Irrelevant to the solution process"],
         "Denominator zero makes the expression undefined.",
         "Including values that zero the denominator as solutions.", "AN6",
         "Explaining role of non-permissible values in rational equations", "Easy", 55),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, t in mc_items:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    return out
