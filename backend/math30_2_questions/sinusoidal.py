"""Sinusoidal Functions — RF8."""

import math
import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Sinusoidal Functions"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # y = a sin(bx + c) + d — extract parameters
    param_cases = [
        (3, 1, 0, 5, 3, 6.28, 5),      # amplitude 3, period 2pi, midline 5
        (5, 2, 0, 10, 5, 3.14, 10),    # amplitude 5, period pi
        (2, 1, 0, -1, 2, 6.28, -1),    # midline -1
        (4, 0.5, 0, 0, 4, 12.57, 0),   # period 4pi
        (6, 1, 0, 12, 6, 6.28, 12),
        (1, 4, 0, 3, 1, 1.57, 3),
        (8, 0.25, 0, 20, 8, 25.13, 20),
        (7, 2, 0, -5, 7, 3.14, -5),
    ]
    for a, b, c, d, amp, period, mid in param_cases:
        out.append(nr(
            f"A sinusoidal function is $y = {a}\\sin({b}x + {c}) + {d}$. "
            f"What is the amplitude? Record the answer as an integer.",
            str(int(amp)),
            f"Amplitude $= |a| = {amp}$.",
            "Students report the midline value instead of amplitude.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Identifying amplitude from sinusoidal equation",
            difficulty="Easy", estimated_time_seconds=60,
        ))
        period_round = round(2 * math.pi / b, 2)
        out.append(nr(
            f"For $y = {a}\\sin({b}x + {c}) + {d}$, what is the period rounded to two decimal places?",
            f"{period_round:.2f}",
            f"Period $= \\dfrac{{2\\pi}}{{b}} = \\dfrac{{2\\pi}}{{{b}}} = {period_round:.2f}$.",
            "Students use $2\\pi b$ instead of $\\dfrac{{2\\pi}}{{b}}$.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Calculating period of a sinusoidal function",
            difficulty="Medium", estimated_time_seconds=80,
        ))
        out.append(nr(
            f"For $y = {a}\\sin({b}x + {c}) + {d}$, what is the midline (vertical shift)? "
            f"Record the integer answer.",
            str(int(mid)),
            f"Midline $= d = {mid}$.",
            "Students confuse midline with amplitude.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Identifying midline of a sinusoidal function",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # Max and min from a and d
    for a, d, mx, mn in [(4, 10, 14, 6), (3, 5, 8, 2), (6, -2, 4, -8), (5, 0, 5, -5),
                         (2, 15, 17, 13), (7, 3, 10, -4)]:
        out.append(nr(
            f"A sinusoidal model has amplitude ${a}$ and midline $y = {d}$. "
            f"What is the maximum value? Record the integer answer.",
            str(mx),
            f"Maximum $= d + a = {d} + {a} = {mx}$.",
            "Students report amplitude instead of maximum.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Calculating maximum from amplitude and midline",
            difficulty="Easy", estimated_time_seconds=60,
        ))
        out.append(nr(
            f"A sinusoidal model has amplitude ${a}$ and midline $y = {d}$. "
            f"What is the minimum value? Record the integer answer.",
            str(mn),
            f"Minimum $= d - a = {d} - {a} = {mn}$.",
            "Students compute $d + a$ for minimum.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Calculating minimum from amplitude and midline",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Evaluate sinusoidal function
    for a, b, d, x in [(3, 1, 5, 0), (3, 1, 5, 1.5708), (4, 2, 10, 0),
                       (5, 1, 0, 1.5708), (2, 1, 7, 3.1416), (6, 0.5, 4, 3.1416)]:
        y_val = round(a * math.sin(b * x) + d)
        out.append(nr(
            f"Evaluate $y = {a}\\sin({b}x) + {d}$ at $x = {round(x, 4)}$. "
            f"Round to the nearest integer.",
            str(y_val),
            f"$y = {a}\\sin({b} \\cdot {round(x,4)}) + {d} \\approx {y_val}$.",
            "Calculator in wrong angle mode (degrees vs radians).",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Evaluating sinusoidal function at a given radian input",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Contextual sinusoidal
    contexts = [
        ("A Ferris wheel seat height is $h(t) = 15\\sin\\!\\left(\\dfrac{\\pi}{6}t\\right) + 18$ metres. "
         "What is the amplitude in metres?", "15", "Amplitude is the coefficient of sine: 15."),
        ("A tide model is $d(t) = 2.5\\sin\\!\\left(\\dfrac{\\pi}{4}t\\right) + 6.5$ metres. "
         "What is the average depth (midline)?", "6.5", "Midline $= 6.5$ m."),
        ("Temperature is $T(t) = 8\\sin\\!\\left(\\dfrac{\\pi}{12}t - \\dfrac{\\pi}{2}\\right) + 18$ °C. "
         "What is the maximum temperature?", "26", "Max $= 18 + 8 = 26$."),
        ("A piston height is $h(t) = 6\\sin(4t) + 10$ cm. What is the minimum height?", "4",
         "Min $= 10 - 6 = 4$."),
        ("Daylight hours: $L(t) = 3.2\\sin\\!\\left(\\dfrac{2\\pi}{365}t\\right) + 12.4$. "
         "What is the amplitude?", "3.2", "Amplitude $= 3.2$ hours."),
    ]
    for q, ans, expl in contexts:
        out.append(nr(
            f"{q} Record the answer as a number.",
            ans,
            expl,
            "Students confuse amplitude with maximum value in context.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Interpreting sinusoidal parameter in context",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # Period from context
    period_contexts = [
        ("$h(t) = 10\\sin\\!\\left(\\dfrac{2\\pi}{5}t\\right) + 20$", 5, "Period $= \\dfrac{2\\pi}{2\\pi/5} = 5$."),
        ("$y = 4\\sin(3t) + 1$", round(2*math.pi/3, 2), "Period $= \\dfrac{2\\pi}{3}$."),
        ("$d(t) = 2\\sin\\!\\left(\\dfrac{\\pi}{8}t\\right) + 7$", 16, "Period $= 16$."),
        ("$T(t) = 6\\sin\\!\\left(\\dfrac{\\pi}{6}t\\right) + 15$", 12, "Period $= 12$."),
    ]
    for eq, period, expl in period_contexts:
        out.append(nr(
            f"A model is {eq}. What is the period? Round to two decimal places if needed.",
            f"{period:.2f}" if isinstance(period, float) else str(period),
            expl,
            "Students invert the frequency coefficient incorrectly.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Determining period from contextual sinusoidal model",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # MC conceptual
    mc_cases = [
        ("amplitude", "The distance from the midline to the maximum", "Half the peak-to-trough distance",
         "The horizontal shift", "The period length"),
        ("period", "The length of one complete cycle", "The vertical shift",
         "The maximum minus minimum", "The coefficient of $x$ inside sine"),
        ("midline", "The average or central value of the oscillation", "The maximum value",
         "The horizontal phase shift", "Twice the amplitude"),
    ]
    for term, correct, d1, d2, d3 in mc_cases:
        out.append(mc(
            f"Which description best defines the {term} of a sinusoidal function?",
            correct,
            [d1, d2, d3],
            f"The {term} is: {correct.lower()}.",
            f"Students confuse {term} with another sinusoidal characteristic.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested=f"Defining {term} of a sinusoidal function",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # Regression-style: given amplitude, period, midline — predict
    for a, d, x, y in [
        (4, 12, 1.5708, 16), (5, 8, 0, 8), (3, 20, 4.7124, 17),
        (6, 0, 1.5708, 6), (2, 10, 3.1416, 10),
    ]:
        y_val = round(a * math.sin(x) + d)
        out.append(nr(
            f"A sinusoidal model $y = {a}\\sin(x) + {d}$ models a quantity. "
            f"What is $y$ when $x = {round(x, 4)}$ radians? Round to nearest integer.",
            str(y_val),
            f"$y = {a}\\sin({round(x,4)}) + {d} \\approx {y_val}$.",
            "Using degrees instead of radians.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Predicting value from sinusoidal regression model",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for _ in range(8):
        a = rng.randint(2, 8)
        d = rng.randint(0, 15)
        mx = a + d
        out.append(nr(
            f"A monthly sales model has amplitude ${a}$ thousand dollars and midline "
            f"${d}$ thousand dollars. What is the peak monthly sales? Record the integer answer.",
            str(mx),
            f"Peak $= {d} + {a} = {mx}$ thousand dollars.",
            "Reporting amplitude instead of peak value.",
            topic=TOPIC, outcome_code="RF8",
            skill_tested="Applying amplitude and midline in sales context",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    return out
