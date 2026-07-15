"""Additional MC-heavy questions for coverage gaps (AN1, RF6, RF7, RF8)."""

import random
from math20_1_questions.helpers import mc, nr

TOPIC_AV = "Absolute Value and Reciprocal Functions"
TOPIC_SYS = "Systems of Equations"
TOPIC_INEQ = "Linear and Quadratic Inequalities"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # AN1 absolute value of numbers
    for v in [-12, -8, -1, 0, 3, 7, 15, -20, 22, -6, 9, -14, 18, -25, 11]:
        out.append(nr(
            f"Evaluate $\\left|{v}\\right|$. Record the integer answer.",
            str(abs(v)),
            f"$\\left|{v}\\right| = {abs(v)}$.",
            "Students report the original signed value.",
            topic=TOPIC_AV, outcome_code="AN1",
            skill_tested="Evaluating absolute value of a real number",
            difficulty="Easy", estimated_time_seconds=45,
        ))

    for a, b in [(3, 7), (-2, 5), (4, -1), (-6, -3), (1, 9), (-8, 2)]:
        dist = abs(a - b)
        out.append(nr(
            f"What is the distance between ${a}$ and ${b}$ on a number line? "
            f"Record the integer answer.",
            str(dist),
            f"Distance $= |{a} - ({b})| = {dist}$.",
            "Students subtract in the wrong order and report a negative value.",
            topic=TOPIC_AV, outcome_code="AN1",
            skill_tested="Calculating distance on a number line using absolute value",
            difficulty="Easy", estimated_time_seconds=55,
        ))

    an1_mc = [
        ("Which statement about $|x|$ is always true for $x \\in \\mathbb{R}$?",
         "$|x| \\ge 0$",
         ["$|x| = x$", "$|x| = -x$", "$|x| < 0$ for some $x$"],
         "Absolute value is never negative.",
         "Assuming $|x| = x$ for all real numbers.", "Easy", 55),
        ("Which value is equal to $\\left|-\\dfrac{7}{3}\\right|$?",
         "$\\dfrac{7}{3}$",
         ["$-\\dfrac{7}{3}$", "$\\dfrac{3}{7}$", "$-7$"],
         "Absolute value returns the positive magnitude $\\frac{7}{3}$.",
         "Keeping the negative sign.", "Easy", 50),
        ("If $|a| = 4$, which could be the value of $a$?",
         "$-4$",
         ["$0$ only", "$-4$ and $4$ is impossible", "$16$"],
         "Both $4$ and $-4$ satisfy $|a| = 4$; $-4$ is one valid choice.",
         "Thinking absolute value removes the possibility of negative $a$.", "Medium", 70),
    ]
    for qt, ans, dist, expl, mis, diff, t in an1_mc:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_AV, outcome_code="AN1",
                      skill_tested="Interpreting absolute value properties",
                      difficulty=diff, estimated_time_seconds=t))

    # RF6 systems MC
    sys_mc = [
        ("A linear-quadratic system has no real points of intersection when:",
         "The line is above or below the parabola everywhere",
         ["The line has slope zero", "The parabola opens downward",
          "The system is written in standard form"],
         "No intersection means the line and parabola never meet.",
         "Confusing 'no intersection' with 'one intersection at the vertex'.", "Medium", 75),
        ("The points of intersection of a system correspond to:",
         "Solutions that satisfy both equations simultaneously",
         ["Only the $y$-intercepts of each graph",
          "The vertex of the parabola only",
          "The axis of symmetry of the parabola"],
         "Intersection coordinates solve both equations at once.",
         "Equating $y$-intercepts instead of solving the system.", "Easy", 60),
        ("When solving $y = x^2$ and $y = 2x + 3$ algebraically, the first step is:",
         "Set $x^2 = 2x + 3$ and rearrange to standard form",
         ["Substitute $y = 0$ into both equations",
          "Graph both equations without algebra",
          "Divide both equations by $x$"],
         "Equating the two expressions for $y$ gives a single equation in $x$.",
         "Dividing by $x$ and losing the $x = 0$ case.", "Medium", 85),
    ]
    for qt, ans, dist, expl, mis, diff, t in sys_mc:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_SYS, outcome_code="RF6",
                      skill_tested="Explaining linear-quadratic system solution meaning",
                      difficulty=diff, estimated_time_seconds=t))

    # RF7 inequalities MC
    rf7_mc = [
        ("Which inequality represents all points below the line $y = -x + 4$?",
         "$y < -x + 4$",
         ["$y > -x + 4$", "$y \\ge -x + 4$", "$x < -y + 4$"],
         "Below the line means lesser $y$-values.",
         "Reversing the inequality direction.", "Easy", 55),
        ("To test whether $(1, 2)$ satisfies $y \\ge x^2 - 3$, you should check:",
         "Whether $2 \\ge 1^2 - 3$",
         ["Whether $1 \\ge 2^2 - 3$", "Whether $2 \\ge 0$ only",
          "Whether $x = y$"],
         "Substitute $x = 1$, $y = 2$ into the inequality.",
         "Swapping $x$ and $y$ coordinates.", "Medium", 75),
        ("A dashed boundary line on an inequality graph indicates:",
         "Points on the boundary are not included in the solution",
         ["The region is unbounded", "The inequality uses $\\ge$ or $\\le$",
          "The boundary is horizontal"],
         "Strict inequalities ($<$ or $>$) use dashed lines.",
         "Using dashed lines for inclusive inequalities.", "Easy", 55),
        ("Which point satisfies $y > 2x - 1$?",
         "$(2, 5)$",
         ["$(2, 3)$", "$(0, -2)$", "$(1, 1)$"],
         "At $(2,5)$: $5 > 2(2)-1 = 3$ is true.",
         "Testing only the boundary line, not strict inequality.", "Medium", 70),
    ]
    for qt, ans, dist, expl, mis, diff, t in rf7_mc:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_INEQ, outcome_code="RF7",
                      skill_tested="Interpreting linear inequality graphs and test points",
                      difficulty=diff, estimated_time_seconds=t))

    # RF8 MC
    rf8_mc = [
        ("For $(x-2)(x+5) > 0$, the solution intervals are:",
         "$x < -5$ or $x > 2$",
         ["$-5 < x < 2$", "$x > 2$ only", "$x < -5$ only"],
         "A positive product occurs outside the roots $-5$ and $2$.",
         "Choosing the interval between roots.", "Medium", 90),
        ("Which is equivalent to $x^2 - 6x + 8 < 0$ after factoring?",
         "$(x-2)(x-4) < 0$",
         ["$(x+2)(x+4) < 0$", "$(x-2)(x+4) < 0$", "$(x+2)(x-4) < 0$"],
         "$x^2 - 6x + 8 = (x-2)(x-4)$.",
         "Sign errors when factoring the trinomial.", "Medium", 85),
        ("When solving a quadratic inequality by sign analysis, critical values are found by:",
         "Setting the factored expression equal to zero",
         ["Setting each factor greater than zero only",
          "Completing the square only",
          "Using the quadratic formula on an inequality directly"],
         "Critical values occur where the expression equals zero (boundaries).",
         "Using only one side of the inequality.", "Medium", 80),
    ]
    for qt, ans, dist, expl, mis, diff, t in rf8_mc:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC_INEQ, outcome_code="RF8",
                      skill_tested="Solving and interpreting quadratic inequalities",
                      difficulty=diff, estimated_time_seconds=t))

    # Additional conceptual MC across topics
    misc_mc = [
        (TOPIC_AV, "RF11",
         "The horizontal asymptote of $y = \\dfrac{1}{x}$ is:",
         "$y = 0$",
         ["$x = 0$", "$y = 1$", "There is no horizontal asymptote"],
         "As $|x| \\to \\infty$, $\\frac{1}{x} \\to 0$.",
         "Confusing vertical and horizontal asymptotes.", "Easy", 55,
         "Identifying horizontal asymptote of reciprocal function"),
        (TOPIC_AV, "RF2",
         "The graph of $y = |x - 3|$ is shifted from $y = |x|$ by:",
         "3 units right",
         ["3 units left", "3 units down", "3 units up"],
         "$(x - 3)$ inside absolute value shifts right 3.",
         "Reversing horizontal shift direction.", "Easy", 60,
         "Identifying horizontal translation of absolute value graph"),
        ("Radical Expressions and Equations", "AN2",
         "Which is equal to $\\sqrt{50}$ in simplest radical form?",
         "$5\\sqrt{2}$",
         ["$25\\sqrt{2}$", "$10\\sqrt{5}$", "$2\\sqrt{5}$"],
         "$\\sqrt{50} = \\sqrt{25 \\cdot 2} = 5\\sqrt{2}$.",
         "Not factoring out the largest perfect square.", "Easy", 55,
         "Selecting simplest radical form"),
        ("Rational Expressions and Equations", "AN5",
         "When dividing $\\dfrac{3}{x} \\div \\dfrac{6}{x}$, the result is:",
         "$\\dfrac{1}{2}$",
         ["$\\dfrac{18}{x^2}$", "$\\dfrac{x}{2}$", "$18$"],
         "Multiply by the reciprocal: $\\frac{3}{x} \\cdot \\frac{x}{6} = \\frac{1}{2}$.",
         "Multiplying numerators and denominators directly without reciprocals.", "Medium", 80,
         "Dividing rational expressions with monomial denominators"),
        ("Sequences and Series", "RF9",
         "In an arithmetic sequence, the common difference is found by:",
         "Subtracting consecutive terms: $t_{n+1} - t_n$",
         ["Dividing consecutive terms",
          "Adding all terms and dividing by $n$",
          "Multiplying $t_1$ by $n$"],
         "Arithmetic sequences have constant difference between consecutive terms.",
         "Using a ratio instead of a difference.", "Easy", 55,
         "Defining common difference of arithmetic sequence"),
        ("Trigonometry", "T1",
         "The reference angle for $240^\\circ$ is:",
         "$60^\\circ$",
         ["$240^\\circ$", "$120^\\circ$", "$300^\\circ$"],
         "$240^\\circ$ is in QIII; reference angle $= 240 - 180 = 60$.",
         "Using the coterminal angle without reducing to acute.", "Easy", 60,
         "Finding reference angle in Quadrant III"),
        ("Quadratic Functions", "RF3",
         "For $f(x) = -2(x + 1)^2 + 5$, the parabola opens:",
         "Downward and has vertex $(-1, 5)$",
         ["Upward with vertex $(1, 5)$",
          "Downward with vertex $(1, -5)$",
          "Upward with vertex $(-1, 5)$"],
         "$a = -2 < 0$ opens down; vertex at $(-1, 5)$.",
         "Ignoring the negative leading coefficient.", "Medium", 75,
         "Identifying vertex and direction from vertex form"),
        ("Quadratic Equations", "RF5",
         "If the discriminant of a quadratic is negative, the equation has:",
         "No real solutions",
         ["Exactly one real solution", "Two equal real solutions",
          "Infinitely many solutions"],
         "$D < 0$ means no real roots.",
         "Assuming quadratics always have real roots.", "Easy", 55,
         "Interpreting negative discriminant"),
    ]
    for item in misc_mc:
        topic, oc, qt, ans, dist, expl, mis, diff, t, skill = item
        out.append(mc(qt, ans, dist, expl, mis, topic=topic, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    return out
