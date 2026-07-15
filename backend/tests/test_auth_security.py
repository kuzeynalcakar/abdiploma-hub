"""Authentication security hardening tests."""

from __future__ import annotations

import unittest
from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.rate_limit import reset_rate_limits
from app.core.security import hash_session_token, utcnow
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.models import UserSession


def _unique_email(prefix: str = "sec") -> str:
    return f"{prefix}-{uuid4().hex[:10]}@example.com"


class AuthSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def setUp(self):
        reset_rate_limits()
        # Keep auth rates low for brute-force test; others use defaults.
        self._prev_enabled = settings.rate_limit_enabled
        self._prev_auth = settings.rate_limit_auth_per_minute
        self._prev_public = settings.rate_limit_public_per_minute
        settings.rate_limit_enabled = True
        settings.rate_limit_auth_per_minute = 10
        settings.rate_limit_public_per_minute = 30

    def tearDown(self):
        settings.rate_limit_enabled = self._prev_enabled
        settings.rate_limit_auth_per_minute = self._prev_auth
        settings.rate_limit_public_per_minute = self._prev_public
        reset_rate_limits()

    def _register(self, email: str | None = None, password: str = "SecurePass1") -> dict:
        email = email or _unique_email()
        response = self.client.post(
            "/api/v1/auth/register",
            json={"name": "Security Tester", "email": email, "password": password},
        )
        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertIn("access_token", body)
        self.assertIn("user", body)
        self.assertNotIn("password", str(body).lower())
        self.assertNotIn("password_hash", str(body))
        return body

    def test_normal_login_flow_bearer_only(self):
        email = _unique_email("login")
        self._register(email=email, password="LoginPass9")
        self.client.cookies.clear()

        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "LoginPass9"},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        token = body["access_token"]
        self.assertTrue(token)
        # No session cookie is issued.
        self.assertEqual(len(response.cookies), 0)
        set_cookie = response.headers.get("set-cookie")
        self.assertTrue(set_cookie is None or "albertaprep_session" not in set_cookie)

        # Cookie alone must not authenticate.
        me_cookie = self.client.get("/api/v1/auth/me")
        self.assertEqual(me_cookie.status_code, 401)

        # Bearer auth works.
        me_bearer = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_bearer.status_code, 200)
        self.assertEqual(me_bearer.json()["email"], email)

    def test_session_token_stored_hashed(self):
        body = self._register(email=_unique_email("hash"))
        raw = body["access_token"]
        db = SessionLocal()
        try:
            row = (
                db.query(UserSession)
                .filter(UserSession.token == hash_session_token(raw))
                .first()
            )
            self.assertIsNotNone(row)
            self.assertNotEqual(row.token, raw)
            self.assertEqual(row.token, hash_session_token(raw))
            self.assertIsNotNone(row.expires_at)
        finally:
            db.close()

    def test_active_session_accepted(self):
        body = self._register()
        token = body["access_token"]
        me = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["id"], body["user"]["id"])

    def test_expired_session_rejected(self):
        body = self._register(email=_unique_email("exp"))
        raw = body["access_token"]
        db = SessionLocal()
        try:
            row = (
                db.query(UserSession)
                .filter(UserSession.token == hash_session_token(raw))
                .first()
            )
            self.assertIsNotNone(row)
            row.expires_at = utcnow() - timedelta(minutes=1)
            db.commit()
        finally:
            db.close()

        me = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {raw}"},
        )
        self.assertEqual(me.status_code, 401)
        self.assertIn("Session expired", me.json()["detail"])

        # Row should be deleted
        db = SessionLocal()
        try:
            gone = (
                db.query(UserSession)
                .filter(UserSession.token == hash_session_token(raw))
                .first()
            )
            self.assertIsNone(gone)
        finally:
            db.close()

    def test_invalid_session_rejected(self):
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer totally-invalid-token"},
        )
        self.assertEqual(response.status_code, 401)
        detail = response.json()["detail"]
        self.assertNotIn("traceback", detail.lower())
        self.assertNotIn("sqlite", detail.lower())

    def test_unauthorized_progress_without_session(self):
        self.client.cookies.clear()
        response = self.client.get("/api/v1/progress")
        self.assertEqual(response.status_code, 401)

    def test_password_validation_messages(self):
        weak = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Weak",
                "email": _unique_email("weak"),
                "password": "abcdefgh",
            },
        )
        self.assertEqual(weak.status_code, 422)
        dumped = str(weak.json())
        self.assertNotIn("abcdefgh", dumped)
        self.assertIn("letters and numbers", dumped.lower())

        short = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Short",
                "email": _unique_email("short"),
                "password": "Ab1",
            },
        )
        self.assertEqual(short.status_code, 422)

    def test_brute_force_login_rate_limited(self):
        settings.rate_limit_auth_per_minute = 3
        reset_rate_limits()
        email = _unique_email("brute")
        self._register(email=email, password="BrutePass1")
        reset_rate_limits()

        statuses = []
        for _ in range(5):
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": "wrong-password"},
            )
            statuses.append(response.status_code)
            if response.status_code == 429:
                self.assertEqual(
                    response.json()["detail"],
                    "Too many requests. Please wait a moment and try again.",
                )
                self.assertNotIn("password", response.json()["detail"].lower())
                break
        self.assertIn(429, statuses)

    def test_logout_clears_session(self):
        body = self._register(email=_unique_email("logout"))
        token = body["access_token"]
        logout = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(logout.status_code, 204)

        me = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me.status_code, 401)

    def test_login_does_not_echo_password(self):
        email = _unique_email("echo")
        password = "EchoPass99"
        self._register(email=email, password=password)
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertNotIn(password, str(body))
        user = body["user"]
        self.assertNotIn("password", user)
        self.assertNotIn("password_hash", user)


if __name__ == "__main__":
    unittest.main()
