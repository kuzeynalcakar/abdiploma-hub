"""Tests for admin authorization and dashboard aggregations."""

import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

# Configure admin env before importing the app.
os.environ["ADMIN_API_KEY"] = "test-admin-key-for-suite"
os.environ["ADMIN_EMAILS"] = "admin@albertaprep.test"

from app.core.admin import is_admin_user, parse_admin_emails  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.database.init_db import init_db  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.main import app  # noqa: E402
from app.models import QuestionReport, User  # noqa: E402
from app.services import admin_stats  # noqa: E402


class AdminAuthUnitTests(unittest.TestCase):
    def test_parse_admin_emails(self):
        with mock.patch.object(
            settings, "admin_emails", "Ada@Example.com, bob@test.com "
        ):
            emails = parse_admin_emails()
        self.assertIn("ada@example.com", emails)
        self.assertIn("bob@test.com", emails)

    def test_is_admin_user(self):
        user = User(id=1, name="Ada", email="admin@albertaprep.test", password_hash="x")
        with mock.patch.object(
            settings, "admin_emails", "admin@albertaprep.test"
        ):
            self.assertTrue(is_admin_user(user))
            user.email = "student@example.com"
            self.assertFalse(is_admin_user(user))


class AdminStatsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_overview_returns_counts(self):
        data = admin_stats.compute_overview(self.db)
        self.assertIn("registered_users", data)
        self.assertGreaterEqual(data["registered_users"], 0)
        self.assertGreaterEqual(data["quiz_attempts"], 0)
        self.assertGreaterEqual(data["total_questions"], 0)
        self.assertIsNone(data["guest_quiz_sessions"])
        self.assertIsInstance(data["recent_registrations"], list)

    def test_analytics_real_only(self):
        data = admin_stats.compute_analytics(self.db)
        self.assertIsNone(data["top_searched_topics"])
        self.assertIn("most_attempted_courses", data)
        self.assertIn("guest_vs_registered", data)

    def test_impact_never_fabricates(self):
        data = admin_stats.compute_impact(self.db)
        for key in (
            "registered_users",
            "quiz_attempts",
            "questions_answered",
            "courses_practiced",
            "feedback_submitted",
            "reports_submitted",
            "students_helped",
            "practice_sessions_completed",
            "daily_practices_completed",
            "strong_topics_mastered",
            "weaknesses_identified",
            "questions_reported",
            "questions_fixed",
            "feedback_received",
            "users_last_7_days",
            "quizzes_last_7_days",
        ):
            self.assertIn(key, data)
            self.assertIsInstance(data[key], int)
            self.assertGreaterEqual(data[key], 0)

    def test_question_quality(self):
        data = admin_stats.compute_question_quality(self.db)
        self.assertIn("unanswered_reports_count", data)
        self.assertIn("questions_with_multiple_reports", data)
        self.assertIn("most_reported_questions", data)
        self.assertIsInstance(data["most_reported_questions"], list)

    def test_overview_masks_email(self):
        data = admin_stats.compute_overview(self.db)
        for user in data["recent_registrations"]:
            self.assertIn("email_masked", user)
            self.assertNotIn("email", user)
            if user["email_masked"] != "—":
                self.assertIn("***@", user["email_masked"])

    def test_db_health(self):
        data = admin_stats.compute_db_health(self.db)
        self.assertEqual(data["health_status"], "ok")
        self.assertGreaterEqual(data["total_questions"], 0)
        self.assertIsInstance(data["questions_by_course"], list)

    def test_report_status_column(self):
        row = self.db.query(QuestionReport).first()
        if row is None:
            self.skipTest("No question reports in database")
        status = getattr(row, "status", None) or "pending"
        self.assertIn(status, ("pending", "resolved", "ignored"))


class AdminApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reload settings from env set at module import time
        settings.admin_api_key = "test-admin-key-for-suite"
        settings.admin_emails = "admin@albertaprep.test"
        init_db()
        cls.client = TestClient(app)

    def test_admin_overview_requires_auth(self):
        response = self.client.get("/api/v1/admin/overview")
        self.assertEqual(response.status_code, 403)

    def test_admin_overview_with_api_key(self):
        response = self.client.get(
            "/api/v1/admin/overview",
            headers={"X-Admin-Key": "test-admin-key-for-suite"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("registered_users", body)
        self.assertIn("daily_active_users", body)

    def test_admin_rejects_bad_key(self):
        response = self.client.get(
            "/api/v1/admin/overview",
            headers={"X-Admin-Key": "wrong-key"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_feedback_and_reports(self):
        headers = {"X-Admin-Key": "test-admin-key-for-suite"}
        feedback = self.client.get("/api/v1/admin/feedback", headers=headers)
        self.assertEqual(feedback.status_code, 200)
        self.assertIn("unread_count", feedback.json())
        reports = self.client.get("/api/v1/admin/reports", headers=headers)
        self.assertEqual(reports.status_code, 200)
        self.assertIn("items", reports.json())
        quality = self.client.get("/api/v1/admin/question-quality", headers=headers)
        self.assertEqual(quality.status_code, 200)
        self.assertIn("unanswered_reports_count", quality.json())
        impact = self.client.get("/api/v1/admin/impact", headers=headers)
        self.assertEqual(impact.status_code, 200)
        self.assertIn("users_last_7_days", impact.json())
        health = self.client.get("/api/v1/admin/health", headers=headers)
        self.assertEqual(health.status_code, 200)
        analytics = self.client.get("/api/v1/admin/analytics", headers=headers)
        self.assertEqual(analytics.status_code, 200)

    def test_report_status_update_sets_timestamp_and_logs(self):
        headers = {"X-Admin-Key": "test-admin-key-for-suite"}
        init_db()
        db = SessionLocal()
        try:
            report = db.query(QuestionReport).first()
            if report is None:
                self.skipTest("No question reports in database")
            report_id = report.id
        finally:
            db.close()

        response = self.client.patch(
            f"/api/v1/admin/reports/{report_id}",
            headers=headers,
            json={"status": "resolved", "admin_note": "Fixed distractor B"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "resolved")
        self.assertIsNotNone(body.get("status_changed_at"))
        self.assertEqual(body.get("admin_note"), "Fixed distractor B")

        from app.models import AdminActionLog

        db = SessionLocal()
        try:
            log = (
                db.query(AdminActionLog)
                .filter(AdminActionLog.entity_id == report_id)
                .order_by(AdminActionLog.id.desc())
                .first()
            )
            self.assertIsNotNone(log)
            self.assertEqual(log.action, "report.resolve")
        finally:
            db.close()

    def test_student_apis_still_ok(self):
        health = self.client.get("/api/v1/health")
        self.assertEqual(health.status_code, 200)
        courses = self.client.get("/api/v1/courses")
        self.assertEqual(courses.status_code, 200)
        stats = self.client.get("/api/v1/stats/platform")
        self.assertEqual(stats.status_code, 200)

    def test_legacy_feedback_admin_with_key(self):
        response = self.client.get(
            "/api/v1/feedback/admin",
            headers={"X-Admin-Key": "test-admin-key-for-suite"},
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
