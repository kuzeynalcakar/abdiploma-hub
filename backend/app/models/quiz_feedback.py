from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class QuizFeedback(Base):
    __tablename__ = "quiz_feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    quiz_attempt_id: Mapped[int | None] = mapped_column(
        ForeignKey("quiz_attempts.id"), nullable=True, index=True
    )
    rating: Mapped[str] = mapped_column(String(20))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Null = unread/new for admin triage (additive column)
    admin_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User | None"] = relationship()
    course: Mapped["Course"] = relationship()
