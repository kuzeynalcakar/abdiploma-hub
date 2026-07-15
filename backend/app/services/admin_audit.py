"""Persist and emit structured admin action audit events."""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.admin_action_log import AdminActionLog
from app.models.user import User

logger = logging.getLogger("albertaprep.admin")


def log_admin_action(
    db: Session,
    *,
    admin: User | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    detail: dict[str, Any] | None = None,
) -> AdminActionLog:
    """Write an append-only audit row and emit a structured log line.

    Does not commit — callers own the transaction.
    Never store passwords, session tokens, or full email addresses in detail.
    """
    payload = None
    if detail:
        # Strip accidental PII keys if present
        safe = {
            k: v
            for k, v in detail.items()
            if k.lower() not in {"email", "password", "token", "cookie"}
        }
        payload = json.dumps(safe, default=str)[:4000]

    row = AdminActionLog(
        admin_user_id=admin.id if admin is not None else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        detail=payload,
    )
    db.add(row)
    logger.info(
        "admin_action action=%s entity=%s:%s admin_user_id=%s",
        action,
        entity_type,
        entity_id,
        admin.id if admin is not None else None,
    )
    return row
