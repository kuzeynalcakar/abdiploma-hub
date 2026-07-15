"""Optional Sentry integration — enabled only in production with a DSN."""

from __future__ import annotations

import logging
import re
from typing import Any

from app.core.config import settings

logger = logging.getLogger("albertaprep.sentry")

_SENSITIVE_KEY = re.compile(
    r"(password|passwd|token|secret|authorization|cookie|session|bearer|api[_-]?key)",
    re.I,
)


def _scrub_dict(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if not data:
        return data
    clean: dict[str, Any] = {}
    for key, value in data.items():
        if _SENSITIVE_KEY.search(str(key)):
            clean[key] = "[Filtered]"
            continue
        if isinstance(value, dict):
            clean[key] = _scrub_dict(value)
        elif isinstance(value, str) and _SENSITIVE_KEY.search(value):
            clean[key] = "[Filtered]"
        else:
            clean[key] = value
    return clean


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any] | None:
    # Drop obvious credential noise from request payloads.
    request = event.get("request") or {}
    if "cookies" in request:
        request["cookies"] = "[Filtered]"
    if "headers" in request and isinstance(request["headers"], dict):
        headers = dict(request["headers"])
        for hk in list(headers):
            if _SENSITIVE_KEY.search(str(hk)):
                headers[hk] = "[Filtered]"
        request["headers"] = headers
    if "data" in request and isinstance(request["data"], dict):
        request["data"] = _scrub_dict(request["data"])
    event["request"] = request

    if "extra" in event and isinstance(event["extra"], dict):
        event["extra"] = _scrub_dict(event["extra"])
    return event


def init_sentry() -> bool:
    """Initialize Sentry when production + DSN. Returns True if enabled."""
    dsn = (settings.sentry_dsn or "").strip()
    env = (settings.environment or "development").strip().lower()
    if not dsn or env != "production":
        logger.info("sentry_disabled environment=%s has_dsn=%s", env, bool(dsn))
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        logger.warning("sentry-sdk not installed; skipping Sentry init")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=settings.app_version,
        traces_sample_rate=0.0,
        send_default_pii=False,
        before_send=_before_send,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )
    logger.info("sentry_enabled environment=%s", env)
    return True


def capture_exception(exc: BaseException, **context: Any) -> None:
    if (settings.environment or "").lower() != "production":
        return
    if not (settings.sentry_dsn or "").strip():
        return
    try:
        import sentry_sdk

        with sentry_sdk.push_scope() as scope:
            for key, value in _scrub_dict(context) or {}.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exc)
    except Exception:
        logger.debug("sentry_capture_failed", exc_info=True)

