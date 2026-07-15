"""Tests for practice streak tracking."""

import unittest
from datetime import date, timedelta

from app.models import User
from app.services.practice_streak import update_practice_streak


class PracticeStreakTests(unittest.TestCase):
    def _user(self, streak=0, last=None):
        return User(
            name="Streak Test",
            email="streak.test@example.com",
            password_hash="hash",
            practice_streak=streak,
            last_practice_date=last,
        )

    def test_first_practice_starts_streak(self):
        user = self._user()
        today = date(2026, 7, 11)
        result = update_practice_streak(user, today)
        self.assertEqual(result, 1)
        self.assertEqual(user.last_practice_date, today)

    def test_consecutive_day_increments_streak(self):
        today = date(2026, 7, 11)
        user = self._user(streak=4, last=today - timedelta(days=1))
        result = update_practice_streak(user, today)
        self.assertEqual(result, 5)

    def test_same_day_does_not_increment(self):
        today = date(2026, 7, 11)
        user = self._user(streak=5, last=today)
        result = update_practice_streak(user, today)
        self.assertEqual(result, 5)


if __name__ == "__main__":
    unittest.main()
