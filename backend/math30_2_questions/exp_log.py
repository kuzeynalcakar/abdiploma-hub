"""Exponential and Logarithmic Functions — RF4, RF5, RF6."""

import math
import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Exponential and Logarithmic Functions"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- RF4: logarithms and laws ---
    for val, result in [
        (1000, 3), (100, 2), (10000, 4), (10, 1), (1, 0), (0.1, -1),
        (0.01, -2), (100000, 5), (0.001, -3), (1000000, 6),
    ]:
        out.append(nr(
            f"Evaluate $\\log_{{10}}({val})$. Record the integer answer.",
            str(result),
            f"$10^{{{result}}} = {val}$, so $\\log_{{10}}({val}) = {result}$.",
            "Students confuse log with square root.",
            topic=TOPIC, outcome_code="RF4",
            skill_tested="Evaluating common logarithm of a power of ten",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    for a, b, prod, log_prod in [(2, 3, 6, 0.7782), (4, 5, 20, 1.3010), (3, 7, 21, 1.3222)]:
        out.append(mc(
            f"Which is equivalent to $\\log({a}) + \\log({b})$?",
            f"$\\log({prod})$",
            [f"$\\log({a+b})$", f"$\\log({a})^{b}$", f"$\\log({a}) \\cdot \\log({b})$"],
            f"Product law: $\\log({a}) + \\log({b}) = \\log({a} \\cdot {b}) = \\log({prod})$.",
            "Students add arguments instead of multiplying.",
            topic=TOPIC, outcome_code="RF4",
            skill_tested="Applying product law of logarithms",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for num, den, quot in [(100, 10, 10), (1000, 100, 10), (50, 5, 10), (8, 2, 4)]:
        out.append(mc(
            f"Which is equivalent to $\\log({num}) - \\log({den})$?",
            f"$\\log({quot})$",
            [f"$\\log({num - den})$", f"$\\log\\!\\left(\\dfrac{{{den}}}{{{num}}}\\right)$",
             f"$\\dfrac{{\\log({num})}}{{\\log({den})}}$"],
            f"Quotient law: $\\log({num}) - \\log({den}) = \\log\\!\\left(\\dfrac{{{num}}}{{{den}}}\\right) = \\log({quot})$.",
            "Students subtract arguments instead of dividing.",
            topic=TOPIC, outcome_code="RF4",
            skill_tested="Applying quotient law of logarithms",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    for base, exp, coeff in [(2, 3, 3), (3, 2, 2), (5, 4, 4), (2, 5, 5), (10, 2, 2)]:
        out.append(nr(
            f"Rewrite $\\log({base}^{{{exp}}})$ as an integer coefficient times $\\log({base})$.",
            str(coeff),
            f"Power law: $\\log({base}^{{{exp}}}) = {exp}\\log({base})$.",
            "Students evaluate as ${base}^{exp}$ inside the log incorrectly.",
            topic=TOPIC, outcome_code="RF4",
            skill_tested="Applying power law of logarithms",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for y, b in [(8, 2), (27, 3), (64, 4), (125, 5), (216, 6)]:
        out.append(mc(
            f"If $\\log_b({y}) = 3$, what is $b$?",
            f"${b}$",
            [f"${y}$", f"${y - 3}$", f"${b + 1}$"],
            f"$b^3 = {y}$, so $b = {int(y ** (1/3))}$.",
            "Students confuse base with argument.",
            topic=TOPIC, outcome_code="RF4",
            skill_tested="Interpreting logarithmic definition to find base",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # --- RF5: exponential equations ---
    exp_cases = [
        (2, "x+1", 16, "x+1", 4, 3),
        (2, "x", 32, "5", 5, 5),
        (3, "x", 9, "2", 2, 2),
        (2, "2x", 64, "6", 3, 3),
        (5, "x", 25, "2", 2, 2),
        (2, "x-1", 8, "3", 3, 4),
        (4, "x", 64, "3", 3, 3),
    ]
    for base, lhs_exp, rhs_val, rhs_exp, rhs_exp_val, sol in exp_cases:
        if sol != int(sol):
            out.append(nr(
                f"Solve ${base}^{{{lhs_exp}}} = {rhs_val}$ for $x$. "
                f"Express as a decimal to one decimal place.",
                f"{sol:.1f}",
                f"${rhs_val} = {base}^{{{rhs_exp}}}$. Equate exponents: "
                f"${lhs_exp} = {rhs_exp_val}$, so $x = {sol}$.",
                "Students divide bases instead of equating exponents.",
                topic=TOPIC, outcome_code="RF5",
                skill_tested="Solving exponential equation with common base",
                difficulty="Medium", estimated_time_seconds=85,
            ))
        else:
            out.append(nr(
                f"Solve ${base}^{{{lhs_exp}}} = {rhs_val}$ for $x$. Record the integer answer.",
                str(int(sol)),
                f"${rhs_val} = {base}^{{{rhs_exp}}}$. Equate exponents: $x = {int(sol)}$.",
                "Students take log of both sides when bases already match.",
                topic=TOPIC, outcome_code="RF5",
                skill_tested="Solving exponential equation with common base",
                difficulty="Medium", estimated_time_seconds=85,
            ))

    for a, b, x, y in [(3, 81, 4, 81), (2, 16, 4, 16), (5, 625, 4, 625), (2, 8, 3, 8)]:
        out.append(nr(
            f"Solve ${a}^x = {b}$ for $x$. Record the integer answer.",
            str(int(math.log(b, a))),
            f"${b} = {a}^{{{int(math.log(b, a))}}}$, so $x = {int(math.log(b, a))}$.",
            "Students guess exponents without systematic comparison.",
            topic=TOPIC, outcome_code="RF5",
            skill_tested="Solving exponential equation by rewriting as power",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # --- RF6: exponential/log applications ---
    for p0, rate, t in [
        (500, 0.06, 5), (1000, 0.04, 3), (200, 0.08, 4),
        (800, 0.05, 6), (1500, 0.03, 10),
    ]:
        ans = round(p0 * (1 + rate) ** t)
        out.append(nr(
            f"A population of ${p0}$ grows at ${rate * 100:g}\\%$ per year under "
            f"$P(t) = {p0}(1 + {rate})^t$. What is $P({t})$ rounded to the nearest whole number?",
            str(ans),
            f"$P({t}) = {p0}(1 + {rate})^{t} \\approx {ans}$.",
            "Students use simple interest instead of compound growth.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Evaluating exponential growth model",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for p0, rate, t in [(1000, 0.12, 3), (500, 0.08, 4), (2000, 0.05, 6)]:
        ans = round(p0 * (1 - rate) ** t)
        out.append(nr(
            f"A car worth $\\${p0}$ depreciates at ${rate * 100:g}\\%$ per year under "
            f"$V(t) = {p0}(1 - {rate})^t$. What is $V({t})$ rounded to the nearest dollar?",
            str(ans),
            f"$V({t}) = {p0}(1 - {rate})^{t} \\approx {ans}$.",
            "Students add depreciation rate instead of multiplying decay factor.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Evaluating exponential decay model",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Given model predict
    for a, b, x in [(100, 1.5, 4), (50, 2, 3), (200, 1.08, 5), (80, 1.25, 4), (120, 1.1, 6)]:
        y = round(a * b ** x, 2)
        out.append(nr(
            f"An exponential model is $y = {a} \\cdot ({b})^x$. "
            f"What is $y$ when $x = {x}$? Round to the nearest hundredth.",
            f"{y:.2f}",
            f"$y = {a} \\cdot {b}^{x} = {y:.2f}$.",
            "Students multiply by $x$ instead of exponentiating.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Evaluating given exponential function model",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for m, c, x in [(3, 2, 10), (2, 5, 100), (4, 1, 16), (1, 0, 1000)]:
        val = round(m * math.log10(x) + c, 2)
        out.append(nr(
            f"A logarithmic model is $y = {m}\\log(x) + {c}$. "
            f"What is $y$ when $x = {x}$? Round to two decimal places.",
            f"{val:.2f}",
            f"$y = {m}\\log({x}) + {c} = {val:.2f}$.",
            "Students use natural log instead of common log.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Evaluating logarithmic function model",
            difficulty="Hard", estimated_time_seconds=95,
        ))

    half_life = [
        (100, 0.5, 3, 12.5), (200, 0.5, 2, 50), (80, 0.5, 4, 5),
    ]
    for init, factor, periods, remaining in half_life:
        out.append(nr(
            f"A substance starts at ${init}$ g and loses half its mass each period. "
            f"How many grams remain after ${periods}$ periods? Record the answer.",
            f"{remaining:.1f}" if remaining != int(remaining) else str(int(remaining)),
            f"${init} \\times ({factor})^{periods} = {remaining}$.",
            "Students subtract half each time instead of multiplying.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Applying repeated halving exponential model",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for _ in range(8):
        p0 = rng.choice([100, 200, 500, 1000])
        r = round(rng.choice([0.03, 0.04, 0.05, 0.06, 0.08]), 2)
        t = rng.randint(2, 6)
        result = round(p0 * (1 + r) ** t)
        out.append(nr(
            f"An investment of $\\${p0}$ earns ${r*100}\\%$ compounded annually. "
            f"What is the value after ${t}$ years? Round to the nearest dollar.",
            str(result),
            f"${p0}(1.{int(r*100):02d})^{t} \\approx {result}$.",
            "Using linear growth $P_0(1 + rt)$ instead of compound.",
            topic=TOPIC, outcome_code="RF6",
            skill_tested="Calculating compound growth over multiple periods",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    return out
