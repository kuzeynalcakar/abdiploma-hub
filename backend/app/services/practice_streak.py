"""Simple daily practice streak tracking."""

from __future__ import annotations

from datetime import date, timedelta

from app.models import User


def update_practice_streak(user: User, today: date | None = None) -> int:
    """Record today's practice and return the updated streak count."""
    today = today or date.today()
    last = user.last_practice_date

    if last == today:
        return user.practice_streak or 0

    if last == today - timedelta(days=1):
        user.practice_streak = (user.practice_streak or 0) + 1
    else:
        user.practice_streak = 1

    user.last_practice_date = today
    return user.practice_streak
