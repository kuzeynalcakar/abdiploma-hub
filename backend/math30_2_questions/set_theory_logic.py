"""Set Theory and Logic — LR1, LR2."""

import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Set Theory and Logic"


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- LR1: puzzles and logical reasoning ---
    patterns = [
        (3, 8, 3, 987, 4, 9876, 5, 98765,
         "Each row uses one more leading digit in the multiplier pattern."),
        (2, 7, 2, 154, 3, 2156, 4, 21567,
         "Digits on the left grow by one each row while the addend matches the row number."),
        (4, 9, 4, 4321, 5, 54321, 6, 654321,
         "The constructed number gains one digit per row following the row index."),
    ]
    for p in patterns:
        mult, base, r, val, r2, val2, r3, val3, note = p
        out.append(nr(
            f"A number pattern begins: Row {r}: ${r} \\times {base} + {r} = {val}$, "
            f"Row {r2}: ${r2} \\times {base} + {r2} = {val2}$. "
            f"Following the same rule, what is the result of Row {r3}? Record the integer answer.",
            str(val3),
            f"{note} Row {r3} gives ${val3}$.",
            "Students repeat the previous row's structure without increasing the digit block.",
            topic=TOPIC, outcome_code="LR1",
            skill_tested="Extending a numerical pattern using logical reasoning",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    for start, step, n, ans in [
        (5, 7, 8, 54), (12, 4, 10, 48), (3, 11, 7, 69), (8, 6, 9, 56),
        (15, 3, 12, 48), (2, 13, 6, 67), (10, 5, 11, 60), (7, 8, 9, 71),
    ]:
        out.append(nr(
            f"A sequence starts at ${start}$ and each term increases by ${step}$. "
            f"What is the ${n}$th term? Record the integer answer.",
            str(ans),
            f"Term $n$ = ${start} + (n-1)({step}) = {ans}$.",
            "Students multiply by the step instead of adding repeatedly.",
            topic=TOPIC, outcome_code="LR1",
            skill_tested="Finding a term in an arithmetic pattern",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    grid_errors = [
        ("Row 2, Column 3 should be 4 but shows 2",
         "The entry violates the no-repeat rule in that row.",
         "2", "3", "4", "2"),
        ("Row 1, Column 4 should be 1 but shows 3",
         "Column 4 already contains 3 in row 3.",
         "1", "4", "1", "3"),
        ("Row 3, Column 2 should be 2 but shows 4",
         "The connected block would contain two 4s.",
         "3", "2", "2", "4"),
    ]
    for err_desc, why, row, col, correct, wrong in grid_errors:
        out.append(mc(
            f"In a $4 \\times 4$ logic grid, each row and column must contain "
            f"$1, 2, 3, 4$ exactly once. An entry in Row {row}, Column {col} "
            f"is {wrong} but should be {correct}. Which statement best describes the error?",
            err_desc,
            [
                f"The error is in Row {int(row)+1}, not Row {row}.",
                f"Column {col} is allowed to repeat the digit {wrong}.",
                "No rule is violated because diagonals may repeat digits.",
            ],
            f"{err_desc}. {why}",
            "Students check only rows or only columns, missing the violated constraint.",
            topic=TOPIC, outcome_code="LR1",
            skill_tested="Identifying an error in a logic grid puzzle",
            difficulty="Medium", estimated_time_seconds=95,
        ))

    for n in [4, 5, 6, 7, 8]:
        total = n * (n + 1) // 2
        side_sum = total // 3 + n
        out.append(mc(
            f"In a triangular array puzzle, the integers $1$ through ${n}$ are placed "
            f"in circles so each side of the triangle sums to the same value. "
            f"If the corner circles contain $1$, ${n}$, and ${n-1}$ in some order, "
            f"what is the side sum when the puzzle is completed correctly?",
            f"${side_sum}$",
            [f"${total}$", f"${side_sum + 2}$", f"${max(1, side_sum - 3)}$"],
            f"Corner values use the extremes; the side sum depends on the triangle size "
            f"and is ${total // 3 + n}$ for this configuration.",
            "Students sum all entries without accounting for shared corner circles.",
            topic=TOPIC, outcome_code="LR1",
            skill_tested="Reasoning about constraints in a triangular number puzzle",
            difficulty="Hard", estimated_time_seconds=120,
        ))

    # --- LR2: set theory ---
    two_set_cases = [
        (120, 55, 48, 30, 47),   # n(A)=55, n(B)=48, n(A∩B)=30, neither=47
        (200, 90, 75, 40, 75),
        (150, 70, 60, 25, 45),
        (180, 80, 65, 35, 70),
        (250, 110, 95, 50, 95),
        (100, 45, 40, 18, 33),
        (300, 140, 120, 60, 100),
        (90, 42, 38, 15, 25),
        (160, 75, 58, 28, 55),
        (220, 100, 88, 45, 77),
    ]
    for universal, a, b, ab, neither in two_set_cases:
        out.append(nr(
            f"In a group of ${universal}$ people, ${a}$ enjoy hiking, ${b}$ enjoy cycling, "
            f"and ${ab}$ enjoy both. How many enjoy neither activity? Record the integer answer.",
            str(neither),
            f"$n(H \\cup C) = {a} + {b} - {ab} = {a + b - ab}$. "
            f"Neither $= {universal} - {a + b - ab} = {neither}$.",
            "Students add the two group sizes without subtracting the overlap.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Solving a two-set Venn problem for elements outside the union",
            difficulty="Medium", estimated_time_seconds=90,
        ))
        only_a = a - ab
        out.append(nr(
            f"A survey of ${universal}$ students shows ${a}$ take art, ${b}$ take drama, "
            f"and ${ab}$ take both. How many take art only? Record the integer answer.",
            str(only_a),
            f"Art only $= n(A) - n(A \\cap B) = {a} - {ab} = {only_a}$.",
            "Students report the full art enrolment as art-only without removing the overlap.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Finding the count in one region of a two-set Venn diagram",
            difficulty="Easy", estimated_time_seconds=75,
        ))

    for u, a, b, ab in [(100, 50, 40, 20), (80, 35, 42, 12), (150, 70, 55, 25),
                        (200, 88, 76, 30), (60, 28, 32, 10)]:
        union = a + b - ab
        out.append(nr(
            f"Given universal set $U$ with $|U| = {u}$, $|A| = {a}$, $|B| = {b}$, "
            f"and $|A \\cap B| = {ab}$, what is $|A \\cup B|$? Record the integer answer.",
            str(union),
            f"$|A \\cup B| = {a} + {b} - {ab} = {union}$.",
            "Students add $|A|$ and $|B|$ without subtracting the intersection.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Applying the union formula for two finite sets",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    three_set_cases = [
        (200, 80, 70, 60, 25, 20, 15, 10),
        (150, 60, 55, 50, 18, 15, 12, 8),
        (180, 75, 68, 62, 22, 18, 14, 9),
        (250, 95, 88, 80, 30, 25, 20, 12),
        (120, 50, 45, 40, 15, 12, 10, 6),
    ]
    for u, a, b, c, ab, ac, bc, abc in three_set_cases:
        union = a + b + c - ab - ac - bc + abc
        neither = u - union
        out.append(nr(
            f"In a class of ${u}$ students: ${a}$ study French, ${b}$ study Spanish, "
            f"${c}$ study German; ${ab}$ study French and Spanish, ${ac}$ French and German, "
            f"${bc}$ Spanish and German, and ${abc}$ study all three. "
            f"How many study at least one of these languages? Record the integer answer.",
            str(union),
            f"Inclusion-exclusion: ${a}+{b}+{c}-{ab}-{ac}-{bc}+{abc} = {union}$.",
            "Students forget to add back the triple intersection count.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Applying inclusion-exclusion for three overlapping sets",
            difficulty="Hard", estimated_time_seconds=120,
        ))
        out.append(nr(
            f"Using the same class of ${u}$ students with language counts "
            f"(${a}$ French, ${b}$ Spanish, ${c}$ German, overlaps ${ab}$, ${ac}$, ${bc}$, ${abc}$), "
            f"how many study none of the three languages? Record the integer answer.",
            str(neither),
            f"At least one $= {union}$. None $= {u} - {union} = {neither}$.",
            "Students subtract only one overlap from the total enrolled in languages.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Finding complement count in a three-set universal set",
            difficulty="Hard", estimated_time_seconds=115,
        ))

    set_ops = [
        ("A = {2, 4, 6, 8} and B = {1, 2, 3, 4}", "A \\cap B", "{2, 4}", "{1, 3}", "{6, 8}", "{2, 3, 4}"),
        ("A = {1, 3, 5, 7} and B = {2, 3, 4, 5}", "A \\cup B", "{1, 2, 3, 4, 5, 7}", "{3, 5}", "{1, 7}", "{2, 4}"),
        ("A = {x | x is even, 1 < x < 10} and B = {x | x is prime, 1 < x < 10}",
         "A \\cap B", "{2}", "{4, 6, 8}", "{3, 5, 7}", "{2, 3, 5, 7}"),
        ("U = {1, 2, 3, 4, 5}, A = {1, 2, 3}", "A'", "{4, 5}", "{1, 2}", "{2, 3, 4}", "{1, 5}"),
    ]
    for given, op, correct, d1, d2, d3 in set_ops:
        out.append(mc(
            f"Given {given}, what is ${op}$?",
            f"${correct}$",
            [f"${d1}$", f"${d2}$", f"${d3}$"],
            f"Evaluate the set operation directly: ${op} = {correct}$.",
            "Students confuse union with intersection or forget complement is relative to $U$.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Evaluating basic set operations with roster notation",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for a_only, b_only, both in [(25, 18, 12), (30, 22, 15), (40, 28, 20), (35, 20, 10)]:
        total = a_only + b_only + both
        out.append(mc(
            f"A Venn diagram shows ${a_only}$ elements in $A$ only, ${b_only}$ in $B$ only, "
            f"and ${both}$ in $A \\cap B$. Which value equals $|A \\cup B|$?",
            f"${total}$",
            [f"${a_only + b_only}$", f"${both}$", f"${a_only + both}$"],
            f"$|A \\cup B| = {a_only} + {b_only} + {both} = {total}$.",
            "Students omit the intersection region when summing.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Interpreting regions of a two-set Venn diagram",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for n in range(8):
        a, b = rng.randint(20, 60), rng.randint(20, 60)
        ab = rng.randint(5, min(a, b) - 5)
        u = rng.randint(a + b - ab + 5, a + b - ab + 40)
        neither = u - (a + b - ab)
        if neither < 0:
            continue
        out.append(nr(
            f"At a community centre, ${u}$ members were surveyed. "
            f"${a}$ use the gym, ${b}$ use the pool, and ${ab}$ use both facilities. "
            f"How many members use neither facility? Record the integer answer.",
            str(neither),
            f"Union $= {a + b - ab}$. Neither $= {u} - {a + b - ab} = {neither}$.",
            "Treating gym and pool users as disjoint groups.",
            topic=TOPIC, outcome_code="LR2",
            skill_tested="Solving contextual two-set survey problem",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    return out
