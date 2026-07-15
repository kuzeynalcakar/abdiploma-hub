import logging
import time

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.database.session import engine

router = APIRouter(tags=["health"])
logger = logging.getLogger("albertaprep.health")

_STARTED_AT = time.time()


def _uptime_seconds() -> int:
    return max(0, int(time.time() - _STARTED_AT))


def _check_database() -> tuple[str, str]:
    """Returns (api_status_fragment, database_label)."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok", "connected"
    except Exception:
        logger.exception("health_check database unavailable")
        return "degraded", "unavailable"


@router.get("/health")
def health_check():
    """Liveness + dependency snapshot for operators and uptime monitors."""
    api_ok, db_status = _check_database()
    overall = "ok" if api_ok == "ok" else "degraded"
    return {
        "status": overall,
        "api": "ok",
        "database": db_status,
        "version": settings.app_version,
        "uptime_seconds": _uptime_seconds(),
        "environment": settings.environment,
    }


@router.get("/ready")
def readiness_check():
    """Deployment readiness — fails when the database is unreachable."""
    _, db_status = _check_database()
    ready = db_status == "connected"
    body = {
        "ready": ready,
        "api": "ok",
        "database": db_status,
        "version": settings.app_version,
        "uptime_seconds": _uptime_seconds(),
    }
    if not ready:
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=503, content=body)
    return body

