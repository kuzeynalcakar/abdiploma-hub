"""Programmatic Quadratic Functions (RF3, RF4) and Equations (RF1, RF5)."""

import math
import random
from math20_1_questions.helpers import mc, nr

TOPIC_FN = "Quadratic Functions"
TOPIC_EQ = "Quadratic Equations"


def _factor_pairs(n: int):
    pairs = []
    for i in range(1, int(math.isqrt(abs(n))) + 1):
        if n % i == 0:
            pairs.append((i, n // i))
            if i != n // i:
                pairs.append((n // i, i))
    return pairs


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # RF3 vertex form
    for _ in range(22):
        a = rng.choice([-3, -2, -1, 1, 2, 3])
        p = rng.randint(-5, 5)
        q = rng.randint(-8, 8)
        vx, vy = p, q
        out.append(nr(
            f"For $f(x) = {a}(x - ({p}))^2 + {q}$, what is the $x$-coordinate of the vertex? "
            f"Record the integer answer.",
            str(vx),
            f"Vertex form $y = a(x-p)^2 + q$ has vertex $({vx}, {vy})$.",
            "Students report the $y$-coordinate or use $-p$ incorrectly.",
            topic=TOPIC_FN, outcome_code="RF3",
            skill_tested="Identifying vertex x-coordinate from vertex form",
            difficulty="Easy", estimated_time_seconds=60,
        ))
        out.append(nr(
            f"For $g(x) = {a}(x + {abs(p)})^2 + {q}$ where the vertex is $({-p}, {q})$, "
            f"what is the $y$-coordinate of the vertex? Record the integer answer.",
            str(vy),
            f"In $a(x-p)^2+q$, the vertex is $({-p}, {q})$ so $y = {vy}$.",
            "Students confuse horizontal shift direction.",
            topic=TOPIC_FN, outcome_code="RF3",
            skill_tested="Identifying vertex y-coordinate from vertex form",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for a in [-2, -1, 1, 2, 3]:
        for p in [-4, -2, 1, 3, 5]:
            q = rng.randint(-6, 6)
            direction = "upward" if a > 0 else "downward"
            out.append(mc(
                f"The parabola $y = {a}(x - {p})^2 + {q}$ opens {direction}. "
                f"Which value determines the direction of opening?",
                f"$a = {a}$",
                [f"$p = {p}$", f"$q = {q}$", "The axis of symmetry only"],
                f"When $a > 0$ the parabola opens upward; when $a < 0$ it opens downward.",
                "Confusing vertical translation with direction of opening.",
                topic=TOPIC_FN, outcome_code="RF3",
                skill_tested="Relating leading coefficient to direction of opening",
                difficulty="Easy", estimated_time_seconds=55,
            ))

    # RF4 standard form / completing square
    for _ in range(20):
        a = rng.choice([1, 1, 1, 2, -1, -2])
        b = rng.randint(-10, 10)
        c = rng.randint(-12, 12)
        xv = -b / (2 * a)
        yv = a * xv ** 2 + b * xv + c
        disc = b ** 2 - 4 * a * c
        n_roots = 0 if disc < 0 else 1 if disc == 0 else 2
        out.append(nr(
            f"How many $x$-intercepts does $y = {a}x^2 + {b}x + {c}$ have? "
            f"Record $0$, $1$, or $2$.",
            str(n_roots),
            f"Discriminant $D = b^2 - 4ac = {disc}$. "
            f"{'No' if n_roots == 0 else 'One' if n_roots == 1 else 'Two'} real intercept(s).",
            "Students count the constant term as the number of intercepts.",
            topic=TOPIC_FN, outcome_code="RF4",
            skill_tested="Using discriminant to count x-intercepts of a quadratic",
            difficulty="Medium", estimated_time_seconds=85,
        ))
        out.append(nr(
            f"For $f(x) = {a}x^2 + {b}x + {c}$, the axis of symmetry is $x = k$. "
            f"What is $k$? Express as a decimal rounded to two decimal places.",
            f"{xv:.2f}",
            f"$x = -\\frac{{b}}{{2a}} = -\\frac{{{b}}}{{2({a})}} = {xv:.2f}$.",
            "Students use $\\frac{b}{2a}$ without the negative sign.",
            topic=TOPIC_FN, outcome_code="RF4",
            skill_tested="Calculating axis of symmetry from standard form",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # RF1 factoring
    for _ in range(30):
        r1 = rng.choice([i for i in range(-8, 9) if i != 0])
        r2 = rng.choice([i for i in range(-8, 9) if i != 0])
        b = -(r1 + r2)
        c = r1 * r2
        out.append(nr(
            f"Factor $x^2 + {b}x + {c}$. If the factored form is $(x - {r1})(x - {r2})$, "
            f"what is the product of the two roots? Record the integer answer.",
            str(r1 * r2),
            f"Roots are $x = {r1}$ and $x = {r2}$; product $= {r1 * r2}$.",
            "Students add roots instead of multiplying.",
            topic=TOPIC_EQ, outcome_code="RF1",
            skill_tested="Relating factored form to root product",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for a in [2, 3, -2]:
        added = 0
        attempts = 0
        while added < 4 and attempts < 40:
            attempts += 1
            r1 = rng.choice([i for i in range(-5, 6) if i != 0])
            r2 = rng.choice([i for i in range(-5, 6) if i != 0 and i != r1])
            b = -a * (r1 + r2)
            c = a * r1 * r2

            def _factor(r):
                if r > 0:
                    return f"$(x - {r})$"
                return f"$(x + {abs(r)})$"

            answer = _factor(r1)
            candidates = [
                _factor(r2),
                f"$(x + {abs(r1 + r2)})$",
                f"$(x - {abs(b)})$" if b != 0 else "$(x - 1)$",
                f"$(x + {abs(c)})$" if c != 0 else "$(x + 2)$",
                f"$(x - {abs(a)})$",
            ]
            distractors = []
            seen = {answer}
            for d in candidates:
                if d not in seen:
                    distractors.append(d)
                    seen.add(d)
                if len(distractors) == 3:
                    break
            if len(distractors) < 3:
                continue
            out.append(mc(
                f"Which is a factor of ${a}x^2 + {b}x + {c}$?",
                answer,
                distractors,
                f"${a}x^2 + {b}x + {c} = {a}(x-{r1})(x-{r2})$.",
                "Using sum of roots as a factor constant.",
                topic=TOPIC_EQ, outcome_code="RF1",
                skill_tested="Identifying linear factor of a quadratic trinomial",
                difficulty="Medium", estimated_time_seconds=85,
            ))
            added += 1

    # Difference of squares
    for a in [1, 2, 3, 4, 5]:
        sq = a ** 2
        out.append(mc(
            f"Which expression is equivalent to $x^2 - {sq}$?",
            f"$(x - {a})(x + {a})$",
            [f"$(x - {sq})^2$", f"$(x + {a})^2$", f"$(x - {a})^2 + {sq}$"],
            f"$x^2 - {sq} = x^2 - ({a})^2 = (x-{a})(x+{a})$.",
            "Treating difference of squares as a perfect square trinomial.",
            topic=TOPIC_EQ, outcome_code="RF1",
            skill_tested="Factoring difference of squares",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    # RF5 solving quadratics
    for _ in range(25):
        a = 1
        r1 = rng.randint(-7, 7)
        r2 = rng.randint(-7, 7)
        b = -(r1 + r2)
        c = r1 * r2
        out.append(nr(
            f"Solve $x^2 + {b}x + {c} = 0$. What is the larger root? Record the integer answer.",
            str(max(r1, r2)),
            f"Factoring: $(x-{r1})(x-{r2}) = 0$, roots $x = {r1}, {r2}$.",
            "Students report the smaller root or the sum of roots.",
            topic=TOPIC_EQ, outcome_code="RF5",
            skill_tested="Solving quadratic equation by factoring",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    for _ in range(18):
        a = rng.choice([1, 2, 1, 1])
        b = rng.randint(-8, 8)
        c = rng.randint(-10, 10)
        disc = b ** 2 - 4 * a * c
        if disc < 0:
            out.append(mc(
                f"How many real solutions does ${a}x^2 + {b}x + {c} = 0$ have?",
                "Zero",
                ["One", "Two", "Infinitely many"],
                f"$D = {b}^2 - 4({a})({c}) = {disc} < 0$.",
                "Students assume every quadratic has two real roots.",
                topic=TOPIC_EQ, outcome_code="RF5",
                skill_tested="Using discriminant to classify number of real roots",
                difficulty="Medium", estimated_time_seconds=80,
            ))
        elif disc == 0:
            root = -b / (2 * a)
            out.append(nr(
                f"Solve ${a}x^2 + {b}x + {c} = 0$. The repeated root is $x = r$. "
                f"What is $r$? Express as a decimal rounded to two decimal places.",
                f"{root:.2f}",
                f"$D = 0$; $x = \\frac{{-b}}{{2a}} = {root:.2f}$.",
                "Students factor incorrectly when the trinomial is a perfect square.",
                topic=TOPIC_EQ, outcome_code="RF5",
                skill_tested="Solving quadratic with zero discriminant",
                difficulty="Medium", estimated_time_seconds=90,
            ))
        else:
            r1 = (-b + math.sqrt(disc)) / (2 * a)
            r2 = (-b - math.sqrt(disc)) / (2 * a)
            out.append(nr(
                f"Using the quadratic formula on ${a}x^2 + {b}x + {c} = 0$, "
                f"find the smaller root. Express as a decimal rounded to two decimal places.",
                f"{min(r1, r2):.2f}",
                f"$x = \\frac{{-{b} \\pm \\sqrt{{{disc}}}}}{{2({a})}}$; smaller root $\\approx {min(r1, r2):.2f}$.",
                "Students forget the $\\pm$ and report only one root.",
                topic=TOPIC_EQ, outcome_code="RF5",
                skill_tested="Applying quadratic formula to find roots",
                difficulty="Medium", estimated_time_seconds=105,
            ))

    # Conceptual MC
    conceptual = [
        (TOPIC_FN, "RF3",
         "The graph of $y = (x - 3)^2 + 2$ is shifted from $y = x^2$ by:",
         "3 units right and 2 units up",
         ["3 units left and 2 units up", "3 units right and 2 units down",
          "2 units right and 3 units up"],
         "$(x-3)$ shifts right 3; $+2$ shifts up 2.",
         "Reversing horizontal shift direction.", "Easy", 60,
         "Identifying transformations in vertex form"),
        (TOPIC_FN, "RF4",
         "Completing the square on $y = 2x^2 + 8x + 5$ requires first:",
         "Factoring out 2 from the $x^2$ and $x$ terms",
         ["Dividing all terms by 5", "Adding 5 to both sides only",
          "Factoring out $x$ from every term"],
         "Factor $a$ from $ax^2+bx$ before completing the square when $a \\ne 1$.",
         "Forgetting to factor the leading coefficient.", "Medium", 85,
         "Explaining first step in completing the square"),
        (TOPIC_EQ, "RF5",
         "The roots of a quadratic equation correspond to:",
         "The $x$-intercepts of its graph",
         ["The $y$-intercept only", "The vertex coordinates",
          "The axis of symmetry value"],
         "Roots are $x$-values where $y = 0$, i.e., $x$-intercepts.",
         "Confusing vertex $x$-value with roots.", "Easy", 55,
         "Relating roots to x-intercepts of quadratic function"),
    ]
    for topic, oc, qt, ans, dist, expl, mis, diff, t, skill in conceptual:
        out.append(mc(qt, ans, dist, expl, mis, topic=topic, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    return out
