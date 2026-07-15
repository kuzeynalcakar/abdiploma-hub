"""Multiple-choice choice ordering helpers for question banks.

Generators must shuffle choices before export so the keyed correct answer is
not always first. Export pipelines should call ``assert_mc_position_balanced``.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Any, Sequence

# Hard fail if any letter exceeds this share of MC items.
MAX_CORRECT_POSITION_SHARE = 0.35
TARGET_POSITION_LABELS = ("A", "B", "C", "D")


def shuffle_mc_choices(
    choices: Sequence[dict[str, Any]],
    *,
    rng: random.Random | None = None,
) -> list[dict[str, Any]]:
    """Return a shuffled copy of MC choice dicts (preserves each is_correct)."""
    if len(choices) < 2:
        return [dict(c) for c in choices]
    out = [dict(c) for c in choices]
    (rng or random).shuffle(out)
    return out


def correct_position_counts(
    questions: Sequence[dict[str, Any]],
) -> Counter[str]:
    """Count which letter (A–D) holds is_correct for Multiple Choice items."""
    counts: Counter[str] = Counter()
    for q in questions:
        qtype = str(q.get("question_type") or "").strip().lower().replace(" ", "_")
        if qtype not in {"multiple_choice", "multiplechoice"}:
            continue
        choices = q.get("choices") or []
        if not choices:
            continue
        idx = next(
            (i for i, c in enumerate(choices) if c.get("is_correct") is True),
            None,
        )
        if idx is None:
            counts["NONE"] += 1
        elif idx < 4:
            counts[TARGET_POSITION_LABELS[idx]] += 1
        else:
            counts[str(idx)] += 1
    return counts


def assert_mc_position_balanced(
    questions: Sequence[dict[str, Any]],
    *,
    max_share: float = MAX_CORRECT_POSITION_SHARE,
    label: str = "MC bank",
) -> Counter[str]:
    """Fail if any correct-answer letter exceeds ``max_share`` of MC items.

    Target after shuffle is roughly 20–30% per letter; ``max_share`` (default
    35%) is the hard generation/import gate against obvious bias.
    """
    counts = correct_position_counts(questions)
    total = sum(counts[letter] for letter in TARGET_POSITION_LABELS)
    if total == 0:
        return counts
    if counts.get("NONE", 0):
        raise ValueError(
            f"{label}: {counts['NONE']} MC question(s) have no is_correct=True choice"
        )
    biased: list[str] = []
    for letter in TARGET_POSITION_LABELS:
        share = counts[letter] / total
        if share > max_share:
            biased.append(f"{letter}={counts[letter]}/{total} ({share:.1%})")
    if biased:
        detail = ", ".join(
            f"{letter}={counts[letter]}" for letter in TARGET_POSITION_LABELS
        )
        raise ValueError(
            f"{label}: correct-answer position bias exceeds {max_share:.0%} "
            f"({'; '.join(biased)}). Distribution: {detail}. "
            "Shuffle choices before export and re-run."
        )
    return counts


def format_position_report(counts: Counter[str]) -> str:
    total = sum(counts[letter] for letter in TARGET_POSITION_LABELS) or 1
    parts = [
        f"{letter}={counts[letter]} ({counts[letter] / total:.1%})"
        for letter in TARGET_POSITION_LABELS
    ]
    return "; ".join(parts)
