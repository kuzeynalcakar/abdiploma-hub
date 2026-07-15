"""Database backup utilities for ABDiploma Hub.

SQLite: uses the online backup API (consistent snapshot while the app runs).
PostgreSQL: uses pg_dump when available (best-effort).

Logs never include credentials from DATABASE_URL — only filenames and counts.
"""

from __future__ import annotations

import logging
import shutil
import sqlite3
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger("albertaprep.backup")

BACKUP_PREFIX = "albertaprep_backup_"
BACKUP_SUFFIX = ".db"

# Core tables that must exist in a healthy backup (student + content).
REQUIRED_TABLES = (
    "users",
    "user_sessions",
    "courses",
    "topics",
    "questions",
    "answer_choices",
    "quiz_attempts",
    "user_answers",
    "quiz_feedback",
    "question_reports",
    "question_history",
    "topic_performance",
    "quiz_attempt_questions",
)


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def backup_dir() -> Path:
    raw = (settings.backup_dir or "").strip()
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = _backend_dir() / path
    else:
        path = _backend_dir() / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def resolve_sqlite_path(database_url: str | None = None) -> Path | None:
    url = database_url or settings.database_url
    if not url.startswith("sqlite"):
        return None
    # sqlite:////abs or sqlite:///./rel or sqlite:////C:/...
    if url.startswith("sqlite:////"):
        return Path("/" + url[len("sqlite:////") :])
    if url.startswith("sqlite:///"):
        rest = url[len("sqlite:///") :]
        if rest.startswith("./"):
            return (_backend_dir() / rest[2:]).resolve()
        # Absolute path without extra slash (Windows drive etc.)
        return Path(rest).resolve()
    return None


def _safe_db_label() -> str:
    """Human label without embedding passwords from DATABASE_URL."""
    path = resolve_sqlite_path()
    if path is not None:
        return path.name
    parsed = urlparse(settings.database_url)
    return f"{parsed.scheme}://{parsed.hostname or 'db'}/{parsed.path.lstrip('/')}"


def list_backups() -> list[dict[str, Any]]:
    directory = backup_dir()
    items: list[dict[str, Any]] = []
    for path in sorted(directory.glob(f"{BACKUP_PREFIX}*{BACKUP_SUFFIX}"), reverse=True):
        if not path.is_file():
            continue
        stat = path.stat()
        items.append(
            {
                "filename": path.name,
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
            }
        )
    return items


def latest_backup_info() -> dict[str, str | None]:
    items = list_backups()
    if not items:
        return {
            "last_backup": None,
            "last_backup_note": (
                f"No backups in configured directory yet. "
                f"Run: python -m scripts.backup_db"
            ),
        }
    latest = items[0]
    return {
        "last_backup": latest["filename"],
        "last_backup_note": (
            f"Size {latest['size_bytes']:,} bytes · modified {latest['modified_at']}"
        ),
    }


def apply_retention(retention_days: int | None = None) -> int:
    """Delete timestamped backups older than retention. Returns deleted count."""
    days = retention_days if retention_days is not None else settings.backup_retention_days
    if days <= 0:
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    deleted = 0
    for path in backup_dir().glob(f"{BACKUP_PREFIX}*{BACKUP_SUFFIX}"):
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            try:
                path.unlink()
                deleted += 1
                logger.info("backup_retention_deleted filename=%s", path.name)
            except OSError:
                logger.exception("backup_retention_failed filename=%s", path.name)
    return deleted


def _backup_sqlite(dest: Path) -> Path:
    source_path = resolve_sqlite_path()
    if source_path is None or not source_path.exists():
        raise FileNotFoundError("SQLite database file not found for backup.")

    # Online consistent copy via SQLite backup API.
    source = sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True)
    try:
        dest_conn = sqlite3.connect(dest.as_posix())
        try:
            source.backup(dest_conn)
            dest_conn.commit()
        finally:
            dest_conn.close()
    finally:
        source.close()
    return dest


def _backup_postgres(dest: Path) -> Path:
    """Best-effort pg_dump. Destination is a .sql.gz-style .db name kept for uniformity."""
    url = settings.database_url
    # Write dump beside naming convention; use .sql content with .db suffix avoided —
    # use albertaprep_backup_TS.sql for postgres clarity.
    sql_dest = dest.with_suffix(".sql")
    env = None
    try:
        # pg_dump accepts connection URI; do not log the URI.
        result = subprocess.run(
            ["pg_dump", "--no-owner", "--no-acl", "--format=plain", "--dbname", url],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "pg_dump not found. Install PostgreSQL client tools to backup Postgres."
        ) from exc

    if result.returncode != 0:
        # Never log stderr wholesale if it may contain connection strings.
        raise RuntimeError("pg_dump failed. Check DATABASE_URL and tool permissions.")

    sql_dest.write_text(result.stdout, encoding="utf-8")
    if dest.exists():
        dest.unlink(missing_ok=True)
    return sql_dest


def create_backup() -> dict[str, Any]:
    """Create a timestamped backup and apply retention. Returns safe metadata."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    directory = backup_dir()
    dest = directory / f"{BACKUP_PREFIX}{stamp}{BACKUP_SUFFIX}"

    try:
        if settings.database_url.startswith("sqlite"):
            path = _backup_sqlite(dest)
        elif settings.database_url.startswith("postgres"):
            path = _backup_postgres(dest)
        else:
            raise RuntimeError("Unsupported database_url scheme for automated backup.")

        deleted = apply_retention()
        size = path.stat().st_size
        logger.info(
            "backup_created filename=%s size_bytes=%s deleted_old=%s source=%s",
            path.name,
            size,
            deleted,
            _safe_db_label(),
        )
        return {
            "ok": True,
            "filename": path.name,
            "path": str(path),  # local operators only; not logged above
            "size_bytes": size,
            "deleted_old": deleted,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        logger.exception("backup_failed source=%s", _safe_db_label())
        raise


def table_row_counts(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        existing = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        counts: dict[str, int] = {}
        for table in REQUIRED_TABLES:
            if table not in existing:
                counts[table] = -1  # missing
            else:
                counts[table] = int(
                    conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
                )
        return counts
    finally:
        conn.close()


def verify_backup_file(db_path: Path | str) -> dict[str, Any]:
    """Open a backup SQLite file and validate required tables + readable counts."""
    path = Path(db_path)
    result: dict[str, Any] = {
        "ok": False,
        "filename": path.name,
        "tables_ok": False,
        "missing_tables": [],
        "row_counts": {},
        "errors": [],
    }
    if not path.exists():
        result["errors"].append("Backup file not found.")
        return result
    if path.suffix == ".sql":
        # Postgres dump: verify non-empty and contains CREATE TABLE markers.
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) < 100:
            result["errors"].append("SQL dump is empty or too small.")
            return result
        lower = text.lower()
        missing = [t for t in REQUIRED_TABLES if t not in lower]
        result["missing_tables"] = missing
        result["tables_ok"] = not missing
        result["ok"] = not missing
        result["row_counts"] = {"sql_dump_chars": len(text)}
        if missing:
            result["errors"].append(f"Missing table references: {', '.join(missing)}")
        return result

    try:
        counts = table_row_counts(path)
    except Exception as exc:
        result["errors"].append(f"Could not open backup: {type(exc).__name__}")
        logger.exception("backup_verify_failed filename=%s", path.name)
        return result

    missing = [t for t, n in counts.items() if n < 0]
    result["missing_tables"] = missing
    result["row_counts"] = {t: n for t, n in counts.items() if n >= 0}
    result["tables_ok"] = not missing
    # Soft checks: question banks and users should be present for a full platform backup.
    if counts.get("questions", 0) <= 0:
        result["errors"].append("questions table is empty.")
    if counts.get("courses", 0) <= 0:
        result["errors"].append("courses table is empty.")
    result["ok"] = result["tables_ok"] and not result["errors"]
    return result


def restore_sqlite_backup(backup_path: Path | str, target_path: Path | None = None) -> Path:
    """Replace the live SQLite DB with a verified backup copy.

    Stops short of starting/stopping the app — operators should stop the API first.
    """
    src = Path(backup_path)
    verification = verify_backup_file(src)
    if not verification["ok"]:
        raise RuntimeError(
            "Backup failed verification: "
            + "; ".join(verification.get("errors") or verification.get("missing_tables") or ["unknown"])
        )
    dest = target_path or resolve_sqlite_path()
    if dest is None:
        raise RuntimeError("Restore currently supports SQLite DATABASE_URL only.")

    # Safety copy of current DB before overwrite.
    if dest.exists():
        safety = backup_dir() / (
            f"albertaprep_pre_restore_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"
        )
        shutil.copy2(dest, safety)
        logger.info("pre_restore_copy filename=%s", safety.name)

    shutil.copy2(src, dest)
    logger.info("restore_complete filename=%s", src.name)
    return dest

