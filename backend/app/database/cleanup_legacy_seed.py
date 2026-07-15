"""Remove legacy demo seed questions not present in the validated final bank.

The original README setup imported ``math30-1_questions_cleaned.json`` (10
questions). The validated ``math30-1_questions_final.json`` (243 questions)
was imported later; nine seed questions were skipped as exact-text duplicates,
leaving one extra seed-only row (VECTOR permutations) in production.

This script:
- Identifies questions whose text appears in the cleaned seed file.
- Deletes only seed questions whose text is NOT in the final bank.
- Leaves the nine overlapping rows intact (they are canonical final content).
- Removes dependent rows (user answers, history, attempt links) before delete.

Usage, from the backend directory:

    python -m app.database.cleanup_legacy_seed [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models import (
    AnswerChoice,
    Course,
    Question,
    QuestionHistory,
    QuizAttemptQuestion,
    Topic,
    UserAnswer,
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
QUESTIONS_DIR = BACKEND_DIR.parent / "questions.json"
CLEANED_PATH = QUESTIONS_DIR / "math30-1_questions_cleaned.json"
FINAL_PATH = QUESTIONS_DIR / "math30-1_questions_final.json"


def _normalize(text: str) -> str:
    return " ".join(text.split()).casefold()


def load_seed_texts() -> tuple[set[str], set[str]]:
    if not CLEANED_PATH.is_file():
        raise FileNotFoundError(f"Missing seed file: {CLEANED_PATH}")
    if not FINAL_PATH.is_file():
        raise FileNotFoundError(f"Missing final bank file: {FINAL_PATH}")

    cleaned = json.loads(CLEANED_PATH.read_text(encoding="utf-8"))
    final = json.loads(FINAL_PATH.read_text(encoding="utf-8"))
    if not isinstance(cleaned, list) or not isinstance(final, list):
        raise ValueError("Seed and final files must contain JSON arrays.")

    cleaned_texts = {_normalize(item["question_text"]) for item in cleaned}
    final_texts = {_normalize(item["question_text"]) for item in final}
    return cleaned_texts, final_texts


def find_legacy_seed_questions(db: Session) -> list[Question]:
    cleaned_texts, _ = load_seed_texts()
    course = db.query(Course).filter(Course.code == "MATH30-1").first()
    if course is None:
        return []

    rows = (
        db.query(Question)
        .join(Topic)
        .filter(Topic.course_id == course.id)
        .order_by(Question.id)
        .all()
    )
    return [q for q in rows if _normalize(q.question_text) in cleaned_texts]


def find_removable_seed_questions(db: Session) -> list[Question]:
    cleaned_texts, final_texts = load_seed_texts()
    removable_norms = cleaned_texts - final_texts
    return [
        q
        for q in find_legacy_seed_questions(db)
        if _normalize(q.question_text) in removable_norms
    ]


def delete_question_dependencies(db: Session, question_id: int) -> dict[str, int]:
    counts = {
        "user_answers": (
            db.query(UserAnswer)
            .filter(UserAnswer.question_id == question_id)
            .delete(synchronize_session=False)
        ),
        "question_history": (
            db.query(QuestionHistory)
            .filter(QuestionHistory.question_id == question_id)
            .delete(synchronize_session=False)
        ),
        "quiz_attempt_questions": (
            db.query(QuizAttemptQuestion)
            .filter(QuizAttemptQuestion.question_id == question_id)
            .delete(synchronize_session=False)
        ),
        "answer_choices": (
            db.query(AnswerChoice)
            .filter(AnswerChoice.question_id == question_id)
            .delete(synchronize_session=False)
        ),
    }
    return counts


def cleanup_legacy_seed(db: Session, *, dry_run: bool = False) -> dict:
    cleaned_texts, final_texts = load_seed_texts()
    legacy = find_legacy_seed_questions(db)
    removable = find_removable_seed_questions(db)
    retained = [q for q in legacy if q not in removable]

    report = {
        "cleaned_seed_count": len(cleaned_texts),
        "final_bank_count": len(final_texts),
        "legacy_seed_identified": [
            {
                "id": q.id,
                "topic": q.topic.name if q.topic else None,
                "in_final_bank": _normalize(q.question_text) in final_texts,
                "question_text_preview": q.question_text[:100],
            }
            for q in legacy
        ],
        "removed": [],
        "retained_seed_overlap": [
            {
                "id": q.id,
                "topic": q.topic.name if q.topic else None,
                "reason": "Exact text exists in math30-1_questions_final.json",
            }
            for q in retained
        ],
        "dry_run": dry_run,
    }

    for question in removable:
        deps = {
            "user_answers": db.query(UserAnswer)
            .filter(UserAnswer.question_id == question.id)
            .count(),
            "question_history": db.query(QuestionHistory)
            .filter(QuestionHistory.question_id == question.id)
            .count(),
            "quiz_attempt_questions": db.query(QuizAttemptQuestion)
            .filter(QuizAttemptQuestion.question_id == question.id)
            .count(),
            "answer_choices": db.query(AnswerChoice)
            .filter(AnswerChoice.question_id == question.id)
            .count(),
        }
        entry = {
            "id": question.id,
            "topic": question.topic.name if question.topic else None,
            "dependencies_before_delete": deps,
        }
        report["removed"].append(entry)

        if dry_run:
            continue

        delete_question_dependencies(db, question.id)
        db.delete(question)

    if not dry_run:
        db.commit()

    report["db_question_count_after"] = (
        None if dry_run else db.query(Question).count()
    )
    return report


def print_report(report: dict) -> None:
    print("Legacy seed cleanup report")
    print(f"  Cleaned seed file questions: {report['cleaned_seed_count']}")
    print(f"  Final bank file questions:   {report['final_bank_count']}")
    print(f"  Legacy seed rows identified: {len(report['legacy_seed_identified'])}")
    print(f"  Rows removed:                {len(report['removed'])}")
    print(f"  Rows retained (final overlap): {len(report['retained_seed_overlap'])}")
    print(f"  Dry run:                     {report['dry_run']}")
    if report["db_question_count_after"] is not None:
        print(f"  DB question count after:     {report['db_question_count_after']}")

    if report["removed"]:
        print("\nRemoved:")
        for row in report["removed"]:
            print(
                f"  - id={row['id']} topic={row['topic']} "
                f"deps={row['dependencies_before_delete']}"
            )

    if report["retained_seed_overlap"]:
        print("\nRetained (canonical final-bank content, same question text):")
        for row in report["retained_seed_overlap"]:
            print(f"  - id={row['id']} topic={row['topic']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report removable rows without deleting.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        report = cleanup_legacy_seed(db, dry_run=args.dry_run)
    finally:
        db.close()

    print_report(report)

    if not args.dry_run and report["db_question_count_after"] != report["final_bank_count"]:
        print(
            "\nWarning: DB count does not match final bank count.",
            file=sys.stderr,
        )
        print(
            f"  Expected: {report['final_bank_count']}, "
            f"Actual: {report['db_question_count_after']}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
