"""Production defaults: HSTS, docs off, signing secret."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from fastapi.testclient import TestClient

from app.core import config as config_mod
from app.main import app


class ProductionConfigTests(unittest.TestCase):
    def test_production_defaults(self):
        with mock.patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SECRET_KEY": "x" * 40,
                "FRONTEND_URL": "https://abdiplomahub.com",
                "ENABLE_API_DOCS": "false",
            },
            clear=False,
        ):
            os.environ.pop("ENABLE_HSTS", None)
            from app.core.config import Settings

            s = Settings(_env_file=None)
            self.assertTrue(s.is_production)
            self.assertTrue(s.hsts_enabled)
            self.assertFalse(s.enable_api_docs)

    def test_hsts_off_in_development(self):
        with mock.patch.dict(
            os.environ,
            {"ENVIRONMENT": "development", "ENABLE_HSTS": "false"},
            clear=False,
        ):
            from app.core.config import Settings

            s = Settings(_env_file=None)
            self.assertFalse(s.is_production)
            self.assertFalse(s.hsts_enabled)

    def test_signing_secret_prefers_guest_then_secret_key(self):
        with mock.patch.dict(
            os.environ,
            {
                "GUEST_QUIZ_SIGNING_SECRET": "guest-secret-value-here",
                "SECRET_KEY": "fallback-secret-key-value",
            },
            clear=False,
        ):
            from app.core.config import Settings

            s = Settings(_env_file=None)
            self.assertEqual(s.signing_secret(), "guest-secret-value-here")

    def test_hsts_header_only_when_enabled(self):
        client = TestClient(app)

        with mock.patch.object(
            type(config_mod.settings),
            "hsts_enabled",
            new_callable=mock.PropertyMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
            self.assertEqual(response.status_code, 200)
            hsts = response.headers.get("strict-transport-security", "")
            self.assertIn("max-age=", hsts)

        with mock.patch.object(
            type(config_mod.settings),
            "hsts_enabled",
            new_callable=mock.PropertyMock,
            return_value=False,
        ):
            response = client.get("/api/v1/health")
            self.assertEqual(response.status_code, 200)
            self.assertIsNone(response.headers.get("strict-transport-security"))


if __name__ == "__main__":
    unittest.main()
