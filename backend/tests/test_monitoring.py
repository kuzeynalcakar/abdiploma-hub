"""Monitoring: health/ready, logging middleware, secret scrubbing, reliability."""

from __future__ import annotations

import json
import logging
import time
import unittest
from io import StringIO
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.error_buffer import clear_errors, recent_errors, record_error
from app.core.logging_config import JsonFormatter
from app.core.rate_limit import reset_rate_limits
from app.core.sentry_setup import _before_send, _scrub_dict
from app.database.init_db import init_db
from app.main import app


class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app, raise_server_exceptions=False)

    def setUp(self):
        clear_errors()
        reset_rate_limits()
        settings.rate_limit_enabled = False

    def tearDown(self):
        settings.rate_limit_enabled = True
        clear_errors()

    def test_health_endpoint_shape(self):
        for path in ("/api/v1/health", "/health"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            body = response.json()
            self.assertIn(body["status"], ("ok", "degraded"))
            self.assertEqual(body["api"], "ok")
            self.assertIn(body["database"], ("connected", "unavailable"))
            self.assertIn("version", body)
            self.assertIn("uptime_seconds", body)
            self.assertIsInstance(body["uptime_seconds"], int)

    def test_ready_endpoint(self):
        for path in ("/api/v1/ready", "/ready"):
            response = self.client.get(path)
            self.assertIn(response.status_code, (200, 503), path)
            body = response.json()
            self.assertIn("ready", body)
            self.assertIn("database", body)
            self.assertIn("version", body)
            if response.status_code == 200:
                self.assertTrue(body["ready"])

    def test_error_buffer_scrubs_sensitive_messages(self):
        record_error(
            endpoint="/api/v1/auth/login",
            status_code=500,
            error_type="RuntimeError",
            message="password=supersecret token=abc",
        )
        items = recent_errors(1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["message"], "sensitive details redacted")
        self.assertNotIn("supersecret", json.dumps(items))

    def test_sentry_before_send_filters_secrets(self):
        event = {
            "request": {
                "cookies": {"albertaprep_session": "raw-token"},
                "headers": {
                    "Authorization": "Bearer xyz",
                    "Content-Type": "application/json",
                },
                "data": {"password": "hunter2", "email": "a@b.com"},
            },
            "extra": {"token": "abc", "path": "/api/v1/health"},
        }
        cleaned = _before_send(event, {})
        dumped = json.dumps(cleaned)
        self.assertNotIn("raw-token", dumped)
        self.assertNotIn("hunter2", dumped)
        self.assertNotIn("Bearer xyz", dumped)
        self.assertIn("[Filtered]", dumped)
        self.assertEqual(cleaned["extra"]["path"], "/api/v1/health")

    def test_scrub_dict_filters_nested(self):
        data = _scrub_dict({"ok": 1, "password": "x", "nested": {"api_key": "k"}})
        self.assertEqual(data["ok"], 1)
        self.assertEqual(data["password"], "[Filtered]")
        self.assertEqual(data["nested"]["api_key"], "[Filtered]")

    def test_request_logging_middleware_emits_access_log(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        access = logging.getLogger("albertaprep.access")
        access.addHandler(handler)
        access.setLevel(logging.INFO)
        try:
            response = self.client.get("/api/v1/health")
            self.assertEqual(response.status_code, 200)
            # Allow handlers to flush
            time.sleep(0.01)
            raw = stream.getvalue()
            self.assertTrue(raw.strip(), "expected access log output")
            # At least one JSON line should reference health
            lines = [ln for ln in raw.splitlines() if ln.strip().startswith("{")]
            self.assertTrue(lines)
            last = json.loads(lines[-1])
            self.assertIn(last.get("endpoint") or last.get("message"), last.values())
            joined = " ".join(lines).lower()
            self.assertIn("health", joined)
            self.assertNotIn("password", joined)
            self.assertNotIn("authorization", joined)
        finally:
            access.removeHandler(handler)

    def test_failed_api_request_recorded(self):
        # Force 401 without secrets in buffer
        response = self.client.get("/api/v1/progress")
        self.assertEqual(response.status_code, 401)
        # 401s are not stored as reliability "errors" (only 5xx)
        self.assertEqual(recent_errors(), [])

        # Trigger a 500 via temporary probe
        probe = "/api/v1/__mon_probe"

        @app.get(probe)
        def boom():
            raise RuntimeError("password=should-not-appear")

        try:
            response = self.client.get(probe)
            self.assertEqual(response.status_code, 500)
            body = response.json()
            self.assertEqual(body["detail"], "Something went wrong. Please try again.")
            self.assertNotIn("password", str(body))
            errs = recent_errors()
            self.assertTrue(errs)
            self.assertEqual(errs[0]["status_code"], 500)
            self.assertNotIn("should-not-appear", json.dumps(errs))
        finally:
            app.router.routes[:] = [
                r for r in app.router.routes if getattr(r, "path", None) != probe
            ]

    def test_admin_reliability_requires_auth(self):
        response = self.client.get("/api/v1/admin/reliability")
        self.assertEqual(response.status_code, 403)

    def test_admin_reliability_with_key(self):
        previous_key = settings.admin_api_key
        previous_emails = settings.admin_emails
        settings.admin_api_key = "mon-test-key"
        settings.admin_emails = None
        try:
            record_error(
                endpoint="/api/v1/demo",
                status_code=500,
                error_type="DemoError",
                message="safe message",
            )
            response = self.client.get(
                "/api/v1/admin/reliability",
                headers={"X-Admin-Key": "mon-test-key"},
            )
            self.assertEqual(response.status_code, 200, response.text)
            body = response.json()
            for key in (
                "total_users",
                "total_quizzes",
                "feedback_count",
                "reported_questions",
                "recent_errors",
                "version",
                "uptime_seconds",
            ):
                self.assertIn(key, body)
            self.assertNotIn("email", json.dumps(body.get("recent_errors")))
            self.assertFalse(any("password" in str(e).lower() for e in body["recent_errors"]))
        finally:
            settings.admin_api_key = previous_key
            settings.admin_emails = previous_emails


if __name__ == "__main__":
    unittest.main()

