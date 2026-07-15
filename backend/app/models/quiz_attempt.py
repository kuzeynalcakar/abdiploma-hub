from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    topic_id: Mapped[int | None] = mapped_column(
        ForeignKey("topics.id"), index=True
    )
    mode: Mapped[str] = mapped_column(String(20), default="quiz")
    practice_date: Mapped[date | None] = mapped_column(Date, index=True)
    selection_metadata: Mapped[str | None] = mapped_column(Text)
    questions_total: Mapped[int] = mapped_column(Integer, default=0)
    questions_correct: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    user: Mapped["User"] = relationship(back_populates="quiz_attempts")
    course: Mapped["Course"] = relationship()
    topic: Mapped["Topic | None"] = relationship()
    answers: Mapped[list["UserAnswer"]] = relationship(
        back_populates="quiz_attempt", cascade="all, delete-orphan"
    )
    attempt_questions: Mapped[list["QuizAttemptQuestion"]] = relationship(
        back_populates="quiz_attempt", cascade="all, delete-orphan"
    )
