"""Rational Expressions and Equations — RF1, RF2, RF3."""

import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Rational Expressions and Equations"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- RF1: equivalent forms and non-permissible values ---
    for a in [2, 3, 4, 5, -2, -3, 6, -4]:
        for b in [1, 2, 3, -1, -5, 4, -3]:
            if a == 0:
                continue
            npv = -b / a
            if npv != int(npv):
                continue
            out.append(nr(
                f"State the non-permissible value of $x$ for "
                f"$\\dfrac{{5}}{{{a}x + {b}}}$. Record the integer answer.",
                str(int(npv)),
                f"Denominator $= 0$ when ${a}x + {b} = 0$, so $x = {int(npv)}$.",
                "Students set the numerator equal to zero.",
                topic=TOPIC, outcome_code="RF1",
                skill_tested="Determining non-permissible value for linear denominator",
                difficulty="Easy", estimated_time_seconds=60,
            ))

    for r in [2, 3, -2, 4, -3, 5, -5, 7]:
        out.append(nr(
            f"State the non-permissible value of $x$ for "
            f"$\\dfrac{{x + 4}}{{x - {r}}}$. Record the integer answer.",
            str(r),
            f"Denominator zero when $x = {r}$.",
            "Students solve $x + 4 = 0$ instead.",
            topic=TOPIC, outcome_code="RF1",
            skill_tested="Finding non-permissible value for binomial denominator",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    for a in [2, 3, 4, 5, 6, 7, 8]:
        sq = a ** 2
        out.append(mc(
            f"Simplify $\\dfrac{{x^2 - {sq}}}{{x - {a}}}$ for $x \\ne {a}$.",
            f"$x + {a}$",
            [f"$x - {a}$", f"$x + {sq}$", f"$\\dfrac{{x - {a}}}{{{a}}}$"],
            f"Factor: $\\dfrac{{(x-{a})(x+{a})}}{{x-{a}}} = x+{a}$.",
            "Cancelling terms instead of factors.",
            topic=TOPIC, outcome_code="RF1",
            skill_tested="Simplifying rational expression by factoring difference of squares",
            difficulty="Medium", estimated_time_seconds=85,
        ))
        out.append(mc(
            f"Simplify $\\dfrac{{x^2 - {sq}}}{{x + {a}}}$ for $x \\ne -{a}$.",
            f"$x - {a}$",
            [f"$x + {a}$", f"$x - {sq}$", f"$\\dfrac{{x + {a}}}{{{a}}}$"],
            f"$\\dfrac{{(x-{a})(x+{a})}}{{x+{a}}} = x-{a}$.",
            "Sign error when cancelling $(x+a)$.",
            topic=TOPIC, outcome_code="RF1",
            skill_tested="Simplifying rational expression with binomial denominator",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for n, d, simp in [(6, 3, 2), (10, 5, 2), (8, 4, 2), (15, 3, 5), (12, 6, 2),
                       (9, 3, 3), (14, 7, 2), (20, 4, 5)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{n}x}}{{{d}x}}$ for $x \\ne 0$. "
            f"What is the simplified coefficient of $x$? Record the integer answer.",
            str(simp),
            f"$\\dfrac{{{n}x}}{{{d}x}} = {simp}$ for $x \\ne 0$.",
            "Students cancel $x$ but keep incorrect coefficient ratio.",
            topic=TOPIC, outcome_code="RF1",
            skill_tested="Simplifying rational expression with monomial terms",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # --- RF2: operations ---
    for n1, n2 in [(2, 3), (3, 5), (4, 1), (5, 2), (6, 4), (7, 3), (2, 7), (8, 5)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{n1}}}{{x}} + \\dfrac{{{n2}}}{{x}}$ for $x \\ne 0$. "
            f"What is the numerator of the result? Record the integer answer.",
            str(n1 + n2),
            f"$\\dfrac{{{n1}+{n2}}}{{x}} = \\dfrac{{{n1+n2}}}{{x}}$.",
            "Students add denominators.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Adding rational expressions with common monomial denominator",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for a, b, c in [(2, 3, 4), (1, 5, 2), (3, 2, 5), (4, 1, 3), (2, 7, 1), (5, 4, 2)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{a}}}{{x + {b}}} + \\dfrac{{{c}}}{{x + {b}}}$. "
            f"What is the numerator? Record the integer answer.",
            str(a + c),
            f"Common denominator: numerator $= {a} + {c} = {a+c}$.",
            "Adding denominators instead of numerators.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Adding rational expressions with same binomial denominator",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for n1, n2 in [(2, 3), (3, 4), (4, 5), (5, 2), (3, 5), (6, 2)]:
        prod = n1 * n2
        out.append(nr(
            f"Simplify $\\dfrac{{{n1}}}{{x}} \\cdot \\dfrac{{{n2}}}{{x}}$ for $x \\ne 0$. "
            f"What is the numerator? Record the integer answer.",
            str(prod),
            f"$\\dfrac{{{prod}}}{{x^2}}$.",
            "Students add numerators.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Multiplying rational expressions",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for num, den, quot in [(6, 2, 3), (10, 5, 2), (12, 3, 4), (15, 5, 3), (8, 4, 2), (9, 3, 3)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{num}x^2}}{{{den}x}}$ for $x \\ne 0$. "
            f"What is the coefficient of $x$ in the result? Record the integer answer.",
            str(quot),
            f"$\\dfrac{{{num}x^2}}{{{den}x}} = {quot}x$.",
            "Students divide exponents incorrectly.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Dividing rational monomial expressions",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    for a, b in [(1, 2), (2, 3), (3, 4), (1, 4), (2, 5)]:
        #  a/(x-1) - b/(x-1) with different numerators
        n1, n2 = rng.randint(2, 6), rng.randint(1, 5)
        if n1 <= n2:
            n1, n2 = n2 + 1, n2
        diff = n1 - n2
        out.append(nr(
            f"Simplify $\\dfrac{{{n1}}}{{x - {a}}} - \\dfrac{{{n2}}}{{x - {a}}}$. "
            f"What is the numerator? Record the integer answer.",
            str(diff),
            f"$\\dfrac{{{n1}-{n2}}}{{x-{a}}} = \\dfrac{{{diff}}}{{x-{a}}}$.",
            "Students subtract denominators.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Subtracting rational expressions with common denominator",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # LCD addition with different denominators — MC for result
    lcd_cases = [
        ("\\dfrac{1}{x} + \\dfrac{1}{x+1}", "\\dfrac{2x+1}{x(x+1)}", "\\dfrac{2}{x+1}", "\\dfrac{1}{2x+1}", "\\dfrac{2x}{x+1}"),
        ("\\dfrac{2}{x-2} + \\dfrac{3}{x+2}", "\\dfrac{5x-10}{(x-2)(x+2)}", "\\dfrac{5}{x}", "\\dfrac{5x}{(x-2)(x+2)}", "\\dfrac{6}{x-2}"),
        ("\\dfrac{3}{x} - \\dfrac{1}{x+3}", "\\dfrac{2x+9}{x(x+3)}", "\\dfrac{2}{x+3}", "\\dfrac{3x-1}{x(x+3)}", "\\dfrac{2x}{x+3}"),
    ]
    for expr, correct, d1, d2, d3 in lcd_cases:
        out.append(mc(
            f"Which expression is equivalent to ${expr}$?",
            f"${correct}$",
            [f"${d1}$", f"${d2}$", f"${d3}$"],
            f"Use LCD and combine numerators: ${correct}$.",
            "Students add numerators without finding LCD.",
            topic=TOPIC, outcome_code="RF2",
            skill_tested="Adding rational expressions with different denominators",
            difficulty="Hard", estimated_time_seconds=110,
        ))

    # --- RF3: rational equations ---
    for a, b, sol in [(3, 6, 2), (4, 8, 2), (5, 10, 2), (2, 8, 4), (3, 9, 3),
                      (6, 12, 2), (4, 12, 3), (5, 15, 3), (2, 6, 3), (7, 14, 2)]:
        out.append(nr(
            f"Solve $\\dfrac{{{a}}}{{x}} = \\dfrac{{{b}}}{{x-1}}$ for $x$. "
            f"Record the integer solution.",
            str(sol),
            f"Cross-multiply: ${a}(x-1) = {b}x$. Solve: $x = {sol}$.",
            "Students forget to exclude $x = 0$ and $x = 1$ when checking.",
            topic=TOPIC, outcome_code="RF3",
            skill_tested="Solving rational equation reducing to linear",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for c, sol in [(6, 4), (12, 4), (8, 4), (10, 5), (15, 5), (9, 3), (16, 4)]:
        out.append(nr(
            f"Solve $\\dfrac{{x+2}}{{x}} = \\dfrac{{{c}}}{{x}}$ for $x \\ne 0$. "
            f"Record the integer solution.",
            str(sol),
            f"Multiply both sides by $x$: $x + 2 = {c}$, so $x = {sol}$.",
            "Students cancel $x$ incorrectly across terms.",
            topic=TOPIC, outcome_code="RF3",
            skill_tested="Solving simple rational equation with monomial denominator",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    # Quadratic result: (x-2)/(x-3) = 2 → x-2 = 2x-6 → x=4
    quad_cases = [
        (2, 3, 2, 4), (1, 4, 3, 5), (3, 5, 2, 7), (2, 5, 3, 9),
    ]
    for p, q, rhs, sol in quad_cases:
        out.append(nr(
            f"Solve $\\dfrac{{x-{p}}}{{x-{q}}} = {rhs}$ for $x \\ne {q}$. "
            f"Record the valid integer solution.",
            str(sol),
            f"$x - {p} = {rhs}(x - {q})$. Expand and solve: $x = {sol}$. Check $x \\ne {q}$.",
            "Students accept $x = {q}$ as a solution without checking.",
            topic=TOPIC, outcome_code="RF3",
            skill_tested="Solving rational equation that simplifies to linear",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for k, extraneous, valid in [(1, 2, 3), (2, 1, 4), (0, 1, 2)]:
        # 1/(x-1) + 1/(x+1) = ... simpler: x/(x-2) = 3 → x = 3x - 6 → -2x = -6 → x=3
        pass

    out.append(mc(
        f"Solve $\\dfrac{{x}}{{x-2}} = 3$ for $x \\ne 2$. Which solution is valid?",
        f"$x = 3$",
        [f"$x = 2$", f"$x = -3$", f"$x = 6$"],
        f"$x = 3( x-2) \\Rightarrow x = 3x - 6 \\Rightarrow x = 3$. $x = 2$ is non-permissible.",
        "Students accept the non-permissible value $x = 2$.",
        topic=TOPIC, outcome_code="RF3",
        skill_tested="Identifying valid solution of a rational equation",
        difficulty="Medium", estimated_time_seconds=85,
    ))

    for _ in range(6):
        m = rng.randint(2, 5)
        n = rng.randint(1, 4)
        # m/x = n/(x-1) → m(x-1)=nx → mx - m = nx → x(m-n) = m → x = m/(m-n)
        if m == n:
            continue
        sol = m / (m - n)
        if sol != int(sol) or sol in (0, 1):
            continue
        out.append(nr(
            f"Solve $\\dfrac{{{m}}}{{x}} = \\dfrac{{{n}}}{{x-1}}$ for $x$. "
            f"Record the integer solution.",
            str(int(sol)),
            f"Cross-multiply and solve: $x = {int(sol)}$.",
            "Distributing incorrectly when clearing denominators.",
            topic=TOPIC, outcome_code="RF3",
            skill_tested="Solving parameterized rational equation",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    return out
