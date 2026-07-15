"""Tests for data-driven weakness analysis."""

import unittest

from app.services.weakness_analysis import (
    STRONG_ACCURACY_THRESHOLD,
    STATUS_NEEDS_PRACTICE,
    STATUS_STRONG,
    TopicAnalysis,
    _analyze_topic,
    build_recommended_action,
    build_why_message,
    compute_weakness_score,
)
from app.models import Topic


class WeaknessScoreTests(unittest.TestCase):
    def test_higher_score_for_low_accuracy(self):
        low = compute_weakness_score(
            accuracy=30.0,
            recent_wrong=8,
            recent_total=12,
            hard_attempted=6,
            hard_wrong=5,
            repeat_mistakes=3,
        )
        high = compute_weakness_score(
            accuracy=90.0,
            recent_wrong=1,
            recent_total=12,
            hard_attempted=6,
            hard_wrong=1,
            repeat_mistakes=0,
        )
        self.assertGreater(low, high)

    def test_why_message_format(self):
        self.assertEqual(
            build_why_message(8, 12),
            "You missed 8 of your last 12 questions",
        )

    def test_why_message_with_skill(self):
        message = build_why_message(
            4,
            10,
            weakest_skill="Trigonometric Identity Transformations",
        )
        self.assertIn("struggling with", message)
        self.assertIn("identity", message.lower())

    def test_recommended_action_for_low_accuracy(self):
        action = build_recommended_action(
            accuracy=35.0,
            weakest_difficulty="hard",
        )
        self.assertIn("easy questions", action)


class TopicClassificationTests(unittest.TestCase):
    def _topic(self, topic_id: int, name: str) -> Topic:
        topic = Topic(id=topic_id, course_id=4, name=name, sort_order=0)
        return topic

    def test_strong_topic_classification(self):
        topic = self._topic(1, "Exponential Functions")
        answers = [
            type(
                "AnswerRecord",
                (),
                {
                    "topic_id": 1,
                    "topic_name": "Exponential Functions",
                    "outcome_code": "RF10",
                    "difficulty": "medium",
                    "is_correct": index < 18,
                    "answered_at": index,
                },
            )()
            for index in range(20)
        ]
        analysis = _analyze_topic(topic, answers, repeat_mistakes=0)
        self.assertEqual(analysis.accuracy, 90.0)
        self.assertEqual(analysis.status, STATUS_STRONG)

    def test_needs_practice_classification(self):
        topic = self._topic(2, "Trigonometric Identities")
        answers = [
            type(
                "AnswerRecord",
                (),
                {
                    "topic_id": 2,
                    "topic_name": "Trigonometric Identities",
                    "outcome_code": "T5",
                    "difficulty": "hard",
                    "is_correct": index < 8,
                    "answered_at": index,
                },
            )()
            for index in range(20)
        ]
        analysis = _analyze_topic(topic, answers, repeat_mistakes=2)
        self.assertEqual(analysis.accuracy, 40.0)
        self.assertEqual(analysis.status, STATUS_NEEDS_PRACTICE)
        self.assertGreater(analysis.weakness_score, 0)


class EmptyStateTests(unittest.TestCase):
    def test_unattempted_topic_is_not_strong(self):
        topic = Topic(id=99, course_id=4, name="Radical Functions", sort_order=0)
        analysis = _analyze_topic(topic, [], repeat_mistakes=0)
        self.assertEqual(analysis.questions_attempted, 0)
        self.assertEqual(analysis.accuracy, 0.0)
        self.assertNotEqual(analysis.status, STATUS_STRONG)


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app.database.seed_weakness_test_data import seed_weakness_test_data
        from app.database.session import SessionLocal
        from app.models import User

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

    def test_seed_student_accuracy(self):
        self.assertEqual(self.seed["identities_accuracy"], 40.0)

    def test_weak_topic_ranking(self):
        from app.services.weakness_analysis import analyze_course_weakness
        from app.models import Course

        course = self.db.query(Course).filter(Course.code == "MATH30-1").first()
        payload = analyze_course_weakness(self.db, self.user.id, course.id)

        self.assertTrue(payload["needs_practice"])
        self.assertEqual(
            payload["needs_practice"][0].topic_name,
            "Trigonometric Identities",
        )
        strong_names = [item.topic_name for item in payload["strong_topics"]]
        self.assertIn("Exponential Functions", strong_names)

    def test_empty_user_has_no_attempted_topics(self):
        from app.services.weakness_analysis import analyze_course_weakness
        from app.models import Course, User

        course = self.db.query(Course).filter(Course.code == "MATH30-1").first()
        empty_user = (
            self.db.query(User)
            .filter(User.email == "empty.weakness@example.com")
            .first()
        )
        if empty_user is None:
            empty_user = User(
                name="Empty Student",
                email="empty.weakness@example.com",
                password_hash="test",
            )
            self.db.add(empty_user)
            self.db.commit()

        payload = analyze_course_weakness(self.db, empty_user.id, course.id)
        self.assertFalse(payload["has_attempted_topics"])
        self.assertEqual(payload["strong_topics"], [])
        self.assertEqual(payload["needs_practice"], [])


if __name__ == "__main__":
    unittest.main()
