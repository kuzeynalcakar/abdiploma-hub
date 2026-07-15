"""One-time migration: shuffle MC answer_choice sort_order, preserve correctness.

Does NOT change choice_text, is_correct, question text, explanations, IDs,
attempts, or user_answers — only reassigns sort_order on existing rows.

Usage (from backend/):
  python scripts/migrate_shuffle_mc_choice_order.py
  python scripts/migrate_shuffle_mc_choice_order.py --dry-run
"""

from __future__ import annotations

import argparse
import random
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from sqlalchemy.orm import selectinload  # noqa: E402

from app.database.init_db import init_db  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.models import AnswerChoice, Question  # noqa: E402

MIGRATION_SEED = 20260715
LETTERS = ("A", "B", "C", "D")


def _position_counts(db) -> tuple[int, Counter[str], int, int]:
    """Return (mc_count, letter_counts, zero_correct, multi_correct)."""
    questions = (
        db.query(Question)
        .options(selectinload(Question.choices))
        .filter(
            Question.question_type == "multiple_choice",
            Question.is_active.is_(True),
        )
        .all()
    )
    letters: Counter[str] = Counter()
    zero = 0
    multi = 0
    for q in questions:
        choices = sorted(q.choices, key=lambda c: (c.sort_order, c.id))
        corrects = [c for c in choices if c.is_correct]
        if len(corrects) == 0:
            zero += 1
        elif len(corrects) > 1:
            multi += 1
        for i, c in enumerate(choices):
            if c.is_correct and i < 4:
                letters[LETTERS[i]] += 1
    return len(questions), letters, zero, multi


def migrate(*, dry_run: bool, seed: int) -> dict:
    init_db()
    db = SessionLocal()
    report: dict = {
        "dry_run": dry_run,
        "seed": seed,
        "backup_path": None,
        "questions_updated": 0,
        "before": {},
        "after": {},
        "zero_correct": 0,
        "multi_correct": 0,
    }
    try:
        before_n, before_letters, before_zero, before_multi = _position_counts(db)
        report["before"] = {
            "mc_active": before_n,
            "distribution": dict(before_letters),
            "zero_correct": before_zero,
            "multi_correct": before_multi,
        }

        if not dry_run:
            backup_dir = BACKEND / "backups"
            backup_dir.mkdir(exist_ok=True)
            db_path = BACKEND / "albertaprep.db"
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup = backup_dir / f"albertaprep.db.bak-mc-shuffle-{stamp}"
            if db_path.is_file():
                shutil.copy2(db_path, backup)
                report["backup_path"] = str(backup)

        questions = (
            db.query(Question)
            .options(selectinload(Question.choices))
            .filter(
                Question.question_type == "multiple_choice",
                Question.is_active.is_(True),
            )
            .order_by(Question.id)
            .all()
        )
        rng = random.Random(seed)
        updated = 0

        if dry_run:
            sim_letters: Counter[str] = Counter()
            for q in questions:
                choices = sorted(list(q.choices), key=lambda c: (c.sort_order, c.id))
                if len(choices) < 2:
                    continue
                reordered = choices[:]
                rng.shuffle(reordered)
                updated += 1
                for i, c in enumerate(reordered):
                    if c.is_correct and i < 4:
                        sim_letters[LETTERS[i]] += 1
            report["questions_updated"] = updated
            report["after"] = {
                "mc_active": before_n,
                "distribution": dict(sim_letters),
                "note": "dry-run simulation (not written)",
            }
            report["zero_correct"] = before_zero
            report["multi_correct"] = before_multi
        else:
            for q in questions:
                choices = list(q.choices)
                if len(choices) < 2:
                    continue
                choices.sort(key=lambda c: (c.sort_order, c.id))
                rng.shuffle(choices)
                for order, choice in enumerate(choices):
                    choice.sort_order = order
                updated += 1

            report["questions_updated"] = updated
            db.commit()
            after_n, after_letters, after_zero, after_multi = _position_counts(db)
            report["after"] = {
                "mc_active": after_n,
                "distribution": dict(after_letters),
            }
            report["zero_correct"] = after_zero
            report["multi_correct"] = after_multi
            if after_zero or after_multi:
                raise RuntimeError(
                    f"Integrity failure after shuffle: zero={after_zero} multi={after_multi}"
                )
    finally:
        db.close()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=MIGRATION_SEED)
    args = parser.parse_args()
    report = migrate(dry_run=args.dry_run, seed=args.seed)
    print("MC choice shuffle migration")
    print(f"  dry_run={report['dry_run']} seed={report['seed']}")
    if report.get("backup_path"):
        print(f"  backup={report['backup_path']}")
    print(f"  questions_updated={report['questions_updated']}")
    print(f"  before={report['before']}")
    print(f"  after={report['after']}")
    print(f"  zero_correct={report['zero_correct']} multi_correct={report['multi_correct']}")
    dist = report["after"].get("distribution") or {}
    total = sum(dist.get(L, 0) for L in LETTERS) or 1
    print("Final distribution:")
    for L in LETTERS:
        n = dist.get(L, 0)
        print(f"  {L}: {n} ({n / total:.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
