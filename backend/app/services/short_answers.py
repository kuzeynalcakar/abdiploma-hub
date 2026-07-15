"""Short-answer / NR helpers: accepted answer lists and normalization."""

from __future__ import annotations

import json
import re
from typing import Any

_SPACE_RE = re.compile(r"\s+")
_PUNCT_EDGE_RE = re.compile(r"^[\s\"'`]+|[\s\"'`.!?,;:]+$")


def parse_accepted_answers_field(raw: Any) -> list[str]:
    """Parse DB/JSON accepted_answers into a clean string list."""
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        values = raw
    elif isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            values = json.loads(text)
        except json.JSONDecodeError:
            # Allow newline- or semicolon-separated fallbacks.
            values = re.split(r"[\n;|]+", text)
    else:
        return []
    out: list[str] = []
    for item in values:
        if item is None:
            continue
        s = str(item).strip()
        if s:
            out.append(s)
    return out


def dump_accepted_answers(values: list[str]) -> str:
    """Serialize accepted answers for DB storage."""
    cleaned: list[str] = []
    seen: set[str] = set()
    for v in values:
        s = str(v).strip()
        if not s:
            continue
        key = normalize_short_answer(s)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(s)
    return json.dumps(cleaned, ensure_ascii=False)


def normalize_short_answer(value: str) -> str:
    """Case/punctuation-insensitive form for short-answer matching."""
    text = str(value).strip().strip("$").strip()
    text = _PUNCT_EDGE_RE.sub("", text)
    text = _SPACE_RE.sub(" ", text)
    return text.casefold()


def coalesce_accepted_answers(
    canonical: str | None,
    accepted_raw: Any = None,
) -> list[str]:
    """Canonical answer first, then variants from accepted_answers."""
    ordered: list[str] = []
    seen: set[str] = set()
    for value in [canonical, *parse_accepted_answers_field(accepted_raw)]:
        if value is None:
            continue
        s = str(value).strip()
        if not s:
            continue
        key = normalize_short_answer(s)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(s)
    return ordered
