"""Programmatic Sequences and Series questions (RF9, RF10)."""

import random
from math20_1_questions.helpers import mc, nr

TOPIC = "Sequences and Series"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- Arithmetic sequences ---
    for _ in range(18):
        t1 = rng.randint(-8, 12)
        d = rng.choice([i for i in range(-6, 7) if i != 0])
        n = rng.randint(5, 15)
        tn = t1 + (n - 1) * d
        out.append(nr(
            f"In an arithmetic sequence, $t_1 = {t1}$ and $d = {d}$. "
            f"What is $t_{{{n}}}$? Record the integer answer.",
            str(tn),
            f"$t_n = t_1 + (n-1)d$. So $t_{{{n}}} = {t1} + ({n}-1)({d}) = {tn}$.",
            "Students use $t_n = t_1 + nd$ instead of $(n-1)d$.",
            topic=TOPIC, outcome_code="RF9",
            skill_tested="Calculating nth term of an arithmetic sequence",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for _ in range(12):
        t1 = rng.randint(2, 10)
        d = rng.randint(2, 6)
        n = rng.randint(6, 12)
        sn = n * (2 * t1 + (n - 1) * d) // 2
        out.append(nr(
            f"Find the sum of the first ${n}$ terms of the arithmetic series "
            f"with $t_1 = {t1}$ and $d = {d}$. Record the integer answer.",
            str(sn),
            f"$S_n = \\frac{{n}}{{2}}(2t_1 + (n-1)d) = \\frac{{{n}}}{{2}}({2*t1} + {n-1} \\cdot {d}) = {sn}$.",
            "Students forget to divide by 2 in the series formula.",
            topic=TOPIC, outcome_code="RF9",
            skill_tested="Calculating sum of an arithmetic series",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for _ in range(8):
        t1 = rng.randint(-5, 8)
        d = rng.choice([i for i in range(-4, 5) if i != 0])
        tn = rng.randint(-20, 40)
        # pick n so tn is reachable
        if d == 0:
            continue
        n = 1 + (tn - t1) // d
        if n < 2 or t1 + (n - 1) * d != tn:
            continue
        out.append(nr(
            f"An arithmetic sequence has $t_1 = {t1}$, common difference $d = {d}$, "
            f"and $t_n = {tn}$. What is the value of $n$? Record the integer answer.",
            str(n),
            f"Solve ${tn} = {t1} + (n-1)({d})$, giving $n = {n}$.",
            "Students solve for $d$ instead of $n$.",
            topic=TOPIC, outcome_code="RF9",
            skill_tested="Finding term number in an arithmetic sequence",
            difficulty="Medium", estimated_time_seconds=100,
        ))

    # --- Geometric sequences ---
    for _ in range(18):
        t1 = rng.choice([2, 3, 4, 5, 6, -2, -3])
        r = rng.choice([-3, -2, -1, 2, 3, 4, 5])
        if r in (0, 1, -1):
            continue
        n = rng.randint(4, 8)
        tn = t1 * (r ** (n - 1))
        out.append(nr(
            f"A geometric sequence has $t_1 = {t1}$ and common ratio $r = {r}$. "
            f"What is $t_{{{n}}}$? Record the integer answer.",
            str(tn),
            f"$t_n = t_1 \\cdot r^{{n-1}} = {t1} \\cdot ({r})^{{{n-1}}} = {tn}$.",
            "Students use $t_n = t_1 \\cdot r^n$ instead of $r^{{n-1}}$.",
            topic=TOPIC, outcome_code="RF10",
            skill_tested="Calculating nth term of a geometric sequence",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for _ in range(12):
        t1 = rng.randint(2, 8)
        r = rng.choice([2, 3, -2, -3])
        n = rng.randint(4, 6)
        if r == 1:
            continue
        sn = t1 * (1 - r ** n) // (1 - r)
        out.append(nr(
            f"Find the sum of the first ${n}$ terms of the geometric series "
            f"with $t_1 = {t1}$ and $r = {r}$. Record the integer answer.",
            str(sn),
            f"$S_n = t_1\\frac{{1-r^n}}{{1-r}} = {t1} \\cdot \\frac{{1-({r})^{n}}}{{1-{r}}} = {sn}$.",
            "Students use the arithmetic series formula by mistake.",
            topic=TOPIC, outcome_code="RF10",
            skill_tested="Calculating sum of a finite geometric series",
            difficulty="Medium", estimated_time_seconds=105,
        ))

    for _ in range(10):
        t1 = rng.randint(4, 20)
        r = rng.choice([2, 3, 4, 5])
        n = rng.randint(3, 6)
        sn = t1 * (1 - r ** n) // (1 - r)
        out.append(nr(
            f"The first term of a geometric series is ${t1}$ and $r = {r}$. "
            f"How many terms are in the partial sum $S_{{{n}}} = {sn}$? Record $n$.",
            str(n),
            f"Verify: $S_{n} = {t1}\\frac{{1-{r}^{n}}}{{1-{r}}} = {sn}$, so $n = {n}$.",
            "Students guess $n$ without checking the partial sum formula.",
            topic=TOPIC, outcome_code="RF10",
            skill_tested="Determining number of terms from geometric series sum",
            difficulty="Hard", estimated_time_seconds=130,
        ))

    # Infinite geometric series (|r| < 1)
    for t1, r, ans in [(8, 0.5, 16), (12, 1 / 3, 18), (15, 0.2, 18.75),
                         (20, -0.5, 40 / 3), (6, 2 / 3, 18), (10, -1 / 3, 7.5),
                         (9, 0.25, 12), (24, 1 / 4, 32), (5, 0.4, 25 / 3),
                         (16, -0.25, 64 / 5)]:
        out.append(nr(
            f"An infinite geometric series has first term $t_1 = {t1:g}$ and "
            f"common ratio $r = {r:g}$. What is the sum to infinity? "
            f"Express as a decimal rounded to two decimal places.",
            f"{ans:.2f}",
            f"Since $|r| < 1$, $S_\\infty = \\frac{{t_1}}{{1-r}} = "
            f"\\frac{{{t1:g}}}{{1-({r:g})}} \\approx {ans:.2f}$.",
            "Students apply the finite sum formula or forget $|r|$ must be less than 1.",
            topic=TOPIC, outcome_code="RF10",
            skill_tested="Calculating sum of a convergent infinite geometric series",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # MC classification / conceptual
    mc_items = [
        (
            "Which sequence is arithmetic but not geometric?",
            "$4, 7, 10, 13, \\ldots$",
            ["$3, 6, 12, 24, \\ldots$", "$5, -5, 5, -5, \\ldots$",
             "$2, 4, 8, 16, \\ldots$"],
            "Common difference $d = 3$ is constant; ratios are not constant.",
            "Assuming any increasing sequence must be geometric.",
            "RF9", "Distinguishing arithmetic from geometric sequences", "Easy", 60,
        ),
        (
            "Which sequence is geometric but not arithmetic?",
            "$81, 27, 9, 3, \\ldots$",
            ["$1, 4, 7, 10, \\ldots$", "$-2, 0, 2, 4, \\ldots$",
             "$10, 10, 10, 10, \\ldots$"],
            "Each term is multiplied by $r = \\frac{1}{3}$; differences are not constant.",
            "Treating a decreasing sequence as arithmetic.",
            "RF10", "Distinguishing geometric from arithmetic sequences", "Easy", 60,
        ),
        (
            "An arithmetic sequence has $t_1 = 5$ and $d = -3$. Which statement is true?",
            "The sequence is decreasing.",
            ["The sequence is increasing.", "The sequence is constant.",
             "The sequence cannot be defined."],
            "A negative common difference produces decreasing terms.",
            "Confusing negative difference with invalid sequence.",
            "RF9", "Interpreting effect of negative common difference", "Easy", 55,
        ),
        (
            "For a geometric series with $r = -2$, what can you conclude?",
            "The series is divergent (no finite sum to infinity).",
            ["The series converges to $0$.", "The series converges to $t_1$.",
             "The series always has sum $0$."],
            "$|r| = 2 > 1$, so terms do not approach $0$ and the infinite sum diverges.",
            "Assuming alternating sign guarantees convergence.",
            "RF10", "Determining convergence of a geometric series", "Medium", 85,
        ),
        (
            "The general term $t_n = 3n + 2$ represents which type of sequence?",
            "An arithmetic sequence with $t_1 = 5$ and $d = 3$",
            ["A geometric sequence with $r = 3$",
             "An arithmetic sequence with $d = 2$ only",
             "Neither arithmetic nor geometric"],
            "$t_n = 3n + 2$ is linear in $n$, characteristic of arithmetic sequences.",
            "Identifying the constant term as the common difference.",
            "RF9", "Recognizing arithmetic sequence from general term", "Medium", 75,
        ),
        (
            "If $t_n = 5 \\cdot 2^{n-1}$, which values are correct for $t_1$ and $r$?",
            "$t_1 = 5$, $r = 2$",
            ["$t_1 = 2$, $r = 5$", "$t_1 = 10$, $r = 2$", "$t_1 = 5$, $r = 5$"],
            "Substituting $n = 1$ gives $t_1 = 5$; each term doubles, so $r = 2$.",
            "Using the exponent as the first term.",
            "RF10", "Identifying first term and ratio from general term", "Medium", 80,
        ),
        (
            "Which infinite geometric series has a finite sum?",
            "$10 + 5 + 2.5 + 1.25 + \\ldots$",
            ["$3 + 6 + 12 + 24 + \\ldots$",
             "$4 - 8 + 16 - 32 + \\ldots$",
             "$2 + 2 + 2 + 2 + \\ldots$"],
            "This series has $r = 0.5$, so $|r| < 1$ and it converges.",
            "Ignoring the requirement $|r| < 1$ for convergence.",
            "RF10", "Identifying convergent infinite geometric series", "Medium", 80,
        ),
        (
            "An arithmetic series has $t_1 = 8$, $d = 4$, and $n = 10$. "
            "Which expression gives $S_{10}$?",
            "$S_{10} = \\dfrac{10}{2}(2(8) + 9(4))$",
            ["$S_{10} = 10(8 + 4)$", "$S_{10} = \\dfrac{10}{2}(8 + 4)$",
             "$S_{10} = 8 + 4(10)$"],
            "Use $S_n = \\frac{n}{2}(2t_1 + (n-1)d)$ with $n = 10$.",
            "Using $nd$ instead of $(n-1)d$ in the sum formula.",
            "RF9", "Selecting correct arithmetic series sum formula", "Medium", 90,
        ),
    ]
    for qt, ans, dist, expl, mis, oc, skill, diff, t in mc_items:
        out.append(mc(qt, ans, dist, expl, mis, topic=TOPIC, outcome_code=oc,
                      skill_tested=skill, difficulty=diff, estimated_time_seconds=t))

    return out
