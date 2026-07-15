#!/usr/bin/env python3
"""Deactivate active courses that have zero active questions.

Integrity rule: active courses must have a playable bank.
Empty curriculum shells stay in the DB (IDs preserved) but is_active=0
so they are not listed as available practice courses.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DB = BACKEND / "albertaprep.db"


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    empty = conn.execute(
        """
        SELECT c.id, c.code, c.name
        FROM courses c
        WHERE c.is_active = 1
          AND NOT EXISTS (
            SELECT 1 FROM topics t
            JOIN questions q ON q.topic_id = t.id AND q.is_active = 1
            WHERE t.course_id = c.id
          )
        ORDER BY c.code
        """
    ).fetchall()

    actions = []
    for row in empty:
        # Confirm no bank under this course at all (inactive questions either)
        all_q = conn.execute(
            """
            SELECT COUNT(*) FROM questions q
            JOIN topics t ON q.topic_id = t.id
            WHERE t.course_id = ?
            """,
            (row["id"],),
        ).fetchone()[0]
        # Confirm no other course code shares this display name with a bank
        name_dupes = conn.execute(
            """
            SELECT c2.code,
              (SELECT COUNT(*) FROM questions q
               JOIN topics t ON q.topic_id = t.id
               WHERE t.course_id = c2.id AND q.is_active = 1) AS n
            FROM courses c2
            WHERE c2.id != ? AND lower(c2.name) = lower(?)
            """,
            (row["id"], row["name"]),
        ).fetchall()
        bank_elsewhere = [dict(r) for r in name_dupes if r["n"] > 0]

        if bank_elsewhere:
            actions.append(
                {
                    "id": row["id"],
                    "code": row["code"],
                    "name": row["name"],
                    "action": "SKIPPED_NAME_COLLISION",
                    "note": bank_elsewhere,
                }
            )
            continue

        if all_q > 0:
            actions.append(
                {
                    "id": row["id"],
                    "code": row["code"],
                    "name": row["name"],
                    "action": "SKIPPED_HAS_INACTIVE_QUESTIONS",
                    "inactive_question_count": all_q,
                }
            )
            continue

        conn.execute(
            "UPDATE courses SET is_active = 0 WHERE id = ?",
            (row["id"],),
        )
        actions.append(
            {
                "id": row["id"],
                "code": row["code"],
                "name": row["name"],
                "action": "deactivated_is_active_false",
                "reason": "genuine empty bank; no alternate course mapping",
            }
        )

    conn.commit()

    # Verify user data untouched snapshot keys
    snapshot = {
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "quiz_attempts": conn.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0],
        "user_answers": conn.execute("SELECT COUNT(*) FROM user_answers").fetchone()[0],
        "question_history": conn.execute(
            "SELECT COUNT(*) FROM question_history"
        ).fetchone()[0],
        "questions": conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0],
        "active_courses": conn.execute(
            "SELECT COUNT(*) FROM courses WHERE is_active = 1"
        ).fetchone()[0],
        "inactive_courses": conn.execute(
            "SELECT COUNT(*) FROM courses WHERE is_active = 0"
        ).fetchone()[0],
    }
    conn.close()

    report = {"actions": actions, "snapshot": snapshot}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
