"""Counting Methods — P4, P5, P6."""

import math
import random
from collections import Counter
from math30_2_questions.helpers import mc, nr

TOPIC = "Counting Methods"


def _perm(n: int, r: int) -> int:
    return math.factorial(n) // math.factorial(n - r)


def _comb(n: int, r: int) -> int:
    return math.factorial(n) // (math.factorial(r) * math.factorial(n - r))


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- P4: Fundamental Counting Principle ---
    fcp_cases = [
        (4, 3, 12, "shirt colors", "pant styles"),
        (5, 4, 20, "entree options", "dessert options"),
        (3, 3, 9, "morning activities", "afternoon activities"),
        (6, 2, 12, "bus routes", "return routes"),
        (4, 5, 20, "appetizers", "main courses"),
        (3, 4, 12, "fabric colors", "button styles"),
        (5, 3, 15, "workshop topics", "time slots"),
        (2, 6, 12, "entrance doors", "exit doors"),
        (7, 2, 14, "questionnaire versions", "language options"),
        (4, 4, 16, "tile colors", "grout colors"),
    ]
    for a, b, prod, label_a, label_b in fcp_cases:
        out.append(nr(
            f"A menu offers ${a}$ {label_a} and ${b}$ {label_b}. "
            f"How many different meal combinations are possible? Record the integer answer.",
            str(prod),
            f"FCP: ${a} \\times {b} = {prod}$.",
            "Students add the options instead of multiplying.",
            topic=TOPIC, outcome_code="P4",
            skill_tested="Applying the fundamental counting principle to two stages",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for s1, s2, s3, prod in [
        (3, 4, 2, 24), (2, 5, 3, 30), (4, 3, 3, 36), (5, 2, 4, 40),
        (3, 3, 5, 45), (6, 2, 2, 24), (4, 4, 2, 32), (3, 5, 2, 30),
    ]:
        out.append(nr(
            f"A travel package is built by choosing one option from each stage: "
            f"${s1}$ departure cities, ${s2}$ hotels, and ${s3}$ activity passes. "
            f"How many distinct packages exist? Record the integer answer.",
            str(prod),
            f"${s1} \\times {s2} \\times {s3} = {prod}$.",
            "Students multiply only two of the three stages.",
            topic=TOPIC, outcome_code="P4",
            skill_tested="Applying FCP across three independent stages",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for digits, length, total in [
        (5, 3, 125), (4, 4, 256), (6, 2, 36), (3, 5, 243), (7, 2, 49),
        (5, 2, 25), (8, 2, 64), (4, 3, 64), (6, 3, 216), (9, 2, 81),
    ]:
        out.append(nr(
            f"A code uses ${length}$ characters chosen from ${digits}$ distinct symbols, "
            f"with repetition allowed. How many codes are possible? Record the integer answer.",
            str(total),
            f"Each position has ${digits}$ choices: ${digits}^{length} = {total}$.",
            "Students use permutation formula when repetition is allowed.",
            topic=TOPIC, outcome_code="P4",
            skill_tested="Counting codes with repetition using FCP",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    for n, r, ans in [(5, 2, 20), (6, 2, 30), (7, 2, 42), (8, 3, 336), (5, 3, 60),
                      (9, 2, 72), (6, 3, 120), (10, 2, 90), (7, 3, 210), (8, 2, 56)]:
        out.append(mc(
            f"How many ways can ${r}$ different awards be distributed to ${n}$ distinct nominees "
            f"if each award goes to a different person?",
            f"${_perm(n, r)}$",
            [f"${_comb(n, r)}$", f"${n ** r}$", f"${math.factorial(r)}$"],
            f"Ordered selection without repetition: $_r P_n = {_perm(n, r)}$.",
            "Students use combinations when order of awards matters.",
            topic=TOPIC, outcome_code="P4",
            skill_tested="Distinguishing ordered selection in a counting context",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # --- P5: Permutations ---
    for n in range(4, 11):
        out.append(nr(
            f"In how many ways can ${n}$ distinct books be arranged on a shelf? "
            f"Record the integer answer.",
            str(math.factorial(n)),
            f"${n}! = {math.factorial(n)}$.",
            "Students use $n^2$ or $_n P_2$ instead of $n!$.",
            topic=TOPIC, outcome_code="P5",
            skill_tested="Calculating linear permutations of distinct objects",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for n, r, ans in [(7, 3, 210), (8, 4, 1680), (9, 2, 72), (6, 4, 360),
                      (10, 3, 720), (7, 4, 840), (8, 2, 56), (9, 3, 504),
                      (6, 2, 30), (10, 2, 90), (5, 3, 60), (8, 3, 336)]:
        out.append(nr(
            f"A committee chair must rank the top ${r}$ finishers from ${n}$ contestants. "
            f"How many different rankings are possible? Record the integer answer.",
            str(ans),
            f"$_{{{r}}}P_{{{n}}} = {ans}$.",
            "Students use $_{{{r}}}C_{{{n}}}$ when order matters.",
            topic=TOPIC, outcome_code="P5",
            skill_tested="Calculating permutations for ranked selections",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    # Permutations with identical elements
    word_cases = [
        ("MISS", "M once, I twice, S twice"),
        ("PEEP", "P twice, E twice"),
        ("LEVEL", "L twice, E twice"),
        ("BANANA", "B once, A three times, N two times"),
        ("TENNESSEE", "T twice, E three times, N two times, S twice"),
        ("BOOKKEEPER", "B once, O twice, K twice, E three times"),
    ]
    for word, note in word_cases:
        counts = Counter(word)
        numer = math.factorial(len(word))
        denom = 1
        for cnt in counts.values():
            denom *= math.factorial(cnt)
        ans = numer // denom
        out.append(nr(
            f"How many distinct arrangements of the letters in {word} are possible? "
            f"Record the integer answer.",
            str(ans),
            f"{note}: $\\frac{{{len(word)}!}}{{\\text{{repeated factorials}}}} = {ans}$.",
            "Students divide by the wrong factorial for repeated letters.",
            topic=TOPIC, outcome_code="P5",
            skill_tested="Permutations with identical elements",
            difficulty="Hard", estimated_time_seconds=110,
        ))

    # One restriction: must sit together or apart — use MC for restriction logic
    for n in [5, 6, 7, 8]:
        together = math.factorial(n - 1) * 2
        out.append(nr(
            f"${n}$ students line up for a photo. Two specific students insist on standing "
            f"next to each other. How many lineups are possible? Record the integer answer.",
            str(together),
            f"Treat the pair as one block: $({n-1})! \\times 2 = {together}$.",
            "Students forget the internal order of the pair (multiply by 2).",
            topic=TOPIC, outcome_code="P5",
            skill_tested="Permutations with one adjacency restriction",
            difficulty="Hard", estimated_time_seconds=100,
        ))

    for n, blocked in [(5, 1), (6, 2), (7, 1), (5, 2)]:
        ans = math.factorial(n - 1)
        out.append(nr(
            f"${n}$ people stand in a line, but one specific position (position ${blocked}$ "
            f"from the left) is blocked by equipment. How many valid lineups remain? "
            f"Record the integer answer.",
            str(ans),
            f"Arrange ${n}-1$ people in the remaining positions: $({n}-1)! = {ans}$.",
            "Students subtract 1 from $n!$ instead of removing one slot properly.",
            topic=TOPIC, outcome_code="P5",
            skill_tested="Permutations with one position restriction",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # --- P6: Combinations ---
    for n, r, ans in [(8, 3, 56), (10, 4, 210), (12, 2, 66), (9, 5, 126),
                      (7, 3, 35), (11, 2, 55), (10, 3, 120), (8, 4, 70),
                      (9, 4, 126), (12, 3, 220), (6, 3, 20), (15, 2, 105),
                      (14, 3, 364), (13, 4, 715), (8, 5, 56), (10, 5, 252)]:
        out.append(nr(
            f"From ${n}$ candidates, how many ways can a team of ${r}$ be chosen "
            f"if order does not matter? Record the integer answer.",
            str(ans),
            f"$_{{{r}}}C_{{{n}}} = {ans}$.",
            "Students use permutation when order is irrelevant.",
            topic=TOPIC, outcome_code="P6",
            skill_tested="Calculating combinations for unordered selection",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # Multi-case combinations
    combo_cases = [
        (5, 3, 7, 2), (6, 2, 8, 3), (4, 2, 9, 2), (7, 4, 6, 1), (5, 2, 5, 2),
    ]
    for n1, r1, n2, r2 in combo_cases:
        c1, c2 = _comb(n1, r1), _comb(n2, r2)
        ans = c1 * c2
        out.append(nr(
            f"A council must select ${r1}$ members from ${n1}$ candidates in Region A "
            f"and ${r2}$ members from ${n2}$ candidates in Region B. "
            f"How many combined selections are possible? Record the integer answer.",
            str(ans),
            f"FCP on combinations: $_{{{r1}}}C_{{{n1}}} \\times $_{{{r2}}}C_{{{n2}}} "
            f"= {c1} \\times {c2} = {ans}$.",
            "Students add the combination counts instead of multiplying.",
            topic=TOPIC, outcome_code="P6",
            skill_tested="Combining independent combination counts",
            difficulty="Hard", estimated_time_seconds=105,
        ))

    for n in [6, 7, 8, 9, 10]:
        handshakes = n * (n - 1) // 2
        out.append(nr(
            f"At a meeting, ${n}$ people each shake hands once with every other person. "
            f"How many handshakes occur? Record the integer answer.",
            str(handshakes),
            f"$_2 C_{{{n}}} = {handshakes}$.",
            "Students use $n(n-1)$ and forget to divide by 2.",
            topic=TOPIC, outcome_code="P6",
            skill_tested="Applying combinations to handshake problems",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    for n, r in [(10, 6), (12, 8), (9, 4), (11, 5)]:
        ans = _comb(n, r)
        out.append(mc(
            f"Which expression equals the number of ways to choose ${r}$ items from ${n}$ "
            f"when order is not important?",
            f"$\\dfrac{{{n}!}}{{{r}!({n}-{r})!}}$",
            [
                f"$\\dfrac{{{n}!}}{{{n}-{r}!}}$",
                f"${n}^{r}$",
                f"$\\dfrac{{{r}!}}{{{n}!}}$",
            ],
            f"Combination formula: $_{{{r}}}C_{{{n}}} = \\dfrac{{n!}}{{r!(n-r)!}} = {ans}$.",
            "Students select the permutation formula.",
            topic=TOPIC, outcome_code="P6",
            skill_tested="Identifying the combination formula",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for _ in range(6):
        n = rng.randint(8, 14)
        r = rng.randint(2, min(5, n - 2))
        ans = _comb(n, r)
        out.append(nr(
            f"A coach chooses ${r}$ players from a roster of ${n}$ for a tournament squad. "
            f"How many different squads are possible? Record the integer answer.",
            str(ans),
            f"$_{{{r}}}C_{{{n}}} = {ans}$.",
            "Using permutation because player names could be listed differently.",
            topic=TOPIC, outcome_code="P6",
            skill_tested="Solving contextual combination problem",
            difficulty="Medium", estimated_time_seconds=75,
        ))

    return out
