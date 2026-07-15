from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class QuizAttemptQuestion(Base):
    """Ordered question list for an attempt (daily practice resume)."""

    __tablename__ = "quiz_attempt_questions"
    __table_args__ = (
        UniqueConstraint(
            "quiz_attempt_id",
            "question_id",
            name="uq_quiz_attempt_questions_attempt_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_attempt_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_attempts.id"), index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    quiz_attempt: Mapped["QuizAttempt"] = relationship(
        back_populates="attempt_questions"
    )
    question: Mapped["Question"] = relationship()
