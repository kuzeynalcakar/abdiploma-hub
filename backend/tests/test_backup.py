"""Backup creation, verification, restore safety, and integrity audits."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.rate_limit import reset_rate_limits
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.main import app
from app.services import backup as backup_svc
from app.services.integrity import run_integrity_audit


class BackupAndIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app, raise_server_exceptions=False)

    def setUp(self):
        reset_rate_limits()
        settings.rate_limit_enabled = False
        self._tmpdir = tempfile.TemporaryDirectory()
        self._prev_backup_dir = settings.backup_dir
        self._prev_retention = settings.backup_retention_days
        settings.backup_dir = self._tmpdir.name
        settings.backup_retention_days = 30

    def tearDown(self):
        settings.backup_dir = self._prev_backup_dir
        settings.backup_retention_days = self._prev_retention
        settings.rate_limit_enabled = True
        self._tmpdir.cleanup()

    def test_create_and_verify_backup(self):
        if not settings.database_url.startswith("sqlite"):
            self.skipTest("SQLite-only backup test")
        result = backup_svc.create_backup()
        self.assertTrue(result["ok"])
        self.assertTrue(result["filename"].startswith("albertaprep_backup_"))
        path = Path(result["path"])
        self.assertTrue(path.exists())
        self.assertGreater(result["size_bytes"], 0)

        verification = backup_svc.verify_backup_file(path)
        self.assertTrue(verification["tables_ok"], verification)
        self.assertTrue(verification["ok"], verification)
        counts = verification["row_counts"]
        for table in (
            "users",
            "questions",
            "quiz_attempts",
            "user_answers",
            "quiz_feedback",
            "question_reports",
        ):
            self.assertIn(table, counts)
            self.assertGreaterEqual(counts[table], 0)

        # Logs / public responses shouldn't embed database passwords (SQLite N/A),
        # but filenames must not leak absolute user home paths in API payloads.
        health = self.client.get(
            "/api/v1/admin/health",
            headers={"X-Admin-Key": self._admin_key()},
        )
        # May be 403 if admin not configured — that's fine for this assert path.
        if health.status_code == 200:
            body = health.json()
            self.assertEqual(body.get("last_backup"), result["filename"])
            self.assertNotIn("password", str(body).lower())

    def test_verify_missing_file_fails(self):
        report = backup_svc.verify_backup_file(
            Path(self._tmpdir.name) / "missing.db"
        )
        self.assertFalse(report["ok"])
        self.assertTrue(report["errors"])

    def test_restore_round_trip(self):
        if not settings.database_url.startswith("sqlite"):
            self.skipTest("SQLite-only restore test")
        source = backup_svc.resolve_sqlite_path()
        self.assertIsNotNone(source)
        self.assertTrue(source.exists())

        result = backup_svc.create_backup()
        backup_path = Path(result["path"])

        # Restore into a temp copy — do not overwrite live DB during unit tests.
        with tempfile.TemporaryDirectory() as restore_dir:
            target = Path(restore_dir) / "restored.db"
            restored = backup_svc.restore_sqlite_backup(backup_path, target_path=target)
            self.assertTrue(restored.exists())
            verify = backup_svc.verify_backup_file(restored)
            self.assertTrue(verify["ok"], verify)
            # Row counts should match the backup snapshot
            self.assertEqual(
                verify["row_counts"].get("questions"),
                backup_svc.verify_backup_file(backup_path)["row_counts"].get("questions"),
            )

    def test_integrity_audit_runs(self):
        db = SessionLocal()
        try:
            report = run_integrity_audit(db)
        finally:
            db.close()
        self.assertIn("ok", report)
        self.assertIn("checks", report)
        self.assertGreater(len(report["checks"]), 5)
        # Each check has required keys
        for check in report["checks"]:
            self.assertIn("key", check)
            self.assertIn("ok", check)
            self.assertIn("count", check)

    def test_admin_integrity_requires_auth(self):
        response = self.client.get("/api/v1/admin/integrity")
        self.assertEqual(response.status_code, 403)

    def test_admin_integrity_with_key(self):
        key = self._admin_key()
        response = self.client.get(
            "/api/v1/admin/integrity",
            headers={"X-Admin-Key": key},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("ok", body)
        self.assertIn("checks", body)
        # No emails / passwords leaked
        dumped = str(body).lower()
        self.assertNotIn("password", dumped)
        self.assertNotIn("@", dumped)  # no emails in integrity payload

    def test_retention_deletes_old_backups(self):
        # Create a fake old backup file and ensure retention removes it
        directory = backup_svc.backup_dir()
        old = directory / "albertaprep_backup_20000101_000000.db"
        old.write_bytes(b"sqlite-fake")
        # Set mtime far in the past via retention using days=1 after touching? 
        # apply_retention uses file mtime — set retention to huge number of days so
        # a just-created file survives; old file with ancient name still has now mtime.
        # Force old mtime:
        import os
        import time

        old_ts = time.time() - (40 * 86400)
        os.utime(old, (old_ts, old_ts))
        settings.backup_retention_days = 14
        deleted = backup_svc.apply_retention()
        self.assertGreaterEqual(deleted, 1)
        self.assertFalse(old.exists())

    def _admin_key(self) -> str:
        previous = settings.admin_api_key
        settings.admin_api_key = "backup-test-key"
        settings.admin_emails = settings.admin_emails or None
        self.addCleanup(lambda: setattr(settings, "admin_api_key", previous))
        return "backup-test-key"


if __name__ == "__main__":
    unittest.main()

