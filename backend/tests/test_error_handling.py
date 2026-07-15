"""Tests for production-safe API error handling."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class ErrorHandlingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app, raise_server_exceptions=False)

    def test_validation_error_strips_input(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email", "password": "secret-password-value"},
        )
        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertIn("detail", body)
        dumped = str(body)
        self.assertNotIn("secret-password-value", dumped)
        for item in body["detail"]:
            self.assertNotIn("input", item)
            self.assertNotIn("ctx", item)
            self.assertIn("msg", item)

    def test_login_wrong_password_safe_message(self):
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "Incorrect email or password.",
        )

    def test_expired_session_message(self):
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally-invalid-token"},
        )
        self.assertEqual(response.status_code, 401)
        detail = response.json()["detail"]
        self.assertIn("Session expired", detail)
        self.assertNotIn("sqlite", detail.lower())
        self.assertNotIn("traceback", detail.lower())

    def test_invalid_quiz_request(self):
        response = self.client.get(
            "/api/v1/quiz/available-count",
            params={"course_id": "not-a-number"},
        )
        self.assertEqual(response.status_code, 422)
        dumped = str(response.json())
        self.assertNotIn("Traceback", dumped)
        self.assertNotIn("password", dumped.lower())
        for item in response.json()["detail"]:
            self.assertNotIn("input", item)

    def test_unhandled_exception_safe_500(self):
        probe_path = "/api/v1/__error_probe"

        @app.get(probe_path)
        def _probe():
            raise RuntimeError("INTERNAL_PATH_/var/db/secret.db")

        try:
            response = self.client.get(probe_path)
            self.assertEqual(response.status_code, 500)
            body = response.json()
            self.assertEqual(
                body["detail"],
                "Something went wrong. Please try again.",
            )
            dumped = str(body).lower()
            self.assertNotIn("traceback", dumped)
            self.assertNotIn("/var/db", dumped)
            self.assertNotIn("secret.db", dumped)
            self.assertNotIn("runtimeerror", dumped)
        finally:
            app.router.routes[:] = [
                route
                for route in app.router.routes
                if getattr(route, "path", None) != probe_path
            ]


if __name__ == "__main__":
    unittest.main()
