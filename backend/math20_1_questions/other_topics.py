"""Absolute Value, Reciprocal, Systems, and Inequalities (AN1, RF2, RF11, RF6, RF7, RF8)."""

import math
import random
from math20_1_questions.helpers import mc, nr

TOPIC_AV = "Absolute Value and Reciprocal Functions"
TOPIC_SYS = "Systems of Equations"
TOPIC_INEQ = "Linear and Quadratic Inequalities"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # AN1 / RF2 absolute value
    for a, b, c in [(2, 3, 7), (3, 2, 8), (2, -1, 5), (4, 1, 9), (2, 5, 11),
                    (3, -2, 4), (5, 1, 11), (2, -3, 5), (4, -1, 7), (3, 4, 10)]:
        # |ax + b| = c  => ax+b = c or ax+b = -c
        x1 = (c - b) / a
        x2 = (-c - b) / a
        larger = max(x1, x2)
        if larger != int(larger):
            continue
        out.append(nr(
            f"Solve $|{a}x + {b}| = {c}$ for $x$. What is the larger solution? "
            f"Record the integer answer.",
            str(int(larger)),
            f"${a}x + {b} = {c}$ gives $x = {x1:g}$; ${a}x + {b} = -{c}$ gives $x = {x2:g}$.",
            "Students find only one case of the absolute value equation.",
            topic=TOPIC_AV, outcome_code="RF2",
            skill_tested="Solving absolute value equation with two cases",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for a, b, c in [(1, 2, 3), (2, 1, 4), (1, -3, 2), (3, 2, 5), (2, -2, 6)]:
        # |ax + b| = c where c < 0 style - MC only
        if c <= 0:
            continue
        out.append(mc(
            f"How many real solutions does $|{a}x + {b}| = {c}$ have?",
            "Two",
            ["Zero", "One", "Infinitely many"],
            f"$|{a}x + {b}| = {c} > 0$ yields two linear equations.",
            "Assuming absolute value equations always have one solution.",
            topic=TOPIC_AV, outcome_code="RF2",
            skill_tested="Determining number of solutions to absolute value equation",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for a, b in [(2, 3), (1, -4), (3, 2), (2, -1), (4, 5)]:
        out.append(mc(
            f"The graph of $y = |{a}x + {b}|$ always opens:",
            "Upward (like $y = |x|$)",
            ["Downward", "To the right", "In both directions horizontally"],
            "Absolute value graphs have a V-shape opening upward.",
            "Confusing absolute value with quadratic opening direction.",
            topic=TOPIC_AV, outcome_code="RF2",
            skill_tested="Describing shape of absolute value graph",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    for m, b in [(2, 1), (-1, 3), (3, -2), (-2, 5), (1, 4)]:
        out.append(mc(
            f"Which is the vertex of $y = |{m}x + {b}|$?",
            f"The point where ${m}x + {b} = 0$",
            ["The y-intercept always", "The origin only",
             "Where the graph crosses $y = {b}$ only"],
            "The vertex occurs where the expression inside $| \\cdot |$ equals zero.",
            "Using the y-intercept as the vertex for all absolute value graphs.",
            topic=TOPIC_AV, outcome_code="RF2",
            skill_tested="Locating vertex of absolute value function",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    # RF11 reciprocal functions
    for a, b in [(1, 2), (2, 3), (1, -1), (3, 1), (2, -3), (4, 2), (1, 5), (3, -2)]:
        out.append(nr(
            f"For $f(x) = {a}x + {b}$, at what $x$-value does $y = \\dfrac{{1}}{{f(x)}}$ "
            f"have a vertical asymptote? Record the integer answer.",
            str(-b // a if a != 0 and (-b % a == 0) else int(-b / a)),
            f"Vertical asymptote where $f(x) = 0$: ${a}x + {b} = 0$, $x = {-b/a:g}$.",
            "Students set $f(x) = 1$ instead of $f(x) = 0$.",
            topic=TOPIC_AV, outcome_code="RF11",
            skill_tested="Finding vertical asymptote of reciprocal function",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for c in [2, 3, 4, 5, 6]:
        out.append(mc(
            f"The graph of $y = \\dfrac{{1}}{{x - {c}}}$ is the reciprocal of $y = x - {c}$. "
            f"Which line is a vertical asymptote?",
            f"$x = {c}$",
            [f"$y = {c}$", f"$x = 0$", f"$y = 0$"],
            f"The reciprocal is undefined when $x - {c} = 0$.",
            "Confusing horizontal and vertical asymptotes.",
            topic=TOPIC_AV, outcome_code="RF11",
            skill_tested="Identifying vertical asymptote of reciprocal function",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for a in [1, 2, -1, -2]:
        out.append(mc(
            f"Compared to $y = {a}x$, the graph of $y = \\dfrac{{1}}{{{a}x}}$ is:",
            "A hyperbola with vertical and horizontal asymptotes",
            ["A parabola opening upward",
             "A straight line through the origin",
             "A circle centered at the origin"],
            f"Reciprocal of a linear function produces a rectangular hyperbola.",
            "Assuming reciprocal graphs are always parabolas.",
            topic=TOPIC_AV, outcome_code="RF11",
            skill_tested="Describing graph of reciprocal of linear function",
            difficulty="Medium", estimated_time_seconds=70,
        ))

    # RF6 systems
    for m, b, p, q in [(1, 2, 1, -1), (2, 1, -1, 5), (1, 3, 2, -1), (3, 2, 1, 4),
                        (2, -1, 1, 3), (-1, 4, 2, 1), (1, 0, 2, 2), (2, 3, 1, 5)]:
        # y = mx + b and y = px + q  => mx+b = px+q => x(m-p) = q-b
        if m == p:
            continue
        x = (q - b) / (m - p)
        y = m * x + b
        if x != int(x) or y != int(y):
            continue
        x, y = int(x), int(y)
        out.append(nr(
            f"Solve the system: $y = {m}x + {b}$ and $y = {p}x + {q}$. "
            f"What is the $x$-coordinate of the intersection? Record the integer answer.",
            str(x),
            f"Set equal: ${m}x + {b} = {p}x + {q}$, $x = {x}$, $y = {y}$.",
            "Students substitute incorrectly and get the wrong coordinate.",
            topic=TOPIC_SYS, outcome_code="RF6",
            skill_tested="Solving linear system by substitution",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for a, b, c in [(1, 0, 0), (1, 2, 1), (2, 1, 3), (1, -1, 2), (3, 2, 5)]:
        # y = ax^2 + bx + c and y = mx + k
        m, k = 1, 0
        # x^2 = ax^2 + (b-m)x + (c-k) ... use simple: y=x and y=x^2-4 => x^2-x-4=0
        pass

    systems_quad = [
        (1, -4, "x^2 - 4", "y = x", 2, 2),  # x=2, y=2
        (1, -1, "x^2 - x", "y = 2x", 3, 6),
        (1, 0, "x^2", "y = 4", 2, 4),
        (1, -9, "x^2 - 9", "y = 0", 3, 0),
    ]
    for setup in [
        ("y = x^2 - 4", "y = x", 2, 2),
        ("y = x^2", "y = 4", 2, 4),
        ("y = x^2 - 9", "y = 0", 3, 0),
        ("y = x^2 - 1", "y = x + 1", 2, 3),
        ("y = x^2", "y = x + 2", 2, 4),
        ("y = x^2 - 5", "y = x + 1", None, None),  # skip if not integer
    ]:
        eq1, eq2, ex, ey = setup
        if ex is None:
            continue
        out.append(nr(
            f"Find the $x$-coordinate of an intersection point of the system "
            f"${eq1}$ and ${eq2}$ with positive $x$. Record the integer answer.",
            str(ex),
            f"Setting equal and solving gives $x = {ex}$, $y = {ey}$.",
            "Students find only one intersection when two exist.",
            topic=TOPIC_SYS, outcome_code="RF6",
            skill_tested="Finding intersection of linear and quadratic system",
            difficulty="Hard", estimated_time_seconds=130,
        ))

    for _ in range(8):
        out.append(mc(
            "How many points of intersection can a linear-quadratic system have?",
            "Zero, one, or two",
            ["Exactly one always", "Zero or one only", "Always two"],
            "A line can miss, touch, or cross a parabola at two points.",
            "Assuming every parabola and line intersect twice.",
            topic=TOPIC_SYS, outcome_code="RF6",
            skill_tested="Describing possible intersections of linear-quadratic system",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # RF7 / RF8 inequalities
    ineq_mc = [
        ("Which inequality represents the region above the line $y = 2x + 1$?",
         "$y > 2x + 1$",
         ["$y < 2x + 1$", "$y \\le 2x + 1$", "$x > 2y + 1$"],
         "Above the line means $y$-values are greater than those on the line.",
         "Reversing the inequality direction.", "RF7",
         "Interpreting linear inequality from region description", "Easy", 60),
        ("For $y > x^2 - 4$, which point is in the solution region?",
         "$(0, 0)$",
         ["$(0, -5)$", "$(3, 0)$", "$(0, -4)$"],
         "At $x=0$, need $y > -4$; $y=0$ satisfies this.",
         "Testing only the boundary, not strict inequality.", "RF7",
         "Using test point for quadratic inequality in two variables", "Medium", 80),
        ("A solid line is used on the boundary of an inequality when:",
         "The boundary points satisfy $\\le$ or $\\ge$",
         ["The region is unbounded", "The inequality is strict ($<$ or $>$)",
          "The line is horizontal"],
         "Solid lines include points where the expression equals zero.",
         "Using dashed lines for all inequalities.", "RF7",
         "Choosing solid vs broken boundary for inequality graph", "Easy", 55),
        ("Solve $x^2 - 5x + 6 > 0$ using a sign chart. Which interval is a solution?",
         "$x < 2$ or $x > 3$",
         ["$2 < x < 3$", "$x > 2$ only", "$x < 3$ only"],
         "Roots at $x=2,3$; parabola opens up, positive outside the roots.",
         "Selecting the interval between roots for an 'outside' inequality.", "RF8",
         "Solving quadratic inequality using sign analysis", "Medium", 95),
        ("Solve $x^2 - 4x + 4 \\le 0$. Which is the solution set?",
         "$x = 2$ only",
         ["$x \\le 2$", "$x \\ge 2$", "All real numbers"],
         "Perfect square $(x-2)^2 \\le 0$ only at $x = 2$.",
         "Treating $\\le 0$ the same as $< 0$.", "RF8",
         "Solving quadratic inequality with repeated root", "Hard", 110),
        ("For $(x - 1)(x + 3) < 0$, which interval satisfies the inequality?",
         "$-3 < x < 1$",
         ["$x < -3$ or $x > 1$", "$x > 1$ only", "$x < -3$ only"],
         "Product negative between roots $-3$ and $1$.",
         "Choosing outside intervals for a 'less than zero' product.", "RF8",
         "Solving quadratic inequality by roots and test points", "Medium", 90),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, t in ineq_mc:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_INEQ, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    # NR for inequality boundary values
    for r1, r2 in [(2, 3), (1, 4), (-2, 3), (0, 5), (-1, 2)]:
        # x^2 - (r1+r2)x + r1*r2 = 0 roots r1, r2
        b = -(r1 + r2)
        c = r1 * r2
        out.append(nr(
            f"Find the larger root of $x^2 + {b}x + {c} = 0$. "
            f"This root is a boundary point for related inequalities. Record the integer.",
            str(max(r1, r2)),
            f"Factor: $(x-{r1})(x-{r2})=0$; larger root $= {max(r1, r2)}$.",
            "Students confuse roots with interval endpoints direction.",
            topic=TOPIC_INEQ, outcome_code="RF8",
            skill_tested="Finding boundary roots for quadratic inequality",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    # AN1 absolute value distance
    for x1, x2 in [(3, 11), (-2, 5), (1, 8), (-4, 2), (6, 15), (-3, 7)]:
        dist = abs(x2 - x1)
        out.append(nr(
            f"What is the distance between ${x1}$ and ${x2}$ on a number line? "
            f"Record the integer answer.",
            str(dist),
            f"$|{x2} - ({x1})| = {dist}$.",
            "Students subtract in wrong order and report a negative distance.",
            topic=TOPIC_AV, outcome_code="RF2",
            skill_tested="Calculating distance between points using absolute value",
            difficulty="Easy", estimated_time_seconds=50,
        ))

    return out
