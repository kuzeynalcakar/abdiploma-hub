"""Tests for learning impact metrics."""

import unittest

from app.database.session import SessionLocal
from app.models import User
from app.services.progress_impact import compute_learning_impact


class ProgressImpactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.database.seed_weakness_test_data import seed_weakness_test_data

        cls.db = SessionLocal()
        cls.seed = seed_weakness_test_data(cls.db)
        cls.user = (
            cls.db.query(User)
            .filter(User.email == cls.seed["user_email"])
            .first()
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_impact_metrics_from_real_data(self):
        impact = compute_learning_impact(self.db, self.user.id)
        self.assertGreater(impact["questions_completed"], 0)
        self.assertGreaterEqual(impact["practice_sessions"], 0)
        self.assertGreaterEqual(impact["overall_accuracy"], 0.0)


if __name__ == "__main__":
    unittest.main()
