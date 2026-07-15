"""Additional diverse Math 30-2 questions to expand the pool with unique templates."""

import math
import random
from math30_2_questions.helpers import mc, nr

TOPICS = {
    "set": "Set Theory and Logic",
    "count": "Counting Methods",
    "prob": "Probability",
    "rat": "Rational Expressions and Equations",
    "poly": "Polynomial Functions",
    "explog": "Exponential and Logarithmic Functions",
    "sin": "Sinusoidal Functions",
}


def _comb(n: int, r: int) -> int:
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # LR2 — complement count
    for u, in_a, in_b, both in [
        (95, 40, 35, 12), (130, 55, 48, 20), (175, 70, 62, 28),
        (210, 88, 74, 31), (65, 28, 25, 9),
    ]:
        neither = u - (in_a + in_b - both)
        out.append(nr(
            f"A festival sold ${u}$ wristbands. ${in_a}$ holders attended the concert stage, "
            f"${in_b}$ attended the art exhibit, and ${both}$ attended both. "
            f"How many wristband holders used neither venue? Record the integer answer.",
            str(neither),
            f"Union $= {in_a + in_b - both}$. Neither $= {u} - {in_a + in_b - both} = {neither}$.",
            "Adding stage and exhibit counts without removing overlap.",
            topic=TOPICS["set"], outcome_code="LR2",
            skill_tested=f"Finding neither-region count in festival survey ({u} total)",
            difficulty="Medium", estimated_time_seconds=88,
        ))

    # LR1 — tile pattern
    for start, diff, n, label in [
        (4, 5, 7, "blue"), (11, 3, 9, "red"), (7, 6, 6, "green"),
    ]:
        ans = start + (n - 1) * diff
        out.append(nr(
            f"A {label} tile pattern uses ${start}$ tiles in row 1 and adds ${diff}$ tiles "
            f"each new row. How many tiles are in row ${n}$? Record the integer answer.",
            str(ans),
            f"Row ${n}$: ${start} + ({n}-1)({diff}) = {ans}$.",
            "Multiplying row number by the increment instead of using an arithmetic sequence.",
            topic=TOPICS["set"], outcome_code="LR1",
            skill_tested=f"Predicting tile count in row {n} of a growing pattern",
            difficulty="Easy", estimated_time_seconds=72,
        ))

    # P4 — license plates with restriction
    plate_cases = [
        (26, 25, 10, 10, "no repeated first letter"),
        (26, 26, 10, 10, "letters may repeat"),
        (20, 20, 9, 9, "restricted alphabet and digits"),
    ]
    for l1, l2, d1, d2, case in plate_cases:
        ans = l1 * l2 * d1 * d2
        out.append(nr(
            f"A licence plate has 2 letter positions followed by 2 digit positions "
            f"({case}). The letter pools have ${l1}$ and ${l2}$ choices; digit pools have "
            f"${d1}$ and ${d2}$ choices. How many plates are possible? Record the integer answer.",
            str(ans),
            f"FCP: ${l1} \\times {l2} \\times {d1} \\times {d2} = {ans}$.",
            "Multiplying only letter positions and ignoring digits.",
            topic=TOPICS["count"], outcome_code="P4",
            skill_tested=f"FCP licence plate count ({case})",
            difficulty="Medium", estimated_time_seconds=82,
        ))

    # P5 — seating circle treated as linear (Alberta scope: not circular perm)
    for n in [6, 7, 9]:
        ans = math.factorial(n)
        out.append(nr(
            f"${n}$ distinct trophies are displayed in a row on a shelf. "
            f"In how many orders can they be arranged? Record the integer answer.",
            str(ans),
            f"Linear arrangement: ${n}! = {ans}$.",
            "Using circular permutation formula not required in Math 30-2.",
            topic=TOPICS["count"], outcome_code="P5",
            skill_tested=f"Arranging {n} distinct objects in a row",
            difficulty="Easy", estimated_time_seconds=68,
        ))

    # P6 — choosing committees with gender split wording variant
    for women, men, rw, rm in [(6, 8, 2, 3), (5, 7, 3, 2), (8, 6, 4, 1)]:
        ans = _comb(women, rw) * _comb(men, rm)
        out.append(nr(
            f"A task force needs ${rw}$ women from ${women}$ candidates and ${rm}$ men from "
            f"${men}$ candidates. How many task forces are possible? Record the integer answer.",
            str(ans),
            f"$_{{{rw}}}C_{{{women}}} \\times $_{{{rm}}}C_{{{men}}} = {ans}$.",
            "Adding the two combination counts instead of multiplying.",
            topic=TOPICS["count"], outcome_code="P6",
            skill_tested=f"Committee selection {rw}+{rm} from split candidate pools",
            difficulty="Hard", estimated_time_seconds=102,
        ))

    # P1 — odds against
    for fav, against in [(2, 7), (5, 3), (1, 8), (4, 5)]:
        p = round(fav / (fav + against), 4)
        out.append(nr(
            f"The odds in favour of making the playoffs are ${fav}:{against}$. "
            f"What is the probability of making the playoffs? Express as a decimal to four places.",
            f"{p:.4f}",
            f"$P = \\dfrac{{{fav}}}{{{fav}+{against}}} = {p:.4f}$.",
            "Using odds against values in the numerator.",
            topic=TOPICS["prob"], outcome_code="P1",
            skill_tested=f"Playoff probability from {fav}:{against} odds",
            difficulty="Easy", estimated_time_seconds=68,
        ))

    # P2 — only A region probability
    for pa, pb, pab in [(0.42, 0.38, 0.12), (0.55, 0.33, 0.18), (0.28, 0.49, 0.09)]:
        only_a = round(pa - pab, 2)
        out.append(nr(
            f"Students: $P(\\text{{plays soccer}})={pa}$, $P(\\text{{plays basketball}})={pb}$, "
            f"$P(\\text{{plays both}})={pab}$. What is $P(\\text{{soccer only}})$? Express as a decimal.",
            f"{only_a:.2f}",
            f"$P(\\text{{soccer only}}) = {pa} - {pab} = {only_a}$.",
            "Reporting $P(\\text{{soccer}})$ instead of soccer-only probability.",
            topic=TOPICS["prob"], outcome_code="P2",
            skill_tested=f"Finding soccer-only probability from joint data",
            difficulty="Medium", estimated_time_seconds=84,
        ))

    # P3 — drawing without replacement (different context)
    for red, total in [(4, 10), (5, 12), (3, 8)]:
        blue = total - red
        p = round((red / total) * ((red - 1) / (total - 1)), 4)
        out.append(nr(
            f"A jar has ${red}$ red and ${blue}$ blue marbles. Two marbles are drawn without "
            f"replacement. What is the probability both are red? Express as a decimal to four places.",
            f"{p:.4f}",
            f"$\\dfrac{{{red}}}{{{total}}} \\times \\dfrac{{{red-1}}}{{{total-1}}} = {p:.4f}$.",
            "Treating the second draw as independent.",
            topic=TOPICS["prob"], outcome_code="P3",
            skill_tested=f"Two-draw without replacement from {total} marbles",
            difficulty="Hard", estimated_time_seconds=98,
        ))

    # RF1 — simplify numeric rational
    for n, d, simp in [(18, 6, 3), (24, 8, 3), (15, 5, 3), (20, 4, 5)]:
        out.append(nr(
            f"Simplify $\\dfrac{{{n}x^2}}{{{d}x}}$ for $x \\ne 0$. "
            f"What is the coefficient of $x$? Record the integer answer.",
            str(simp),
            f"$\\dfrac{{{n}x^2}}{{{d}x}} = {simp}x$.",
            "Subtracting exponents incorrectly.",
            topic=TOPICS["rat"], outcome_code="RF1",
            skill_tested=f"Simplifying monomial rational {n}x^2/{d}x",
            difficulty="Easy", estimated_time_seconds=62,
        ))

    # RF3 — rational equation variant
    for a, b, sol in [(4, 12, 3), (3, 9, 3), (5, 15, 3), (6, 18, 3)]:
        out.append(nr(
            f"Solve $\\dfrac{{{a}}}{{x-1}} = \\dfrac{{{b}}}{{x}}$ for $x \\ne 0, 1$. "
            f"Record the integer solution.",
            str(sol),
            f"Cross-multiply: ${a}x = {b}(x-1)$ gives $x = {sol}$.",
            "Cross-multiplying incorrectly across denominators.",
            topic=TOPICS["rat"], outcome_code="RF3",
            skill_tested=f"Solving proportion {a}/(x-1) = {b}/x",
            difficulty="Medium", estimated_time_seconds=92,
        ))

    # RF7 — quadratic revenue
    for p, rev in [(10, 0), (8, 96), (6, 96), (4, 96)]:
        out.append(nr(
            f"Revenue from price $p$ is $R(p) = p(12 - p)$ dollars. Find $R({p})$. Record the integer answer.",
            str(rev),
            f"$R({p}) = {p}(12-{p}) = {rev}$.",
            "Using $12-p$ without multiplying by price.",
            topic=TOPICS["poly"], outcome_code="RF7",
            skill_tested=f"Evaluating quadratic revenue at price ${p}",
            difficulty="Medium", estimated_time_seconds=78,
        ))

    # RF4 — expand log
    for a, b in [(10, 1000), (2, 8), (3, 27), (5, 125)]:
        out.append(mc(
            f"Which equals $\\log({b})$ using the power law?",
            f"$3\\log({a})$",
            [f"$\\log({a}) + 3$", f"$3 + \\log({a})$", f"$\\log({a + b})$"],
            f"$\\log({b}) = \\log({a}^3) = 3\\log({a})$.",
            "Adding 3 to log instead of multiplying.",
            topic=TOPICS["explog"], outcome_code="RF4",
            skill_tested=f"Rewriting log({b}) with power law",
            difficulty="Easy", estimated_time_seconds=64,
        ))

    # RF5 — exponential
    for base, exp, rhs in [(3, "x", 81), (2, "x+2", 32), (5, "x", 125)]:
        if exp == "x":
            sol = int(round(math.log(rhs, base)))
        else:
            offset = int(exp.replace("x", "").replace("+", ""))
            sol = int(round(math.log(rhs, base) - offset))
        out.append(nr(
            f"Solve ${base}^{{{exp}}} = {rhs}$ for $x$. Record the integer answer.",
            str(sol),
            f"Rewrite ${rhs} = {base}^{{{sol}}}$ and equate exponents.",
            "Dividing bases instead of equating exponents.",
            topic=TOPICS["explog"], outcome_code="RF5",
            skill_tested=f"Solving {base}^({exp}) = {rhs}",
            difficulty="Medium", estimated_time_seconds=86,
        ))

    # RF6 — compound interest variant
    for principal, rate, years in [(2500, 0.045, 4), (1200, 0.07, 5), (800, 0.055, 6)]:
        ans = round(principal * (1 + rate) ** years)
        out.append(nr(
            f"An account with $\\${principal}$ earns ${rate*100:g}\\%$ compounded annually. "
            f"What is the balance after ${years}$ years? Round to the nearest dollar.",
            str(ans),
            f"${principal}(1+{rate})^{years} \\approx {ans}$.",
            "Using simple interest over multiple years.",
            topic=TOPICS["explog"], outcome_code="RF6",
            skill_tested=f"Compound balance on ${principal} after {years} years",
            difficulty="Medium", estimated_time_seconds=88,
        ))

    # RF8 — period from context
    for coeff, period in [(2, 6.28), (4, 3.14), (0.5, 12.57)]:
        pr = round(2 * math.pi / coeff, 2)
        out.append(nr(
            f"A model is $y = 5\\sin({coeff}t) + 11$. What is the period? Round to two decimal places.",
            f"{pr:.2f}",
            f"Period $= 2\\pi/{coeff} = {pr:.2f}$.",
            "Multiplying by $2\\pi$ instead of dividing.",
            topic=TOPICS["sin"], outcome_code="RF8",
            skill_tested=f"Period of 5sin({coeff}t)+11 model",
            difficulty="Medium", estimated_time_seconds=82,
        ))

    # RF8 — peak from context
    for amp, mid in [(9, 14), (12, 3), (6, 22)]:
        out.append(nr(
            f"A seasonal sales model has amplitude ${amp}$ (thousand units) and midline ${mid}$. "
            f"What is the peak sales level? Record the integer answer.",
            str(amp + mid),
            f"Peak $= {mid} + {amp} = {amp + mid}$.",
            "Reporting amplitude instead of peak value.",
            topic=TOPICS["sin"], outcome_code="RF8",
            skill_tested=f"Peak sales from amplitude {amp} and midline {mid}",
            difficulty="Easy", estimated_time_seconds=62,
        ))

    return out
