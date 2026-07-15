from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), index=True)
    question_text: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    # Canonical values: multiple_choice, numerical_response, written_response
    question_type: Mapped[str] = mapped_column(
        String(50), default="multiple_choice"
    )
    difficulty: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(20), default="manual")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Alberta curriculum metadata (Program of Studies alignment).
    unit: Mapped[str | None] = mapped_column(String(100))
    outcome_code: Mapped[str | None] = mapped_column(String(20))
    skill_tested: Mapped[str | None] = mapped_column(String(255))
    estimated_time_seconds: Mapped[int | None] = mapped_column(Integer)
    # Canonical answer. For numerical_response / short-answer this is the
    # primary expected value; variants live in accepted_answers (JSON list).
    answer: Mapped[str | None] = mapped_column(Text)
    # JSON array of accepted equivalent answers (canonical also listed in answer).
    accepted_answers: Mapped[str | None] = mapped_column(Text)
    common_mistake: Mapped[str | None] = mapped_column(Text)

    topic: Mapped["Topic"] = relationship(back_populates="questions")
    choices: Mapped[list["AnswerChoice"]] = relationship(
        back_populates="question",
        order_by="AnswerChoice.sort_order",
        cascade="all, delete-orphan",
    )
