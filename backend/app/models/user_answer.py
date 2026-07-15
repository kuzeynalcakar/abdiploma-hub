from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"
    __table_args__ = (
        UniqueConstraint(
            "quiz_attempt_id",
            "question_id",
            name="uq_user_answers_attempt_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_attempt_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_attempts.id"), index=True
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), index=True
    )
    answer_choice_id: Mapped[int | None] = mapped_column(
        ForeignKey("answer_choices.id"), nullable=True
    )
    # Free-text response for numerical and written response questions.
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # False for written response (self-review); True for auto-graded formats.
    auto_graded: Mapped[bool] = mapped_column(Boolean, default=True)
    # Copied at answer time. None when the response requires manual review.
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    quiz_attempt: Mapped["QuizAttempt"] = relationship(
        back_populates="answers"
    )
    question: Mapped["Question"] = relationship()
    answer_choice: Mapped["AnswerChoice"] = relationship()
