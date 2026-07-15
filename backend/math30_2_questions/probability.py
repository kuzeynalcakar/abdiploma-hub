"""Probability — P1, P2, P3."""

import random
from math30_2_questions.helpers import mc, nr

TOPIC = "Probability"


def _odds_to_prob(fav: int, against: int) -> float:
    return round(fav / (fav + against), 4)


def _prob_to_odds_fav(p: float) -> tuple[int, int]:
    """Return integer odds favour simplified-ish."""
    against = round((1 - p) / p, 2)
    fav = 1
    return fav, int(against * fav) if against == int(against) else None


def generate(rng: random.Random) -> list[dict]:
    out: list[dict] = []

    # --- P1: odds and probability statements ---
    odds_cases = [
        (3, 7, 0.3), (5, 2, 0.7143), (1, 4, 0.2), (7, 3, 0.7), (2, 8, 0.2),
        (4, 1, 0.8), (9, 1, 0.9), (1, 9, 0.1), (3, 2, 0.6), (6, 4, 0.6),
        (5, 5, 0.5), (2, 3, 0.4), (8, 2, 0.8), (1, 1, 0.5), (7, 1, 0.875),
    ]
    for fav, against, prob in odds_cases:
        out.append(nr(
            f"The odds in favour of event $E$ are ${fav}:{against}$. "
            f"What is $P(E)$? Express as a decimal rounded to four decimal places.",
            f"{prob:.4f}",
            f"$P(E) = \\dfrac{{{fav}}}{{{fav}+{against}}} = {prob:.4f}$.",
            "Students use part-part odds as the probability directly.",
            topic=TOPIC, outcome_code="P1",
            skill_tested="Converting odds in favour to probability",
            difficulty="Easy", estimated_time_seconds=70,
        ))
        prob_round = round(fav / (fav + against), 2)
        against_calc = round((1 - prob_round) / prob_round, 1) if prob_round > 0 else 0
        if against_calc == int(against_calc):
            out.append(nr(
                f"If $P(E) = {prob_round}$, what are the odds against $E$ "
                f"expressed as the against value when odds are written $1:{int(against_calc)}$? "
                f"Record the integer against value.",
                str(int(against_calc)),
                f"Odds against: $\\dfrac{{1-{prob_round}}}{{{prob_round}}} "
                f"\\approx 1:{int(against_calc)}$.",
                "Students report odds in favour instead of odds against.",
                topic=TOPIC, outcome_code="P1",
                skill_tested="Converting probability to odds against",
                difficulty="Medium", estimated_time_seconds=85,
            ))

    validity_mc = [
        ("$P(A) = 1.2$", "A probability cannot exceed 1."),
        ("Odds in favour of $B$ are $-3:5$", "Odds counts must be non-negative."),
        ("$P(C) = -0.05$", "Probability must be between 0 and 1 inclusive."),
        ("$P(D) + P(D') = 1.5$", "Complement probabilities must sum to 1."),
        ("Odds against $F$ are $2:0$", "Odds against with zero is invalid."),
    ]
    for stmt, reason in validity_mc:
        out.append(mc(
            f"Which statement about the following claim is correct? {stmt}",
            f"Invalid — {reason}",
            [
                "Valid — any non-negative value is acceptable.",
                "Valid — odds may be negative.",
                "Valid — complements may sum above 1.",
            ],
            f"{reason}",
            "Students accept probabilities outside $[0,1]$.",
            topic=TOPIC, outcome_code="P1",
            skill_tested="Assessing validity of a probability statement",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for fav, against in [(4, 6), (2, 5), (7, 2), (3, 8), (5, 4)]:
        p = _odds_to_prob(fav, against)
        out.append(mc(
            f"Event $G$ has odds in favour of ${fav}:{against}$. "
            f"Which probability is correct?",
            f"${p:.4f}$",
            [f"${fav/(fav+against+1):.4f}$", f"${against/(fav+against):.4f}$", f"${fav/against:.4f}$"],
            f"$P(G) = \\dfrac{{{fav}}}{{{fav}+{against}}} = {p:.4f}$.",
            "Using the against part as the numerator.",
            topic=TOPIC, outcome_code="P1",
            skill_tested="Selecting correct probability from given odds",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    # Ranking by likelihood — MC not NR (no sequence codes)
    rank_sets = [
        ((0.15, 0.35, 0.22, 0.28), "Event 2", "Event 4", "Event 3", "Event 1"),
        ((0.08, 0.42, 0.30, 0.20), "Event 2", "Event 3", "Event 4", "Event 1"),
        ((0.25, 0.25, 0.40, 0.10), "Event 3", "Event 1", "Event 2", "Event 4"),
    ]
    for probs, most, second, third, least in rank_sets:
        labels = [f"Event {i+1} ({p})" for i, p in enumerate(probs)]
        out.append(mc(
            f"Four events have probabilities: {', '.join(labels)}. "
            f"Which list ranks them from most likely to least likely?",
            f"{most}, {second}, {third}, {least}",
            [
                f"{least}, {third}, {second}, {most}",
                f"{second}, {most}, {third}, {least}",
                f"{most}, {third}, {second}, {least}",
            ],
            f"Descending order: {most} > {second} > {third} > {least}.",
            "Students rank by odds wording rather than numeric probability.",
            topic=TOPIC, outcome_code="P1",
            skill_tested="Comparing relative likelihood of events",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # --- P2: mutually exclusive and non-mutually exclusive ---
    me_cases = [
        (0.4, 0.35, 0.75),
        (0.25, 0.55, 0.80),
        (0.6, 0.2, 0.80),
        (0.15, 0.70, 0.85),
        (0.33, 0.42, 0.75),
        (0.5, 0.5, 1.0),
        (0.12, 0.63, 0.75),
        (0.45, 0.45, 0.90),
    ]
    for pa, pb, ans in me_cases:
        out.append(nr(
            f"Events $A$ and $B$ are mutually exclusive with $P(A)={pa}$ and $P(B)={pb}$. "
            f"What is $P(A \\cup B)$? Express as a decimal.",
            f"{ans:.2f}" if ans != int(ans) else str(int(ans)),
            f"Mutually exclusive: $P(A \\cup B) = {pa} + {pb} = {ans}$.",
            "Students subtract an overlap that does not exist.",
            topic=TOPIC, outcome_code="P2",
            skill_tested="Probability of union for mutually exclusive events",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    nme_cases = [
        (0.5, 0.4, 0.2, 0.7),
        (0.6, 0.5, 0.25, 0.85),
        (0.35, 0.45, 0.15, 0.65),
        (0.7, 0.55, 0.3, 0.95),
        (0.4, 0.6, 0.1, 0.9),
        (0.25, 0.55, 0.1, 0.7),
        (0.55, 0.35, 0.12, 0.78),
        (0.48, 0.52, 0.18, 0.82),
    ]
    for pa, pb, pab, ans in nme_cases:
        out.append(nr(
            f"Events $A$ and $B$ are not mutually exclusive. "
            f"$P(A)={pa}$, $P(B)={pb}$, $P(A \\cap B)={pab}$. "
            f"What is $P(A \\cup B)$? Express as a decimal.",
            f"{ans:.2f}",
            f"$P(A \\cup B) = {pa} + {pb} - {pab} = {ans}$.",
            "Students add probabilities without subtracting the intersection.",
            topic=TOPIC, outcome_code="P2",
            skill_tested="Applying inclusion-exclusion for overlapping events",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    for pa, pb, pab in [(0.45, 0.40, 0.15), (0.55, 0.50, 0.20), (0.3, 0.35, 0.1)]:
        only_a = round(pa - pab, 2)
        out.append(nr(
            f"In a Venn diagram for events $A$ and $B$, $P(A)={pa}$, $P(B)={pb}$, "
            f"and $P(A \\cap B)={pab}$. What is $P(A \\text{{ only}})$? "
            f"Express as a decimal.",
            f"{only_a:.2f}",
            f"$P(A \\text{{ only}}) = P(A) - P(A \\cap B) = {pa} - {pab} = {only_a}$.",
            "Students give $P(A)$ without removing the overlap.",
            topic=TOPIC, outcome_code="P2",
            skill_tested="Finding probability of a single Venn region",
            difficulty="Medium", estimated_time_seconds=80,
        ))

    # --- P3: two events (independent and dependent) ---
    indep_cases = [
        (0.5, 0.4, 0.2), (0.6, 0.3, 0.18), (0.25, 0.8, 0.2),
        (0.7, 0.5, 0.35), (0.4, 0.6, 0.24), (0.55, 0.55, 0.3025),
        (0.33, 0.5, 0.165), (0.75, 0.2, 0.15),
    ]
    for pa, pb, ans in indep_cases:
        out.append(nr(
            f"Events $X$ and $Y$ are independent with $P(X)={pa}$ and $P(Y)={pb}$. "
            f"What is $P(X \\cap Y)$? Express as a decimal rounded to four decimal places.",
            f"{ans:.4f}",
            f"Independent: $P(X \\cap Y) = ({pa})({pb}) = {ans:.4f}$.",
            "Students add probabilities instead of multiplying.",
            topic=TOPIC, outcome_code="P3",
            skill_tested="Calculating intersection of independent events",
            difficulty="Easy", estimated_time_seconds=70,
        ))

    dep_cases = [
        (0.4, 0.5, 0.2), (0.6, 0.25, 0.15), (0.5, 0.6, 0.3),
        (0.3, 0.7, 0.21), (0.55, 0.4, 0.22), (0.25, 0.5, 0.125),
    ]
    for pa, pb_given_a, ans in dep_cases:
        out.append(nr(
            f"Events $M$ and $N$ are dependent. $P(M)={pa}$ and $P(N|M)={pb_given_a}$. "
            f"What is $P(M \\cap N)$? Express as a decimal.",
            f"{ans:.2f}",
            f"$P(M \\cap N) = P(M) \\cdot P(N|M) = {pa} \\times {pb_given_a} = {ans}$.",
            "Students multiply $P(M)$ and $P(N)$ as if independent.",
            topic=TOPIC, outcome_code="P3",
            skill_tested="Calculating intersection of dependent events",
            difficulty="Medium", estimated_time_seconds=90,
        ))

    # Card/dice contextual
    dice_cases = [
        ("even", 3, 6, 0.5), ("greater than 4", 2, 6, 1/3), ("less than 3", 2, 6, 1/3),
        ("a 5", 1, 6, 1/6), ("at least 4", 3, 6, 0.5),
    ]
    for desc, fav, total, prob in dice_cases:
        p = round(fav / total, 4)
        out.append(nr(
            f"A fair six-sided die is rolled once. "
            f"What is the probability of rolling a number {desc}? "
            f"Express as a decimal rounded to four decimal places.",
            f"{p:.4f}",
            f"Favourable outcomes $= {fav}$, total $= {total}$, "
            f"$P = \\dfrac{{{fav}}}{{{total}}} = {p:.4f}$.",
            "Students use incorrect favourable count for the described event.",
            topic=TOPIC, outcome_code="P3",
            skill_tested="Calculating simple single-event probability",
            difficulty="Easy", estimated_time_seconds=60,
        ))

    for red, total in [(5, 10), (8, 20), (3, 12), (7, 15), (4, 16)]:
        p_red = round(red / total, 4)
        p_not = round(1 - p_red, 4)
        out.append(nr(
            f"A bag contains ${red}$ red marbles and ${total - red}$ blue marbles. "
            f"One marble is drawn at random. What is the probability it is not red? "
            f"Express as a decimal rounded to four decimal places.",
            f"{p_not:.4f}",
            f"$P(\\text{{not red}}) = 1 - \\dfrac{{{red}}}{{{total}}} = {p_not:.4f}$.",
            "Students report $P(\\text{{red}})$ instead of the complement.",
            topic=TOPIC, outcome_code="P3",
            skill_tested="Calculating complement probability in a uniform draw",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    two_draw = [
        (13, 52, 12, 51, 0.0471),  # two hearts without replacement approx
    ]
    # P(both hearts) = 13/52 * 12/51
    p = round(13/52 * 12/51, 4)
    out.append(nr(
        f"Two cards are drawn without replacement from a standard 52-card deck. "
        f"What is the probability both cards are hearts? "
        f"Express as a decimal rounded to four decimal places.",
        f"{p:.4f}",
        f"$\\dfrac{{13}}{{52}} \\times \\dfrac{{12}}{{51}} = {p:.4f}$.",
        "Students treat draws as independent with replacement.",
        topic=TOPIC, outcome_code="P3",
        skill_tested="Calculating compound probability without replacement",
        difficulty="Hard", estimated_time_seconds=100,
    ))

    for pa, ans in [(0.65, 0.4225), (0.4, 0.16), (0.8, 0.64)]:
        out.append(mc(
            f"Independent events $S$ and $T$ each have probability ${pa}$. "
            f"Which value equals $P(S \\cap T)$?",
            f"${ans}$",
            [f"${round(pa + pa, 4)}$", f"${round(1 - ans, 4)}$", f"${round(pa * (1 - pa), 4)}$"],
            f"$P(S \\cap T) = ({pa})^2 = {ans}$.",
            "Students add instead of multiply for independent joint events.",
            topic=TOPIC, outcome_code="P3",
            skill_tested="Identifying intersection probability for independent events",
            difficulty="Easy", estimated_time_seconds=65,
        ))

    for _ in range(8):
        pa = round(rng.uniform(0.2, 0.7), 2)
        pb = round(rng.uniform(0.2, 0.7), 2)
        pab = round(min(pa, pb) * rng.uniform(0.1, 0.5), 2)
        if pab > min(pa, pb):
            pab = round(min(pa, pb) * 0.3, 2)
        union = round(pa + pb - pab, 2)
        out.append(nr(
            f"In a survey, $P(\\text{{owns a bike}}) = {pa}$, "
            f"$P(\\text{{owns a helmet}}) = {pb}$, and "
            f"$P(\\text{{owns both}}) = {pab}$. "
            f"What is the probability a randomly selected person owns at least one? "
            f"Express as a decimal.",
            f"{union:.2f}",
            f"$P(A \\cup B) = {pa} + {pb} - {pab} = {union}$.",
            "Assuming bike and helmet owners are disjoint.",
            topic=TOPIC, outcome_code="P2",
            skill_tested="Solving contextual overlapping probability problem",
            difficulty="Medium", estimated_time_seconds=85,
        ))

    return out
