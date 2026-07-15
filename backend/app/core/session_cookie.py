"""HttpOnly session cookie helpers for browser clients."""

from __future__ import annotations

import logging

from fastapi import Response

from app.core.config import settings

logger = logging.getLogger("albertaprep")


def set_session_cookie(response: Response, raw_token: str) -> None:
    logger.debug(
        "Setting session cookie name=%s secure=%s samesite=%s path=%s max_age=%s",
        settings.auth_cookie_name,
        settings.cookie_secure,
        settings.cookie_samesite,
        "/",
        int(settings.session_ttl_hours * 3600),
    )
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        max_age=int(settings.session_ttl_hours * 3600),
    )


def clear_session_cookie(response: Response) -> None:
    logger.debug(
        "Clearing session cookie name=%s secure=%s samesite=%s path=%s",
        settings.auth_cookie_name,
        settings.cookie_secure,
        settings.cookie_samesite,
        "/",
    )
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )

