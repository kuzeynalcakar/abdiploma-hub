"""Request timing / structured access logs and slow-query hooks."""

from __future__ import annotations

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.core.error_buffer import record_error

access_logger = logging.getLogger("albertaprep.access")
perf_logger = logging.getLogger("albertaprep.perf")

_SENSITIVE_PATH_FRAGMENTS = ("/auth/login", "/auth/register")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        path = request.url.path
        method = request.method
        status_code = 500
        error_type = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            error_type = type(exc).__name__
            status_code = 500
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            slow = duration_ms >= settings.slow_request_threshold_ms

            # Never attach bodies / cookies / tokens to logs.
            extra = {
                "endpoint": path,
                "method": method,
                "status_code": status_code,
                "duration_ms": duration_ms,
                "slow": slow,
            }
            if error_type:
                extra["error_type"] = error_type

            if status_code >= 500:
                record_error(
                    endpoint=path,
                    status_code=status_code,
                    error_type=error_type or "HTTPError",
                    message=f"{method} {path} -> {status_code}",
                )
                access_logger.error("request_failed", extra=extra)
            elif status_code >= 400 and path not in _SENSITIVE_PATH_FRAGMENTS:
                # Auth credential failures are expected noise at INFO without bodies.
                access_logger.info("request_client_error", extra=extra)
            else:
                access_logger.info("request_completed", extra=extra)

            if slow:
                perf_logger.warning("slow_request", extra=extra)


def register_db_timing(engine: Engine) -> None:
    """Log SQL statements that exceed the slow-request threshold."""

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        conn.info["query_start_time"] = time.perf_counter()

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        start = conn.info.pop("query_start_time", None)
        if start is None:
            return
        duration_ms = (time.perf_counter() - start) * 1000
        if duration_ms < settings.slow_request_threshold_ms:
            return
        # Log statement type only — never bind parameters (may contain answers).
        kind = (statement or "").strip().split(" ", 1)[0].upper() or "SQL"
        perf_logger.warning(
            "slow_query",
            extra={
                "duration_ms": round(duration_ms, 2),
                "error_type": kind,
                "endpoint": "db",
                "method": "SQL",
                "status_code": 0,
                "slow": True,
            },
        )

