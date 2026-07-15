"""Signed guest-quiz session: binds grading to questions that were issued."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from fastapi import HTTPException

from app.core.config import settings

# Guest quizzes are short-lived practice sessions.
DEFAULT_TTL_SECONDS = 2 * 60 * 60  # 2 hours


def _signing_key() -> bytes:
    secret = settings.signing_secret()
    if not secret:
        # Deterministic fallback so single-process restarts keep tokens valid.
        # Operators must set SECRET_KEY or GUEST_QUIZ_SIGNING_SECRET in production.
        material = f"{settings.app_name}:{settings.database_url}:guest-quiz"
        secret = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return secret.encode("utf-8")


def _b64encode(data: bytes) -> str:
    return urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return urlsafe_b64decode(data + pad)


def issue_guest_quiz_token(question_ids: list[int], ttl_seconds: int = DEFAULT_TTL_SECONDS) -> str:
    payload = {
        "qid": sorted({int(q) for q in question_ids}),
        "exp": int(time.time()) + int(ttl_seconds),
    }
    body = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = _b64encode(hmac.new(_signing_key(), body.encode("ascii"), hashlib.sha256).digest())
    return f"{body}.{sig}"


def parse_guest_quiz_token(token: str) -> set[int]:
    try:
        body, sig = token.split(".", 1)
        expected = _b64encode(
            hmac.new(_signing_key(), body.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad signature")
        payload = json.loads(_b64decode(body))
        if int(payload["exp"]) < int(time.time()):
            raise ValueError("expired")
        return {int(q) for q in payload["qid"]}
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Guest quiz session expired or invalid. Start a new quiz.",
        ) from exc


def require_guest_question(guest_token: str | None, question_id: int) -> None:
    if not guest_token:
        raise HTTPException(
            status_code=401,
            detail="Guest quiz session required. Start a quiz before grading.",
        )
    allowed = parse_guest_quiz_token(guest_token)
    if int(question_id) not in allowed:
        raise HTTPException(
            status_code=403,
            detail="That question is not part of your current guest quiz.",
        )
