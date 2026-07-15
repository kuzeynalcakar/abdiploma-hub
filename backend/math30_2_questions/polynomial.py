"""Polynomial Functions — RF7."""

import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Polynomial Functions"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # Given polynomial in factored or standard form — predict values
    for a, h, k, x in [
        (2, 1, 3, 4), (1, -2, 5, 0), (3, 0, -1, 2), (-1, 2, 8, 1),
        (0.5, 0, 4, 6), (2, 3, -2, 5),
    ]:
        y = a * (x - h) ** 2 + k
        out.append(nr(
            f"A quadratic model is $y = {a}(x - {h})^2 + {k}$. "
            f"What is $y$ when $x = {x}$? Record the answer as an integer.",
            str(int(round(y))),
            f"Substitute $x = {x}$: $y = {a}({x}-{h})^2 + {k} = {y:g}$.",
            "Students forget to square the bracketed term.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Evaluating a quadratic function model at a given input",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # Linear models y = mx + b
    for m, b, x in [
        (3, 5, 4), (2, -1, 6), (-1, 10, 3), (4, 0, 5),
        (1.5, 2, 4), (0.5, 3, 10), (6, -4, 2), (-2, 15, 4),
        (3, 7, 0), (5, -3, 3),
    ]:
        y = m * x + b
        out.append(nr(
            f"A linear model for data is $y = {m}x + {b}$. "
            f"What is the predicted $y$ when $x = {x}$? "
            f"Record the answer as an integer.",
            str(int(round(y))),
            f"$y = ({m})({x}) + {b} = {y:g}$.",
            "Students substitute into $x$ incorrectly.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Evaluating a linear regression model",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    # Cubic evaluation (degree 3)
    for a, b, c, d, x in [
        (1, -2, 1, 5, 2), (2, 0, -3, 1, 3), (1, 1, -4, 0, 4), (-1, 3, 0, 10, 1),
    ]:
        y = a * x**3 + b * x**2 + c * x + d
        out.append(nr(
            f"A cubic model is $y = {a}x^3 + {b}x^2 + {c}x + {d}$. "
            f"What is $y$ when $x = {x}$? Record the integer answer.",
            str(int(round(y))),
            f"Substitute: $y = {a}({x})^3 + {b}({x})^2 + {c}({x}) + {d} = {y:g}$.",
            "Sign errors when evaluating negative inputs.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Evaluating a cubic polynomial model",
            difficulty="Hard", estimated_time_seconds=100,
        ))

    # Degree identification
    for coeffs, degree in [
        ("3x^2 - 5x + 1", 2), ("-x^3 + 2x", 3), ("7x - 4", 1),
        ("x^4 - x^2 + 1", 4), ("-2x^3 + x^2 - 6", 3), ("5", 0),
        ("4x^2 + 9", 2), ("-6x^3 + 2x^2 - x + 1", 3),
    ]:
        if degree == 0:
            distractors = ["$1$", "$2$", "$-1$"]
        else:
            d1, d2, d3 = degree + 1, max(0, degree - 1), degree + 2
            opts = []
            for d in (d1, d2, d3):
                if d != degree and f"${d}$" not in opts:
                    opts.append(f"${d}$")
            while len(opts) < 3:
                extra = degree + len(opts) + 2
                if f"${extra}$" not in opts:
                    opts.append(f"${extra}$")
            distractors = opts[:3]
        out.append(mc(
            f"What is the degree of the polynomial $f(x) = {coeffs}$?",
            f"${degree}$",
            distractors,
            f"The highest exponent on $x$ is ${degree}$.",
            "Students confuse degree with number of terms.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Identifying degree of a polynomial function",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    # Intercepts from standard form
    for h, k in [(2, 5), (3, -4), (-1, 7), (4, 0), (-3, -2)]:
        # y = (x-h)^2 + k, y-intercept: x=0 → (0-h)^2 + k
        y_int = h ** 2 + k
        out.append(nr(
            f"A quadratic function is $y = (x - {h})^2 + {k}$. "
            f"What is the $y$-intercept? Record the integer answer.",
            str(y_int),
            f"Set $x = 0$: $y = (0-{h})^2 + {k} = {h**2} + {k} = {y_int}$.",
            "Students report the vertex instead of the $y$-intercept.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Finding y-intercept of a quadratic model",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    # Contextual polynomial problems
    contexts = [
        ("A ball's height is modelled by $h(t) = -5t^2 + 20t + 1$", 2, "metres"),
        ("Revenue is $R(n) = -2n^2 + 28n$", 5, "dollars"),
        ("Profit is $P(x) = -x^2 + 12x - 20$", 4, ""),
        ("Area is $A(w) = w(20 - w)$", 6, ""),
        ("Cost is $C(q) = 0.5q^2 + 3q + 10$", 4, ""),
    ]
    evaluators = {
        "h(t)": lambda v: -5 * v**2 + 20 * v + 1,
        "R(n)": lambda v: -2 * v**2 + 28 * v,
        "P(x)": lambda v: -v**2 + 12 * v - 20,
        "A(w)": lambda v: v * (20 - v),
        "C(q)": lambda v: 0.5 * v**2 + 3 * v + 10,
    }
    for qtext, var_val, unit in contexts:
        key = next(k for k in evaluators if k in qtext)
        ans = int(round(evaluators[key](var_val)))
        out.append(nr(
            f"{qtext}. Find the value when the input is ${var_val}$"
            f"{f' in {unit}' if unit else ''}. Record the integer answer.",
            str(ans),
            f"Substitute the input value to obtain ${ans}$.",
            "Arithmetic error when substituting into the model.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Applying polynomial model to a contextual problem",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Number of valid solutions in context
    for roots, valid, reject in [
        (2, 1, 1),  # two roots, one valid in context
    ]:
        out.append(mc(
            f"A rectangle's width $w$ satisfies $w(24 - w) = 80$. "
            f"The solutions are $w = 4$ and $w = 20$. If width must be less than 15 cm, "
            f"which value is valid in context?",
            f"$w = 4$",
            [f"$w = 20$", f"Both values", f"Neither value"],
            f"$w = 20$ exceeds the 15 cm constraint; only $w = 4$ is valid.",
            "Students accept all algebraic solutions without context check.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Rejecting invalid polynomial solution based on context",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for _ in range(10):
        m = rng.randint(1, 5)
        b = rng.randint(-5, 10)
        x = rng.randint(1, 8)
        y = m * x + b
        out.append(nr(
            f"Data is modelled by $y = {m}x + {b}$. Predict $y$ when $x = {x}$. "
            f"Record the integer answer.",
            str(y),
            f"$y = {m}({x}) + {b} = {y}$.",
            "Using rounded slope from a graph instead of given model.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Interpolating with a given linear model",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for a, b, c in [(1, -6, 9), (1, -4, 4), (1, -10, 25), (2, -8, 8), (1, 0, 0)]:
        # perfect square vertex form detection
        h = -b / (2 * a) if a != 0 else 0
        if h != int(h):
            continue
        k = int(a * h * h + b * h + c)
        out.append(mc(
            f"Which vertex form matches $y = {a}x^2 + {b}x + {c}$?",
            f"$y = {a}(x - {int(h)})^2 + {k}$",
            [
                f"$y = {a}(x + {int(h)})^2 + {k}$",
                f"$y = (x - {int(h)})^2 + {k}$",
                f"$y = {a}(x - {int(h)})^2 - {k}$",
            ],
            f"Complete the square: vertex $({int(h)}, {k})$.",
            "Sign error in horizontal shift when converting to vertex form.",
            topic=TOPIC, outcome_code="RF7",
            skill_tested="Relating standard and vertex form of quadratic model",
            difficulty="Hard", estimated_time_seconds=105,
        ))

    return out
