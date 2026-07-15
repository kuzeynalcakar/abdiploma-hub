"""In-memory ring buffer of recent API errors for admin reliability view.

Stores only sanitized metadata — never passwords, tokens, cookies, or answers.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any

_LOCK = threading.Lock()
_MAX = 50
_errors: deque[dict[str, Any]] = deque(maxlen=_MAX)


_SENSITIVE_FRAGMENTS = (
    "password",
    "token",
    "secret",
    "authorization",
    "cookie",
    "bearer",
    "session",
)


def _sanitize_message(message: str | None) -> str:
    text = (message or "error")[:200]
    lower = text.lower()
    for frag in _SENSITIVE_FRAGMENTS:
        if frag in lower:
            return "sensitive details redacted"
    return text


def record_error(
    *,
    endpoint: str,
    status_code: int,
    error_type: str,
    message: str | None = None,
) -> None:
    entry = {
        "ts": time.time(),
        "endpoint": (endpoint or "/")[:200],
        "status_code": int(status_code),
        "error_type": (error_type or "Error")[:100],
        "message": _sanitize_message(message),
    }
    with _LOCK:
        _errors.appendleft(entry)


def recent_errors(limit: int = 20) -> list[dict[str, Any]]:
    with _LOCK:
        items = list(_errors)[: max(0, min(limit, _MAX))]
    return items


def clear_errors() -> None:
    """Test helper."""
    with _LOCK:
        _errors.clear()

