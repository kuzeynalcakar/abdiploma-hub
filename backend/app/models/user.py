from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    practice_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_practice_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(
        back_populates="user"
    )
    topic_performances: Mapped[list["TopicPerformance"]] = relationship(
        back_populates="user"
    )
    question_histories: Mapped[list["QuestionHistory"]] = relationship(
        back_populates="user"
    )
