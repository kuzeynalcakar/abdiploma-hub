"""Tests for daily practice question selection."""

import unittest

from app.database.session import SessionLocal
from app.models import Course, User
from app.services.daily_practice import (
    DAILY_QUESTION_COUNT,
    build_selection_metadata,
    select_daily_questions,
)


class DailyPracticeAlgorithmTests(unittest.TestCase):
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
        cls.course = cls.db.query(Course).filter(Course.code == "MATH30-1").first()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_daily_question_count_is_ten(self):
        self.assertEqual(DAILY_QUESTION_COUNT, 10)

    def test_selects_ten_questions_for_student_with_history(self):
        questions, metadata = select_daily_questions(
            self.db, self.user.id, self.course.id
        )
        self.assertEqual(len(questions), 10)
        self.assertEqual(metadata["allocation"]["weak"], 7)
        self.assertEqual(metadata["allocation"]["medium"], 2)
        self.assertEqual(metadata["allocation"]["review"], 1)

    def test_metadata_records_target_topics(self):
        questions, metadata = select_daily_questions(
            self.db, self.user.id, self.course.id
        )
        self.assertTrue(metadata["target_topics"])
        topic_ids = {item["topic_id"] for item in metadata["target_topics"]}
        question_topic_ids = {question.topic_id for question in questions}
        self.assertTrue(question_topic_ids.issubset(topic_ids | question_topic_ids))

    def test_no_duplicate_questions(self):
        questions, _ = select_daily_questions(
            self.db, self.user.id, self.course.id
        )
        ids = [question.id for question in questions]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
