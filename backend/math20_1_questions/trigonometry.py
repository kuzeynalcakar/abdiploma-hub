"""Programmatic Trigonometry questions (T1, T2, T3)."""

import math
import random
from math20_1_questions.helpers import mc, nr

TOPIC = "Trigonometry"

EXACT = {
    30: (0.5, math.sqrt(3) / 2, math.sqrt(3) / 3),
    45: (math.sqrt(2) / 2, math.sqrt(2) / 2, 1.0),
    60: (math.sqrt(3) / 2, 0.5, math.sqrt(3)),
}

QUADRANT_SIGNS = {
    1: ("+", "+", "+"),
    2: ("+", "-", "-"),
    3: ("-", "-", "+"),
    4: ("-", "+", "-"),
}


def _ref_angle(theta: int) -> int:
    t = theta % 360
    if t <= 90:
        return t
    if t <= 180:
        return 180 - t
    if t <= 270:
        return t - 180
    return 360 - t


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # T1 reference angles and quadrants
    for theta in [15, 25, 35, 55, 65, 75, 95, 105, 115, 125, 135, 145,
                  155, 165, 195, 205, 215, 225, 235, 245, 255, 265, 275,
                  285, 295, 305, 315, 325, 335, 345]:
        ref = _ref_angle(theta)
        q = 1 if theta <= 90 else 2 if theta <= 180 else 3 if theta <= 270 else 4
        out.append(nr(
            f"What is the reference angle for ${theta}^\\circ$ in standard position? "
            f"Record the answer in degrees as an integer.",
            str(ref),
            f"${theta}^\\circ$ is in Quadrant {q}. The reference angle is ${ref}^\\circ$.",
            "Students report the original angle instead of the acute reference angle.",
            topic=TOPIC, outcome_code="T1",
            skill_tested="Determining reference angle for angles in standard position",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for theta in [110, 130, 200, 250, 310, 140, 220, 320, 170, 190, 280, 100]:
        q = 1 if theta <= 90 else 2 if theta <= 180 else 3 if theta <= 270 else 4
        out.append(mc(
            f"In which quadrant does ${theta}^\\circ$ terminate?",
            f"Quadrant {q}",
            [f"Quadrant {((q % 4) + 1)}", f"Quadrant {((q + 1) % 4 + 1)}",
             f"Quadrant {((q + 2) % 4 + 1)}"],
            f"${theta}^\\circ$ lies between the axes defining Quadrant {q}.",
            "Using the reference angle to determine quadrant instead of the actual angle.",
            topic=TOPIC, outcome_code="T1",
            skill_tested="Identifying quadrant of an angle in standard position",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # T2 trig ratios from points
    points = [(3, 4), (5, 12), (8, 15), (7, 24), (-3, 4), (-5, 12), (3, -4),
              (-8, 15), (12, 5), (-7, 24), (9, 40), (-20, 21), (15, 8)]
    for x, y in points:
        r = math.hypot(x, y)
        sin_v = round(y / r, 4)
        cos_v = round(x / r, 4)
        tan_v = round(y / x, 4) if x != 0 else "undefined"
        out.append(nr(
            f"Point $P({x}, {y})$ lies on the terminal arm of angle $\\theta$ "
            f"in standard position. What is $\\sin\\theta$? "
            f"Express as a decimal rounded to four decimal places.",
            f"{sin_v:.4f}",
            f"$r = \\sqrt{{{x}^2 + {y}^2}} = {r:g}$. "
            f"$\\sin\\theta = \\frac{{y}}{{r}} = \\frac{{{y}}}{{{r:g}}} = {sin_v:.4f}$.",
            "Students use $\\frac{x}{r}$ for sine or forget the sign of $y$.",
            topic=TOPIC, outcome_code="T2",
            skill_tested="Calculating sine ratio from coordinates on terminal arm",
            difficulty="Medium", estimated_time_seconds=90,
        ))
        out.append(nr(
            f"For angle $\\theta$ in standard position with $P({x}, {y})$ on its terminal arm, "
            f"what is $\\cos\\theta$? Express as a decimal rounded to four decimal places.",
            f"{cos_v:.4f}",
            f"$\\cos\\theta = \\frac{{x}}{{r}} = {cos_v:.4f}$.",
            "Students use $\\frac{y}{r}$ for cosine.",
            topic=TOPIC, outcome_code="T2",
            skill_tested="Calculating cosine ratio from coordinates on terminal arm",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Exact values
    for ref, ratio in [(30, "sin"), (30, "cos"), (45, "sin"), (45, "cos"),
                       (60, "sin"), (60, "cos")]:
        s, c, t = EXACT[ref]
        val = s if ratio == "sin" else c
        for quad, sign_idx in [(2, 0), (3, 1), (4, 0)]:
            angle = {2: 180 - ref, 3: 180 + ref, 4: 360 - ref}[quad]
            signs = QUADRANT_SIGNS[quad]
            sign = signs[0 if ratio == "sin" else 1]
            actual = val if sign == "+" else -val
            label = f"\\{ratio}\\theta"
            out.append(nr(
                f"Determine the exact value of ${label}$ for $\\theta = {angle}^\\circ$ "
                f"without a calculator. Express as a decimal rounded to four decimal places.",
                f"{actual:.4f}",
                f"Reference angle is ${ref}^\\circ$. Quadrant {quad} gives "
                f"${label} = {sign}{val:g}$.",
                "Students forget to apply the correct sign for the quadrant.",
                topic=TOPIC, outcome_code="T2",
                skill_tested="Evaluating exact trigonometric ratios using reference angles",
                difficulty="Medium", estimated_time_seconds=95,
            ))

    # T3 sine and cosine laws
    triangles = [
        (7, 9, 40, "cosine"), (5, 8, 52, "cosine"), (6, 10, 35, "cosine"),
        (4, 6, 48, "cosine"), (8, 11, 115, "cosine"), (9, 12, 28, "cosine"),
        (10, 7, 33, "cosine"), (6, 9, 102, "cosine"),
    ]
    for a, b, angle_c, _ in triangles:
        c = math.sqrt(a ** 2 + b ** 2 - 2 * a * b * math.cos(math.radians(angle_c)))
        out.append(nr(
            f"In $\\triangle ABC$, $a = {a}$, $b = {b}$, and $\\angle C = {angle_c}^\\circ$. "
            f"Find side $c$ to the nearest tenth.",
            f"{c:.1f}",
            f"Cosine law: $c^2 = a^2 + b^2 - 2ab\\cos C$. "
            f"$c \\approx {c:.1f}$.",
            "Students use the sine law when only two sides and the included angle are known.",
            topic=TOPIC, outcome_code="T3",
            skill_tested="Applying cosine law to find a side length",
            difficulty="Medium", estimated_time_seconds=110,
        ))

    for a, angle_a, b, angle_b in [(8, 42, 6, 57), (10, 35, 7, 48), (12, 28, 9, 41),
                                    (7, 52, 9, 38), (11, 31, 8, 44), (9, 47, 6, 63)]:
        sin_a = math.sin(math.radians(angle_a))
        sin_b = math.sin(math.radians(angle_b))
        b_calc = a * sin_b / sin_a
        out.append(nr(
            f"In $\\triangle ABC$, $a = {a}$, $\\angle A = {angle_a}^\\circ$, "
            f"and $\\angle B = {angle_b}^\\circ$. Find side $b$ to the nearest tenth.",
            f"{b_calc:.1f}",
            f"Sine law: $\\frac{{a}}{{\\sin A}} = \\frac{{b}}{{\\sin B}}$, "
            f"so $b \\approx {b_calc:.1f}$.",
            "Students use the cosine law when two angles and one side are given.",
            topic=TOPIC, outcome_code="T3",
            skill_tested="Applying sine law to find a side length",
            difficulty="Medium", estimated_time_seconds=115,
        ))

    # Ambiguous case MC
    ambig = [
        ("A triangle has $a = 7$, $b = 10$, and $\\angle A = 30^\\circ$. "
         "How many possible triangles exist?",
         "Two", ["Zero", "One", "Infinitely many"],
         "SSA with $a < b$ and acute $\\angle A$ can produce two solutions.",
         "Assuming SSA always gives exactly one triangle.", "Hard", 130),
        ("A triangle has $a = 12$, $b = 8$, and $\\angle A = 120^\\circ$. "
         "How many triangles satisfy these conditions?",
         "One", ["Zero", "Two", "Infinitely many"],
         "With obtuse $\\angle A$ and $a > b$, exactly one triangle is possible.",
         "Applying the acute-angle ambiguous case rule incorrectly.", "Hard", 125),
        ("Which set of measurements could produce the ambiguous case (SSA)?",
         "$a = 5$, $b = 8$, $\\angle A = 40^\\circ$",
         ["$a = 5$, $b = 3$, $\\angle C = 90^\\circ$",
          "$a = 6$, $b = 6$, $\\angle C = 60^\\circ$",
          "$a = 7$, $b = 9$, $\\angle C = 55^\\circ$"],
         "SSA occurs with two sides and a non-included angle when $a < b$ and $\\angle A$ is acute.",
         "Confusing SSA with SAS or ASA cases.", "Hard", 120),
    ]
    for qt, ans, dist, expl, mis, diff, t in ambig:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code="T3",
                      skill_tested="Analyzing ambiguous case of sine law",
                      difficulty=diff, estimated_time_seconds=t))

    # CAST / sign MC
    sign_items = [
        ("Which ratio is positive in Quadrant III?",
         "$\\tan\\theta$",
         ["$\\sin\\theta$", "$\\cos\\theta$", "None of the ratios"],
         "Quadrant III: sine and cosine are negative; tangent is positive.",
         "Memorizing 'All Students Take Calculus' incorrectly.", "Easy", 55, "T2"),
        ("Which statement is true for $\\theta = 210^\\circ$?",
         "$\\sin\\theta < 0$ and $\\cos\\theta < 0$",
         ["$\\sin\\theta > 0$ and $\\cos\\theta > 0$",
          "$\\sin\\theta > 0$ and $\\cos\\theta < 0$",
          "$\\sin\\theta < 0$ and $\\cos\\theta > 0$"],
         "$210^\\circ$ is in Quadrant III where both sine and cosine are negative.",
         "Using the reference angle without applying quadrant signs.", "Medium", 75, "T2"),
        ("If $\\cos\\theta = -\\dfrac{3}{5}$ and $\\theta$ is in Quadrant II, "
         "what is the sign of $\\sin\\theta$?",
         "Positive",
         ["Negative", "Zero", "Cannot be determined"],
         "In Quadrant II, sine is positive while cosine is negative.",
         "Assuming both ratios share the same sign.", "Medium", 70, "T2"),
    ]
    for qt, ans, dist, expl, mis, diff, t, oc in sign_items:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                      skill_tested="Determining signs of trigonometric ratios by quadrant",
                      difficulty=diff, estimated_time_seconds=t))

    return out
