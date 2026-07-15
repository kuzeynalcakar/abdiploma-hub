from datetime import datetime



from sqlalchemy import DateTime, ForeignKey, String, func

from sqlalchemy.orm import Mapped, mapped_column, relationship



from app.database.session import Base





class UserSession(Base):

    """An opaque bearer/cookie session for one login.



    The `token` column stores a SHA-256 hex digest of the client secret —

    never the raw token. Deleting the row (or letting expires_at pass)

    logs the session out. A user may hold several sessions (one per device).

    """



    __tablename__ = "user_sessions"



    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # SHA-256 hex (64 chars) of the opaque client token.

    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True), server_default=func.now()

    )

    expires_at: Mapped[datetime | None] = mapped_column(

        DateTime(timezone=True), nullable=True, index=True

    )



    user: Mapped["User"] = relationship()


