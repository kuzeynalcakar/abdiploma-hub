# Importing app.models registers every model class on Base.metadata,
# which is required before create_all can see the tables.
import app.models  # noqa: F401
from sqlalchemy import inspect, text

from app.database.session import Base, engine

# Columns added after the initial release. create_all only creates missing
# tables, never missing columns, so existing databases are patched here.
# SQLite supports ALTER TABLE ... ADD COLUMN, which is all we need.
_QUESTIONS_NEW_COLUMNS = {
    "unit": "VARCHAR(100)",
    "outcome_code": "VARCHAR(20)",
    "skill_tested": "VARCHAR(255)",
    "estimated_time_seconds": "INTEGER",
    "answer": "TEXT",
    "accepted_answers": "TEXT",
    "common_mistake": "TEXT",
}

_QUIZ_ATTEMPTS_NEW_COLUMNS = {
    "practice_date": "DATE",
    "selection_metadata": "TEXT",
}

_USERS_NEW_COLUMNS = {
    "practice_streak": "INTEGER DEFAULT 0",
    "last_practice_date": "DATE",
}


_USER_ANSWERS_NEW_COLUMNS = {
    "response_text": "TEXT",
    "auto_graded": "BOOLEAN DEFAULT 1",
}

_QUESTION_REPORTS_NEW_COLUMNS = {
    "status": "VARCHAR(20) DEFAULT 'pending'",
    "admin_note": "TEXT",
    "status_changed_at": "DATETIME",
}

_QUIZ_FEEDBACK_NEW_COLUMNS = {
    "admin_reviewed_at": "DATETIME",
}

_USER_SESSIONS_NEW_COLUMNS = {
    "expires_at": "DATETIME",
}


def _migrate_user_answers_nullable_choice() -> None:
    """Rebuild user_answers so answer_choice_id and is_correct allow NULL."""
    inspector = inspect(engine)
    if "user_answers" not in inspector.get_table_names():
        return

    columns = {col["name"]: col for col in inspector.get_columns("user_answers")}
    choice_col = columns.get("answer_choice_id")
    if choice_col is None or not choice_col.get("nullable", True):
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS user_answers__new (
                        id INTEGER PRIMARY KEY,
                        quiz_attempt_id INTEGER NOT NULL,
                        question_id INTEGER NOT NULL,
                        answer_choice_id INTEGER,
                        response_text TEXT,
                        auto_graded BOOLEAN DEFAULT 1,
                        is_correct BOOLEAN,
                        answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(quiz_attempt_id) REFERENCES quiz_attempts(id),
                        FOREIGN KEY(question_id) REFERENCES questions(id),
                        FOREIGN KEY(answer_choice_id) REFERENCES answer_choices(id),
                        UNIQUE(quiz_attempt_id, question_id)
                    )
                    """
                )
            )
            has_response = "response_text" in columns
            has_auto_graded = "auto_graded" in columns
            conn.execute(
                text(
                    f"""
                    INSERT INTO user_answers__new (
                        id, quiz_attempt_id, question_id, answer_choice_id,
                        response_text, auto_graded, is_correct, answered_at
                    )
                    SELECT
                        id, quiz_attempt_id, question_id, answer_choice_id,
                        {"response_text" if has_response else "NULL"},
                        {"auto_graded" if has_auto_graded else "1"},
                        is_correct, answered_at
                    FROM user_answers
                    """
                )
            )
            conn.execute(text("DROP TABLE user_answers"))
            conn.execute(text("ALTER TABLE user_answers__new RENAME TO user_answers"))
            print("Migrated user_answers for nullable answer_choice_id")


def _add_missing_columns() -> None:
    inspector = inspect(engine)
    with engine.begin() as conn:
        if "questions" in inspector.get_table_names():
            existing = {col["name"] for col in inspector.get_columns("questions")}
            for name, sql_type in _QUESTIONS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(f"ALTER TABLE questions ADD COLUMN {name} {sql_type}")
                    )
                    print(f"Added column questions.{name}")

        if "quiz_attempts" in inspector.get_table_names():
            existing = {
                col["name"] for col in inspector.get_columns("quiz_attempts")
            }
            for name, sql_type in _QUIZ_ATTEMPTS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE quiz_attempts ADD COLUMN {name} {sql_type}"
                        )
                    )
                    print(f"Added column quiz_attempts.{name}")

        if "users" in inspector.get_table_names():
            existing = {col["name"] for col in inspector.get_columns("users")}
            for name, sql_type in _USERS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(f"ALTER TABLE users ADD COLUMN {name} {sql_type}")
                    )
                    print(f"Added column users.{name}")

        if "user_answers" in inspector.get_table_names():
            existing = {
                col["name"] for col in inspector.get_columns("user_answers")
            }
            for name, sql_type in _USER_ANSWERS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE user_answers ADD COLUMN {name} {sql_type}"
                        )
                    )
                    print(f"Added column user_answers.{name}")

        if "question_reports" in inspector.get_table_names():
            existing = {
                col["name"] for col in inspector.get_columns("question_reports")
            }
            for name, sql_type in _QUESTION_REPORTS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE question_reports ADD COLUMN {name} {sql_type}"
                        )
                    )
                    print(f"Added column question_reports.{name}")

        if "quiz_feedback" in inspector.get_table_names():
            existing = {
                col["name"] for col in inspector.get_columns("quiz_feedback")
            }
            for name, sql_type in _QUIZ_FEEDBACK_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE quiz_feedback ADD COLUMN {name} {sql_type}"
                        )
                    )
                    print(f"Added column quiz_feedback.{name}")

        if "user_sessions" in inspector.get_table_names():
            existing = {
                col["name"] for col in inspector.get_columns("user_sessions")
            }
            for name, sql_type in _USER_SESSIONS_NEW_COLUMNS.items():
                if name not in existing:
                    conn.execute(
                        text(
                            f"ALTER TABLE user_sessions ADD COLUMN {name} {sql_type}"
                        )
                    )
                    print(f"Added column user_sessions.{name}")

    _migrate_user_answers_nullable_choice()
    _migrate_session_token_hashes_and_expiry()


def _migrate_session_token_hashes_and_expiry() -> None:
    """One-time: hash plaintext session tokens and backfill expires_at.

    Strategy (preserves existing logins):
    1. Rows whose token is not already a 64-char hex digest are assumed to
       be legacy plaintext → replace with SHA-256(hex) of that value.
       Clients still holding the original plaintext continue to work because
       lookups always hash the presented secret before querying.
    2. Rows with NULL expires_at get now + SESSION_TTL_HOURS.
    """
    import hashlib
    from datetime import datetime, timedelta, timezone

    from app.core.config import settings

    inspector = inspect(engine)
    if "user_sessions" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("user_sessions")}
    if "token" not in columns:
        return

    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, token, expires_at FROM user_sessions")
        ).fetchall()
        ttl = timedelta(hours=settings.session_ttl_hours)
        now = datetime.now(timezone.utc)
        hashed = 0
        dated = 0
        for row_id, token, expires_at in rows:
            new_token = token
            # SHA-256 hex is always 64 lowercase hex chars.
            is_hex64 = (
                isinstance(token, str)
                and len(token) == 64
                and all(c in "0123456789abcdef" for c in token)
            )
            if token and not is_hex64:
                new_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
                hashed += 1

            new_expires = expires_at
            if expires_at is None:
                new_expires = now + ttl
                dated += 1

            if new_token != token or (expires_at is None and "expires_at" in columns):
                conn.execute(
                    text(
                        "UPDATE user_sessions SET token = :token, expires_at = :expires_at "
                        "WHERE id = :id"
                    ),
                    {"token": new_token, "expires_at": new_expires, "id": row_id},
                )

        if hashed or dated:
            print(
                f"Migrated user_sessions: hashed={hashed} backfilled_expiry={dated}"
            )


def init_db() -> None:
    """Create all database tables defined by the models and apply
    additive column migrations to pre-existing tables."""
    _add_missing_columns()
    Base.metadata.create_all(bind=engine)
    # create_all may create user_sessions without running column patches first
    # on brand-new DBs; re-run session migration safely (no-op if already done).
    _migrate_session_token_hashes_and_expiry()


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
