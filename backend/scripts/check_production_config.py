#!/usr/bin/env python3
"""Fail closed on unsafe production configuration.

Usage (from backend/):
  ENVIRONMENT=production SECRET_KEY=... FRONTEND_URL=https://... \\
    python scripts/check_production_config.py

Exit 0 = ready (or warnings only); exit 1 = blockers (or warnings with --strict).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure backend package is importable when run as a script.
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# Force production for this check if the operator forgot ENVIRONMENT.
os.environ.setdefault("ENVIRONMENT", "production")


def main() -> int:
    parser = argparse.ArgumentParser(description="ABDiploma Hub production config check")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (exit 1).",
    )
    args = parser.parse_args()

    from app.core.config import Settings

    settings = Settings()
    errors: list[str] = []
    warnings: list[str] = []

    if settings.environment != "production":
        errors.append(f"ENVIRONMENT must be production (got {settings.environment!r})")

    if settings.enable_api_docs:
        errors.append("ENABLE_API_DOCS must be false in production")

    if not settings.hsts_enabled:
        warnings.append("HSTS is disabled — enable unless TLS terminator already sends it")

    secret = settings.signing_secret()
    if not secret:
        errors.append("SECRET_KEY or GUEST_QUIZ_SIGNING_SECRET must be set in production")
    elif len(secret) < 32:
        warnings.append("SECRET_KEY / signing secret is shorter than 32 characters")

    frontend = (settings.frontend_url or "").strip()
    if not frontend:
        errors.append("FRONTEND_URL must list the public HTTPS origin(s)")
    else:
        for part in frontend.split(","):
            origin = part.strip().rstrip("/")
            if not origin:
                continue
            if origin == "*":
                errors.append("FRONTEND_URL must not contain '*'")
            elif origin.startswith("http://") and "localhost" not in origin:
                warnings.append(f"FRONTEND_URL uses HTTP (not HTTPS): {origin}")
            elif not origin.startswith("https://") and "localhost" not in origin:
                warnings.append(f"FRONTEND_URL looks non-HTTPS: {origin}")

    if "sqlite" in settings.database_url.lower():
        warnings.append(
            "DATABASE_URL is SQLite — OK for single-node; use Postgres for HA / multi-instance"
        )

    if not (settings.admin_emails or settings.admin_api_key):
        warnings.append("Neither ADMIN_EMAILS nor ADMIN_API_KEY is set")

    if not settings.sentry_dsn:
        warnings.append("SENTRY_DSN is empty — error reporting disabled")

    if not (settings.structured_logging or settings.is_production):
        warnings.append("STRUCTURED_LOGGING is off")

    print("=== ABDiploma Hub production configuration check ===")
    print(f"environment={settings.environment}")
    print(f"hsts_enabled={settings.hsts_enabled}")
    print(f"enable_api_docs={settings.enable_api_docs}")
    print(f"structured_logging={settings.structured_logging or settings.is_production}")
    print()

    for msg in errors:
        print(f"ERROR: {msg}")
    for msg in warnings:
        print(f"WARN:  {msg}")

    if not errors and not warnings:
        print("OK: production configuration looks ready.")
        return 0
    if errors:
        print("\nResult: FAILED (fix errors above).")
        return 1
    print("\nResult: PASSED with warnings.")
    if args.strict:
        print("(Treating warnings as failure because --strict was set.)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
