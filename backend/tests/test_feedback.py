"""Tests for feedback models and platform stats (no HTTP client required)."""

import unittest

from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.models import Course, Question, QuestionReport, QuizFeedback, Topic
from app.services.platform_stats import compute_platform_stats


class FeedbackModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()
        cls.course = cls.db.query(Course).filter(Course.code == "BIO30").first()
        cls.question = (
            cls.db.query(Question)
            .join(Topic)
            .filter(Topic.course_id == cls.course.id, Question.is_active.is_(True))
            .first()
        )

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_create_guest_feedback(self):
        row = QuizFeedback(
            user_id=None,
            course_id=self.course.id,
            quiz_attempt_id=None,
            rating="positive",
            message="Helpful practice",
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        self.assertIsNotNone(row.id)
        self.assertIsNone(row.user_id)
        self.assertEqual(row.rating, "positive")

    def test_create_question_report(self):
        row = QuestionReport(
            question_id=self.question.id,
            user_id=None,
            reason="confusing_wording",
            comment="Stem unclear",
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        self.assertIsNotNone(row.id)
        self.assertEqual(row.reason, "confusing_wording")

    def test_platform_stats_returns_real_counts(self):
        stats = compute_platform_stats(self.db)
        self.assertGreaterEqual(stats["students_helped"], 0)
        self.assertGreaterEqual(stats["questions_completed"], 0)
        self.assertGreaterEqual(stats["practice_sessions"], 0)


class ProgressImpactFieldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_learning_impact_includes_subjects_practiced(self):
        from app.services.progress_impact import compute_learning_impact
        from app.models import User

        user = self.db.query(User).first()
        if user is None:
            self.skipTest("No users in database")
        impact = compute_learning_impact(self.db, user.id)
        self.assertIn("subjects_practiced", impact)
        self.assertGreaterEqual(impact["subjects_practiced"], 0)


if __name__ == "__main__":
    unittest.main()
