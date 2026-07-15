"""Admin authorization helpers (ADMIN_API_KEY and/or ADMIN_EMAILS)."""



from __future__ import annotations



import hmac



from fastapi import Depends, Header, HTTPException, Request

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session



from app.core.config import settings

from app.core.deps import extract_raw_session_token

from app.core.security import hash_session_token, utcnow

from app.database.session import get_db

from app.models import User, UserSession

from datetime import timezone



_bearer = HTTPBearer(auto_error=False)





def parse_admin_emails() -> set[str]:

    raw = (settings.admin_emails or "").strip()

    if not raw:

        return set()

    return {part.strip().lower() for part in raw.split(",") if part.strip()}





def admin_configured() -> bool:

    return bool(settings.admin_api_key) or bool(parse_admin_emails())





def is_admin_user(user: User | None) -> bool:

    if user is None:

        return False

    return user.email.lower() in parse_admin_emails()





def _aware(dt):

    if dt is None:

        return None

    if dt.tzinfo is None:

        return dt.replace(tzinfo=timezone.utc)

    return dt





def _user_from_request(

    request: Request,

    credentials: HTTPAuthorizationCredentials | None,

    db: Session,

) -> User | None:

    raw = extract_raw_session_token(request, credentials)

    if not raw:

        return None

    session = (

        db.query(UserSession)

        .filter(UserSession.token == hash_session_token(raw))

        .first()

    )

    if session is None:

        return None

    expires_at = _aware(session.expires_at)

    if expires_at is None or expires_at <= utcnow():

        db.delete(session)

        db.commit()

        return None

    return session.user





def require_admin(

    request: Request,

    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),

    db: Session = Depends(get_db),

    x_admin_key: str | None = Header(None, alias="X-Admin-Key"),

) -> User | None:

    """Allow access via X-Admin-Key or an authenticated admin email.



    Returns the admin User when authenticated by email; None when authorized

    solely by API key (script/CLI access).

    """

    if not admin_configured():

        raise HTTPException(

            status_code=503,

            detail="Admin access is not configured. Set ADMIN_API_KEY and/or ADMIN_EMAILS.",

        )



    expected = settings.admin_api_key or ""

    if expected and x_admin_key and hmac.compare_digest(x_admin_key, expected):

        return None



    user = _user_from_request(request, credentials, db)

    if user is not None and is_admin_user(user):

        return user



    raise HTTPException(status_code=403, detail="Admin access required.")


