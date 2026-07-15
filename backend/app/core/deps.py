from datetime import timezone

import logging

from fastapi import Depends, HTTPException, Request

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session



from app.core.config import settings

from app.core.security import hash_session_token, utcnow

from app.database.session import get_db

from app.models import User, UserSession



_bearer = HTTPBearer(auto_error=False)





def _aware(dt):

    """SQLite may return naive datetimes; treat them as UTC."""

    if dt is None:

        return None

    if dt.tzinfo is None:

        return dt.replace(tzinfo=timezone.utc)

    return dt





def extract_raw_session_token(

    request: Request,

    credentials: HTTPAuthorizationCredentials | None,

) -> str | None:

    """Prefer Authorization Bearer, then HttpOnly session cookie."""

    logger = logging.getLogger("albertaprep")
    logger.debug("Incoming request cookie names=%s", list(request.cookies.keys()))

    if credentials is not None and credentials.credentials:

        return credentials.credentials

    cookie = request.cookies.get(settings.auth_cookie_name)

    if cookie:

        return cookie

    return None





def _lookup_session(db: Session, raw_token: str) -> UserSession | None:

    token_hash = hash_session_token(raw_token)

    return (

        db.query(UserSession)

        .filter(UserSession.token == token_hash)

        .first()

    )





def _reject_if_expired(db: Session, session: UserSession) -> None:

    expires_at = _aware(session.expires_at)

    if expires_at is None:

        # Legacy row without expiry — treat as expired and force re-login.

        db.delete(session)

        db.commit()

        raise HTTPException(

            status_code=401,

            detail="Session expired or invalid. Log in again.",

        )

    if expires_at <= utcnow():

        db.delete(session)

        db.commit()

        raise HTTPException(

            status_code=401,

            detail="Session expired or invalid. Log in again.",

        )





def get_current_user(

    request: Request,

    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),

    db: Session = Depends(get_db),

) -> User:

    raw = extract_raw_session_token(request, credentials)

    if not raw:

        raise HTTPException(status_code=401, detail="Not authenticated.")



    session = _lookup_session(db, raw)

    if session is None:

        raise HTTPException(

            status_code=401, detail="Session expired or invalid. Log in again."

        )

    _reject_if_expired(db, session)

    return session.user





def get_optional_user(

    request: Request,

    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),

    db: Session = Depends(get_db),

) -> User | None:

    raw = extract_raw_session_token(request, credentials)

    if not raw:

        return None



    session = _lookup_session(db, raw)

    if session is None:

        return None

    try:

        _reject_if_expired(db, session)

    except HTTPException:

        return None

    return session.user


