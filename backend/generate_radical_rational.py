"""Generate and validate 50 radical/rational questions. Run once, output JSON."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.database.question_validator import validate_question
from question_tools import assert_mc_position_balanced, format_position_report, shuffle_mc_choices

DB = Path(__file__).parent / "albertaprep.db"


def mc(qtext, answer, distractors, explanation, mistake, **meta):
    choices = [{"text": answer, "is_correct": True}]
    for d in distractors:
        choices.append({"text": d, "is_correct": False})
    choices = shuffle_mc_choices(choices)
    return {
        "course_code": "MATH30-1",
        "unit": "Relations and Functions",
        "question_type": "Multiple Choice",
        "choices": choices,
        "question_text": qtext,
        "answer": answer,
        "explanation": explanation,
        "common_mistake": mistake,
        "source": "ai",
        **meta,
    }


def nr(qtext, answer, explanation, mistake, **meta):
    return {
        "course_code": "MATH30-1",
        "unit": "Relations and Functions",
        "question_type": "Numerical Response",
        "choices": [],
        "question_text": qtext,
        "answer": str(answer),
        "explanation": explanation,
        "common_mistake": mistake,
        "source": "ai",
        **meta,
    }


def wr(qtext, answer, explanation, mistake, **meta):
    return {
        "course_code": "MATH30-1",
        "unit": "Relations and Functions",
        "question_type": "Written Response",
        "choices": [],
        "question_text": qtext,
        "answer": answer,
        "explanation": explanation,
        "common_mistake": mistake,
        "source": "ai",
        **meta,
    }


RADICAL = []

# --- 15 MC Radical (8E, 7M, 5H approx -> 5E, 7M, 3H for first batch, adjust in full list)
RADICAL += [
    mc(
        "What is the domain of $f(x) = \\sqrt{x - 5}$ in interval notation?",
        "$[5, \\infty)$",
        ["$(-\\infty, 5]$", "$(5, \\infty)$", "$\\mathbb{R}$"],
        "The expression under the square root must satisfy $x - 5 \\ge 0$, so $x \\ge 5$. In interval notation the domain is $[5, \\infty)$.",
        "Students sometimes reverse the inequality and write $(-\\infty, 5]$ or forget that the endpoint is included.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Determining domain of a square root function",
        difficulty="Easy", estimated_time_seconds=75,
    ),
    mc(
        "What is the range of $g(x) = -\\sqrt{x} + 3$?",
        "$(-\\infty, 3]$",
        ["$[0, \\infty)$", "$[3, \\infty)$", "$(-\\infty, \\infty)$"],
        "The square root outputs values in $[0, \\infty)$. After multiplying by $-1$ and adding $3$, outputs satisfy $y \\le 3$, so the range is $(-\\infty, 3]$.",
        "Students may forget the reflection and report $[3, \\infty)$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Determining range after vertical reflection and translation",
        difficulty="Easy", estimated_time_seconds=90,
    ),
    mc(
        "Which equation represents the graph of $y = \\sqrt{x}$ shifted $4$ units right and $2$ units down?",
        "$y = \\sqrt{x - 4} - 2$",
        ["$y = \\sqrt{x + 4} - 2$", "$y = \\sqrt{x - 4} + 2$", "$y = \\sqrt{x} - 6$"],
        "A right shift of $4$ replaces $x$ with $x - 4$, and a downward shift of $2$ subtracts $2$ from the output: $y = \\sqrt{x - 4} - 2$.",
        "A right shift is often written incorrectly as $x + 4$ inside the radical.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Writing radical functions after horizontal and vertical translations",
        difficulty="Easy", estimated_time_seconds=80,
    ),
    mc(
        "The graph of $y = 2\\sqrt{x + 1}$ is obtained from $y = \\sqrt{x}$ by which transformations?",
        "A horizontal shift $1$ unit left and a vertical stretch by a factor of $2$",
        [
            "A horizontal shift $1$ unit right and a vertical stretch by a factor of $2$",
            "A horizontal shift $1$ unit left and a vertical compression by a factor of $\\frac{1}{2}$",
            "A vertical shift $1$ unit up and a horizontal stretch by a factor of $2$",
        ],
        "Replacing $x$ with $x + 1$ shifts the graph $1$ unit left. The coefficient $2$ outside the radical stretches the graph vertically by a factor of $2$.",
        "Students confuse left/right shifts and vertical stretch factors.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Identifying transformations of radical functions",
        difficulty="Medium", estimated_time_seconds=100,
    ),
    mc(
        "Solve $\\sqrt{3x + 1} = 4$. Which value of $x$ satisfies the equation?",
        "$5$",
        ["$3$", "$\\frac{5}{3}$", "$17$"],
        "Squaring both sides gives $3x + 1 = 16$, so $3x = 15$ and $x = 5$. Checking: $\\sqrt{16} = 4$, which is valid.",
        "Students may square incorrectly as $3x + 1 = 4$ and get $x = 1$, or forget to isolate before squaring.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving a basic radical equation by squaring both sides",
        difficulty="Medium", estimated_time_seconds=120,
    ),
    mc(
        "How many real solutions does the equation $\\sqrt{x + 2} = -1$ have?",
        "$0$",
        ["$1$", "$2$", "Infinitely many"],
        "A principal square root cannot equal a negative number. Therefore the equation has no real solutions.",
        "Students may square both sides and find $x = -1$ without checking that the original equation is impossible.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Recognizing impossible radical equations",
        difficulty="Easy", estimated_time_seconds=70,
    ),
    mc(
        "What is the $x$-intercept of $f(x) = \\sqrt{2x - 8}$?",
        "$(4, 0)$",
        ["$(0, 4)$", "$(8, 0)$", "$(2, 0)$"],
        "Set $f(x) = 0$: $\\sqrt{2x - 8} = 0$ implies $2x - 8 = 0$, so $x = 4$. The intercept is $(4, 0)$.",
        "Students may set $2x - 8 = 4$ instead of $0$, or confuse $x$- and $y$-intercepts.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Finding x-intercepts of radical functions",
        difficulty="Easy", estimated_time_seconds=100,
    ),
    mc(
        "Which function has domain $x \\ge -3$?",
        "$f(x) = \\sqrt{x + 3}$",
        ["$f(x) = \\sqrt{x - 3}$", "$f(x) = \\sqrt{-x + 3}$", "$f(x) = \\sqrt{3x}$"],
        "Require $x + 3 \\ge 0$, giving $x \\ge -3$. Only $f(x) = \\sqrt{x + 3}$ satisfies this.",
        "Students may choose $\\sqrt{x - 3}$, which requires $x \\ge 3$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Matching radical functions to stated domains",
        difficulty="Easy", estimated_time_seconds=75,
    ),
    mc(
        "The point $(9, 5)$ lies on $y = \\sqrt{x - 4} + 1$. After the transformation $y = -\\sqrt{x - 4} + 1$, where does the corresponding point move?",
        "$(9, -5)$",
        ["$(9, 5)$", "$(-9, 5)$", "$(9, 3)$"],
        "The transformation reflects the graph across the $x$-axis, mapping $(x, y)$ to $(x, -y)$. Thus $(9, 5)$ becomes $(9, -5)$.",
        "Students may reflect across the $y$-axis instead, changing the $x$-coordinate.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Applying vertical reflection to points on radical graphs",
        difficulty="Easy", estimated_time_seconds=95,
    ),
    mc(
        "Solve $\\sqrt{2x + 3} = x$. Which value of $x$ is a valid solution?",
        "$x = 3$",
        ["$x = -1$", "$x = 1$", "No real solutions"],
        "Squaring gives $2x + 3 = x^2$, or $x^2 - 2x - 3 = 0$, which factors as $(x - 3)(x + 1) = 0$. Checking: $x = 3$ gives $\\sqrt{9} = 3$ (valid); $x = -1$ gives $\\sqrt{1} = 1 \\ne -1$ (extraneous).",
        "Students often accept both algebraic roots after squaring without checking in the original equation.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving radical equations with extraneous roots",
        difficulty="Hard", estimated_time_seconds=180,
    ),
    mc(
        "Which graph could represent $y = -\\frac{1}{2}\\sqrt{x - 1} + 4$?",
        "A square-root curve starting near $(1, 4)$, opening downward and to the right, with vertical compression",
        [
            "A square-root curve starting near $(-1, 4)$, opening upward and to the right",
            "A parabola with vertex $(1, 4)$ opening downward",
            "A square-root curve starting near $(1, 4)$, opening upward and to the right",
        ],
        "The term $\\sqrt{x - 1}$ starts at $x = 1$. The negative coefficient reflects the graph vertically and compresses it by $\\frac{1}{2}$. The $+4$ shifts it up to begin near $(1, 4)$ with a decreasing trend.",
        "Students may ignore the negative coefficient and sketch an increasing radical graph.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Analyzing combined transformations of radical functions",
        difficulty="Hard", estimated_time_seconds=150,
    ),
    mc(
        "If $f(x) = \\sqrt{x}$ and $g(x) = f(x - 2) + 3$, what is $g(6)$?",
        "$5$",
        ["$3$", "$\\sqrt{6}$", "$9$"],
        "Compute $g(6) = f(6 - 2) + 3 = f(4) + 3 = \\sqrt{4} + 3 = 2 + 3 = 5$.",
        "Students may evaluate $f(6)$ instead of $f(4)$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Evaluating transformed radical functions",
        difficulty="Medium", estimated_time_seconds=70,
    ),
    mc(
        "What is the minimum value of $h(x) = \\sqrt{x - 2} + 7$ on its domain?",
        "$7$",
        ["$2$", "$0$", "$9$"],
        "On the domain $x \\ge 2$, the smallest radicand is $0$ when $x = 2$, giving $h(2) = 0 + 7 = 7$.",
        "Students may report the domain endpoint $x = 2$ as the minimum value instead of the output.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Finding minimum output values of translated radical functions",
        difficulty="Easy", estimated_time_seconds=90,
    ),
    mc(
        "Which restriction on $x$ is required for $\\sqrt{5 - 2x}$ to be defined?",
        "$x \\le \\frac{5}{2}$",
        ["$x \\ge \\frac{5}{2}$", "$x \\le -\\frac{5}{2}$", "$x \\ge 0$"],
        "Require $5 - 2x \\ge 0$, so $2x \\le 5$ and $x \\le \\frac{5}{2}$.",
        "Students may reverse the inequality direction.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Determining domain restrictions from radicands",
        difficulty="Medium", estimated_time_seconds=85,
    ),
    mc(
        "The graph of $y = \\sqrt{x}$ is reflected in the $y$-axis and then shifted $3$ units up. Which equation matches the result?",
        "$y = \\sqrt{-x} + 3$",
        ["$y = -\\sqrt{x} + 3$", "$y = \\sqrt{x} + 3$", "$y = \\sqrt{x - 3}$"],
        "A reflection in the $y$-axis replaces $x$ with $-x$, giving $y = \\sqrt{-x}$. A shift up $3$ adds $3$: $y = \\sqrt{-x} + 3$.",
        "Students confuse reflection in the $y$-axis with reflection in the $x$-axis.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Combining reflection and translation of radical functions",
        difficulty="Hard", estimated_time_seconds=130,
    ),
]

# 7 NR Radical
RADICAL += [
    nr(
        "For $f(x) = \\sqrt{x + 9}$, determine the $x$-coordinate of the $x$-intercept.",
        -9,
        "Set $\\sqrt{x + 9} = 0$. Then $x + 9 = 0$, so $x = -9$.",
        "Students may answer $9$ by forgetting the sign when solving $x + 9 = 0$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Finding x-intercepts of radical functions",
        difficulty="Medium", estimated_time_seconds=80,
    ),
    nr(
        "Evaluate $f(10)$ if $f(x) = 3\\sqrt{x - 1} - 2$.",
        7,
        "Substitute $x = 10$: $f(10) = 3\\sqrt{9} - 2 = 3(3) - 2 = 7$.",
        "Students may compute $\\sqrt{10 - 1}$ incorrectly or forget the final subtraction.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Evaluating radical functions at a given input",
        difficulty="Medium", estimated_time_seconds=75,
    ),
    nr(
        "Solve $\\sqrt{2x - 3} = 5$. State the value of $x$.",
        14,
        "Square both sides: $2x - 3 = 25$, so $2x = 28$ and $x = 14$. Check: $\\sqrt{25} = 5$.",
        "Students may add $3$ before squaring or divide by $2$ too early.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving radical equations",
        difficulty="Medium", estimated_time_seconds=120,
    ),
    nr(
        "The graph of $y = a\\sqrt{x - 2}$ passes through $(6, 4)$. Determine the value of $a$.",
        2,
        "Substitute the point: $4 = a\\sqrt{6 - 2} = a\\sqrt{4} = 2a$. Solve $2a = 4$ to get $a = 2$.",
        "Students may divide by $4$ instead of $2$ after taking the square root.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Determining stretch factors from points on radical graphs",
        difficulty="Medium", estimated_time_seconds=130,
    ),
    nr(
        "Solve $\\sqrt{x + 7} = x + 1$. Enter the valid solution for $x$.",
        2,
        "Square: $x + 7 = (x + 1)^2 = x^2 + 2x + 1$. Rearrange to $x^2 + x - 6 = 0$, giving $x = 2$ or $x = -3$. Check: $x = 2$ gives $\\sqrt{9} = 3$ (valid); $x = -3$ gives $\\sqrt{4} = -2$ (invalid).",
        "Students often include the extraneous root $x = -3$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving radical equations and rejecting extraneous roots",
        difficulty="Hard", estimated_time_seconds=180,
    ),
    nr(
        "For $g(x) = -\\sqrt{x} + 6$, determine the $y$-coordinate of the endpoint of the graph on its domain.",
        6,
        "The domain starts at $x = 0$, where $g(0) = -\\sqrt{0} + 6 = 6$. The endpoint has $y$-coordinate $6$.",
        "Students may give the $x$-coordinate $0$ instead of the $y$-coordinate.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Identifying endpoints of radical graphs",
        difficulty="Easy", estimated_time_seconds=85,
    ),
    nr(
        "If $\\sqrt{4x + 1} = 9$, determine the value of $x$.",
        20,
        "Square: $4x + 1 = 81$, so $4x = 80$ and $x = 20$.",
        "Students may subtract $1$ incorrectly or divide by $4$ prematurely.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving linear radical equations",
        difficulty="Medium", estimated_time_seconds=110,
    ),
    nr(
        "The graph of $y = \\sqrt{x + 4}$ begins at its endpoint. Determine the $x$-coordinate of this endpoint.",
        -4,
        "Require $x + 4 \\ge 0$. The graph starts when the radicand is $0$, at $x = -4$.",
        "Students may answer $4$ by ignoring the sign in the radicand shift.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Identifying starting points of radical graphs",
        difficulty="Easy", estimated_time_seconds=75,
    ),
]

# 2 WR Radical (removed domain/range WR — covered by MC/NR)
RADICAL += [
    wr(
        "Solve $\\sqrt{x + 5} = x - 1$. Show all algebraic steps and verify each potential solution in the original equation.",
        "$x = 4$",
        "Solution guide: square both sides to obtain $x + 5 = (x - 1)^2$. Expand and rearrange to a quadratic, factor, then test each root in the original radical equation. Only $x = 4$ satisfies $\\sqrt{9} = 3$.",
        "Accepting $x = -1$ after squaring without checking that $\\sqrt{4} \\neq -2$.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Solving radical equations with verification",
        difficulty="Hard", estimated_time_seconds=300,
    ),
    wr(
        "Describe the sequence of transformations that maps $y = \\sqrt{x}$ onto $y = -2\\sqrt{x + 3} - 1$. Include the starting point of the transformed graph.",
        "Left 3, vertical stretch by 2, reflection in x-axis, down 1; starting point $(-3, -1)$",
        "Rubric: identify horizontal shift ($x \\to x + 3$), vertical stretch (factor $2$), reflection (negative coefficient), vertical translation ($-1$), and correct transformed starting point $(-3, -1)$.",
        "Listing transformations in an order that does not match the equation, or giving the wrong starting point.",
        topic="Radical Functions", outcome_code="RF12",
        skill_tested="Describing transformations of radical functions",
        difficulty="Medium", estimated_time_seconds=240,
    ),
]

# Need 25 radical total: 15+8+2=25
assert len(RADICAL) == 25, len(RADICAL)

RATIONAL = []

# 15 MC Rational
RATIONAL += [
    mc(
        "What is the vertical asymptote of $f(x) = \\dfrac{3}{x - 4}$?",
        "$x = 4$",
        ["$x = -4$", "$x = 3$", "$y = 4$"],
        "A vertical asymptote occurs where the denominator is zero (and the factor does not cancel): $x - 4 = 0$ gives $x = 4$.",
        "Students may set the numerator equal to zero or confuse vertical and horizontal asymptotes.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Identifying vertical asymptotes of rational functions",
        difficulty="Easy", estimated_time_seconds=70,
    ),
    mc(
        "What is the horizontal asymptote of $g(x) = \\dfrac{2x + 1}{x - 5}$?",
        "$y = 2$",
        ["$y = 1$", "$y = -5$", "$y = 0$"],
        "Degrees of numerator and denominator are equal, so the horizontal asymptote is the ratio of leading coefficients: $\\frac{2}{1} = 2$.",
        "Students may use the constant term of the numerator instead of the leading coefficient.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Determining horizontal asymptotes when degrees are equal",
        difficulty="Easy", estimated_time_seconds=80,
    ),
    mc(
        "For $h(x) = \\dfrac{x^2 - 1}{x - 1}$, which statement is true?",
        "There is a hole at $x = 1$ and a simplified form $h(x) = x + 1$ for $x \\ne 1$",
        [
            "There is a vertical asymptote at $x = 1$ only",
            "The function is undefined for all real $x$",
            "The horizontal asymptote is $y = 1$",
        ],
        "Factor numerator: $x^2 - 1 = (x - 1)(x + 1)$. The common factor cancels, creating a hole at $x = 1$, not a vertical asymptote.",
        "Students may cancel incorrectly and still claim a vertical asymptote remains.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Distinguishing holes from vertical asymptotes",
        difficulty="Medium", estimated_time_seconds=120,
    ),
    mc(
        "What is the domain of $f(x) = \\dfrac{5}{x^2 - 9}$?",
        "$x \\ne 3$ and $x \\ne -3$",
        ["$x \\ne 9$", "$x \\ge 3$", "All real numbers"],
        "Exclude values that make the denominator zero: $x^2 - 9 = 0$ gives $x = \\pm 3$.",
        "Students may exclude only $x = 3$ and forget $x = -3$.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Determining domain of rational functions",
        difficulty="Easy", estimated_time_seconds=75,
    ),
    mc(
        "Which function has a horizontal asymptote of $y = 0$?",
        "$f(x) = \\dfrac{4x + 1}{x^2 + 2}$",
        ["$f(x) = \\dfrac{x^2 + 1}{2x}$", "$f(x) = \\dfrac{3x}{x + 1}$", "$f(x) = \\dfrac{x^2}{x^2 - 1}$"],
        "When the denominator degree is greater than the numerator degree, the horizontal asymptote is $y = 0$.",
        "Students may choose equal-degree examples where $y \\ne 0$.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Identifying horizontal asymptotes from degrees",
        difficulty="Medium", estimated_time_seconds=95,
    ),
    mc(
        "Solve $\\dfrac{2}{x} = \\dfrac{5}{x + 3}$ for $x$.",
        "$x = 2$",
        ["$x = -2$", "$x = 5$", "$x = 0$"],
        "Cross-multiply: $2(x + 3) = 5x$, so $2x + 6 = 5x$ and $x = 2$. Check that $x \\ne 0$.",
        "Students may forget to exclude $x = 0$ from the domain or make sign errors.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving simple rational equations",
        difficulty="Hard", estimated_time_seconds=120,
    ),
    mc(
        "The graph of $y = \\dfrac{1}{x}$ is shifted $2$ units right. Which equation represents the transformed graph?",
        "$y = \\dfrac{1}{x - 2}$",
        ["$y = \\dfrac{1}{x + 2}$", "$y = \\dfrac{1}{x} - 2$", "$y = \\dfrac{1}{x - 2} + 2$"],
        "A right shift replaces $x$ with $x - 2$ in the denominator: $y = \\dfrac{1}{x - 2}$.",
        "Students may write $x + 2$ for a right shift.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Writing reciprocal functions after horizontal translation",
        difficulty="Medium", estimated_time_seconds=80,
    ),
    mc(
        "What is the $y$-intercept of $f(x) = \\dfrac{3x - 6}{x + 4}$?",
        "$(0, -\\frac{3}{2})$",
        ["$(0, 3)$", "$(-4, 0)$", "There is no $y$-intercept"],
        "Evaluate at $x = 0$: $f(0) = \\frac{-6}{4} = -\\frac{3}{2}$, so the intercept is $(0, -\\frac{3}{2})$.",
        "Students may confuse the $x$-value that makes the denominator zero with a $y$-intercept.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Finding intercepts of rational functions",
        difficulty="Medium", estimated_time_seconds=100,
    ),
    mc(
        "Which expression is equivalent to $\\dfrac{x^2 - 5x + 6}{x - 2}$ for $x \\ne 2$?",
        "$x - 3$",
        ["$x + 3$", "$x - 2$", "$x^2 - 3$"],
        "Factor the numerator: $(x - 2)(x - 3)$. Cancel $x - 2$ to get $x - 3$.",
        "Students may factor incorrectly as $(x + 2)(x + 3)$.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Simplifying rational expressions by factoring",
        difficulty="Medium", estimated_time_seconds=110,
    ),
    mc(
        "For $f(x) = \\dfrac{x + 1}{x^2 - 4}$, how many vertical asymptotes does the graph have?",
        "$2$",
        ["$1$", "$0$", "$4$"],
        "Factor denominator $x^2 - 4 = (x - 2)(x + 2)$. No common factors cancel with the numerator, so there are vertical asymptotes at $x = 2$ and $x = -2$.",
        "Students may count only one factor or include a hole that does not exist.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Counting vertical asymptotes",
        difficulty="Medium", estimated_time_seconds=115,
    ),
    mc(
        "Solve $\\dfrac{x}{x - 1} = 2$. Which value is a valid solution?",
        "$x = 2$",
        ["$x = 1$", "$x = -2$", "No solution"],
        "Multiply both sides by $x - 1$ (with $x \\ne 1$): $x = 2(x - 1)$, so $x = 2x - 2$ and $x = 2$.",
        "Students may accept $x = 1$, which is excluded from the domain.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving rational equations with domain restrictions",
        difficulty="Hard", estimated_time_seconds=150,
    ),
    mc(
        "Which graph description matches $y = \\dfrac{-2}{x + 1} + 3$?",
        "A reciprocal graph with vertical asymptote $x = -1$, horizontal asymptote $y = 3$, reflected across the $x$-axis",
        [
            "A reciprocal graph with vertical asymptote $x = 1$, horizontal asymptote $y = -3$",
            "A parabola opening downward with vertex $(-1, 3)$",
            "A reciprocal graph with vertical asymptote $x = -1$, horizontal asymptote $y = -3$",
        ],
        "The denominator $x + 1$ gives a vertical asymptote at $x = -1$. The negative coefficient reflects the graph, and adding $3$ shifts the horizontal asymptote to $y = 3$.",
        "Students may ignore the vertical translation effect on the horizontal asymptote.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Analyzing transformed reciprocal functions",
        difficulty="Hard", estimated_time_seconds=160,
    ),
    mc(
        "What is the horizontal asymptote of $p(x) = \\dfrac{7x^2 + 1}{3x^2 - x + 4}$?",
        "$y = \\dfrac{7}{3}$",
        ["$y = 7$", "$y = 0$", "$y = \\dfrac{1}{4}$"],
        "Equal degrees in numerator and denominator give a horizontal asymptote at the ratio of leading coefficients $\\frac{7}{3}$.",
        "Students may use constant terms instead of leading coefficients.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Determining horizontal asymptotes for quadratic-over-quadratic functions",
        difficulty="Medium", estimated_time_seconds=100,
    ),
    mc(
        "The function $f(x) = \\dfrac{x^2 - 4x + 4}{x - 2}$ simplifies to which expression for $x \\ne 2$?",
        "$x - 2$",
        ["$x + 2$", "$x - 4$", "$x^2 - 2$"],
        "Numerator factors as $(x - 2)^2$. Cancel one factor of $x - 2$ to obtain $x - 2$.",
        "Students may cancel both factors and incorrectly conclude the function is constant.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Simplifying rational expressions with repeated factors",
        difficulty="Hard", estimated_time_seconds=90,
    ),
    mc(
        "Which value of $x$ must be excluded from the domain of $g(x) = \\dfrac{x + 5}{x^2 + x - 6}$?",
        "$x = 2$ and $x = -3$",
        ["$x = -5$", "$x = 3$ and $x = -2$", "$x = 6$"],
        "Factor denominator: $x^2 + x - 6 = (x + 3)(x - 2)$. Exclude $x = -3$ and $x = 2$.",
        "Students may factor incorrectly or exclude only one root.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Finding domain exclusions by factoring denominators",
        difficulty="Hard", estimated_time_seconds=140,
    ),
]

# 7 NR Rational
RATIONAL += [
    nr(
        "Determine the $x$-coordinate of the vertical asymptote of $f(x) = \\dfrac{6}{x + 5}$.",
        -5,
        "Set the denominator equal to zero: $x + 5 = 0$, so $x = -5$.",
        "Students may answer $5$ by dropping the negative sign.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Finding vertical asymptotes",
        difficulty="Easy", estimated_time_seconds=70,
    ),
    nr(
        "For $h(x) = \\dfrac{4x}{x + 2}$, determine the horizontal asymptote value $y = k$.",
        4,
        "Degrees are equal, so $k$ is the ratio of leading coefficients $\\frac{4}{1} = 4$.",
        "Students may answer $2$ from the denominator constant.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Determining horizontal asymptotes",
        difficulty="Easy", estimated_time_seconds=80,
    ),
    nr(
        "Solve $\\dfrac{3}{x - 1} = 2$ for $x$.",
        2.5,
        "Multiply: $3 = 2(x - 1) = 2x - 2$, so $2x = 5$ and $x = 2.5$.",
        "Students may distribute incorrectly as $3 = 2x - 1$.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving rational equations",
        difficulty="Medium", estimated_time_seconds=120,
    ),
    nr(
        "For $f(x) = \\dfrac{x^2 - 9}{x - 3}$, the hole occurs at $x = 3$. Determine the $y$-coordinate of the hole.",
        6,
        "Simplify to $x + 3$ for $x \\ne 3$. The hole is at $(3, 6)$, so the $y$-coordinate is $6$.",
        "Students may answer $3$ or $0$ by confusing coordinates.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Finding coordinates of holes in rational graphs",
        difficulty="Medium", estimated_time_seconds=130,
    ),
    nr(
        "Solve $\\dfrac{5}{x} + \\dfrac{2}{x + 1} = 1$. Enter the positive solution for $x$.",
        5,
        "Combine fractions: $\\frac{5(x+1) + 2x}{x(x+1)} = 1$, so $7x + 5 = x^2 + x$. Rearrange to $x^2 - 6x - 5 = 0$. Using the quadratic formula, $x = 3 \\pm 2\\sqrt{7}$. The positive solution is $3 + 2\\sqrt{7} \\approx 8.29$, but checking the simplified integer-friendly equivalent: multiply through correctly gives $x = 5$ after algebraic simplification when using common denominator $x(x+1)$: $7x + 5 = x^2 + x$, roots $x = \\frac{6 \\pm \\sqrt{36 + 20}}{2} = \\frac{6 \\pm \\sqrt{56}}{2}$. Recalculate: $x^2 - 6x - 5 = 0$, positive root $x = 3 + 2\\sqrt{7}$. Use cleaner equation instead - fix to solvable integer.",
        "Students may include $x = 0$ or $x = -1$ despite domain restrictions.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving rational equations with multiple fractions",
        difficulty="Hard", estimated_time_seconds=200,
    ),
]

# Fix the bad NR question #5 - replace with clean math
RATIONAL[-1] = nr(
    "Solve $\\dfrac{6}{x + 1} = x + 2$. Enter the smaller valid solution for $x$.",
    -4,
    "Multiply by $x + 1$ (with $x \\ne -1$): $6 = (x + 1)(x + 2) = x^2 + 3x + 2$. Rearrange to $x^2 + 3x - 4 = 0$, or $(x + 4)(x - 1) = 0$. Both $x = 1$ and $x = -4$ satisfy the original equation; the smaller is $-4$.",
    "Students may give only the positive root or forget that $x = -1$ is excluded.",
    topic="Rational Functions", outcome_code="RF14",
    skill_tested="Solving rational equations leading to quadratics",
    difficulty="Hard", estimated_time_seconds=180,
)

# Add 2 more NR to reach 7
RATIONAL += [
    nr(
        "Evaluate $f(0)$ for $f(x) = \\dfrac{2x - 5}{x + 3}$. Express your answer as a decimal.",
        -1.667,
        "Substitute $x = 0$: $f(0) = \\frac{-5}{3} \\approx -1.667$.",
        "Students may invert the fraction or use $x = -3$.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Evaluating rational functions",
        difficulty="Medium", estimated_time_seconds=75,
    ),
    nr(
        "Solve $\\dfrac{x + 4}{x - 1} = 3$ for $x$.",
        3.5,
        "Cross-multiply or multiply both sides: $x + 4 = 3(x - 1) = 3x - 3$. Then $7 = 2x$ and $x = 3.5$.",
        "Students may distribute the $3$ incorrectly as $3x - 1$.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving linear rational equations",
        difficulty="Medium", estimated_time_seconds=115,
    ),
]

# 3 WR Rational
RATIONAL += [
    wr(
        "Given $f(x) = \\dfrac{2x}{x - 3}$, determine all asymptotes, intercepts, and the domain. State whether the function has any holes.",
        "VA: $x = 3$; HA: $y = 2$; Domain: $x \\ne 3$; x-int: $(0,0)$; y-int: $(0,0)$; no holes",
        "Rubric: identify vertical asymptote from denominator zero with no cancellation; horizontal asymptote from equal degrees; domain exclusion; intercepts by substitution; confirm no common factors for holes.",
        "Claiming a hole at $x = 3$ or giving the wrong horizontal asymptote.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Analyzing key characteristics of rational functions",
        difficulty="Medium", estimated_time_seconds=300,
    ),
    wr(
        "Solve $\\dfrac{1}{x} + \\dfrac{1}{x + 2} = \\dfrac{3}{4}$. Show algebraic steps and identify any excluded values.",
        "$x = 2$ and $x = -\\dfrac{4}{3}$",
        "Rubric: exclude $x \\ne 0, -2$; multiply through by $4x(x + 2)$ or use a common denominator to obtain $3x^2 - 2x - 8 = 0$; solve to get $x = 2$ and $x = -\\frac{4}{3}$; verify both in the original equation.",
        "Failing to exclude domain values or not checking solutions after clearing denominators.",
        topic="Rational Functions", outcome_code="RF14",
        skill_tested="Solving rational equations with multiple terms",
        difficulty="Hard", estimated_time_seconds=360,
    ),
    wr(
        "A rational function has a vertical asymptote at $x = -2$, a horizontal asymptote at $y = 1$, and passes through $(0, 0)$. Write one possible equation and justify each feature.",
        "Example: $f(x) = \\dfrac{x}{x + 2}$",
        "Rubric: denominator zero at $x = -2$; equal-degree numerator and denominator with matching leading coefficients for $y = 1$; substitution confirms $(0,0)$.",
        "Using unequal degrees, which changes the horizontal asymptote away from $y = 1$.",
        topic="Rational Functions", outcome_code="RF13",
        skill_tested="Constructing rational functions from characteristics",
        difficulty="Hard", estimated_time_seconds=360,
    ),
]

# Verify counts
assert len(RADICAL) == 25, len(RADICAL)
assert len(RATIONAL) == 25, len(RATIONAL)
all_q = RADICAL + RATIONAL

# Count distributions
from collections import Counter

def count(items, key):
    return Counter(q[key] for q in items)

print("STATS", count(all_q, "question_type"), count(all_q, "difficulty"), file=sys.stderr)

# Load existing texts
existing = set()
if DB.exists():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        """SELECT lower(trim(q.question_text)) FROM questions q
           JOIN topics t ON q.topic_id=t.id
           JOIN courses co ON t.course_id=co.id
           WHERE co.code='MATH30-1'"""
    )
    existing = {row[0] for row in c.fetchall()}
    conn.close()

errors = []
for i, item in enumerate(all_q):
    reasons = validate_question(item, i)
    if reasons:
        errors.append((i, reasons))
    norm = " ".join(item["question_text"].split()).casefold()
    if norm in existing:
        errors.append((i, ["duplicate of existing DB question"]))

if errors:
    print("VALIDATION ERRORS:", file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)
    sys.exit(1)

out = Path(__file__).parent.parent / "questions.json" / "radical_rational_50.json"
mc_pos = assert_mc_position_balanced(all_q, label=str(out))
print("MC correct-position distribution:", format_position_report(mc_pos))
out.write_text(json.dumps(all_q, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(all_q, ensure_ascii=False))
