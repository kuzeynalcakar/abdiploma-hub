from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.admin import is_admin_user
from app.core.config import settings
from app.core.deps import extract_raw_session_token, get_current_user
from app.core.rate_limit import rate_limit_auth
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiry,
    verify_password,
)
from app.core.session_cookie import clear_session_cookie, set_session_cookie
from app.database.session import get_db
from app.models import User, UserSession
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_bearer = HTTPBearer(auto_error=False)


def _user_payload(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        name=user.name,
        email=user.email,
        is_admin=is_admin_user(user),
    )


def _open_session(db: Session, user: User) -> str:
    raw_token = generate_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token=hash_session_token(raw_token),
            expires_at=session_expiry(settings.session_ttl_hours),
        )
    )
    db.commit()
    return raw_token


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_auth),
):
    email = payload.email.lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists. Try logging in.",
        )

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        # Race: another request registered the same email between our
        # existence check and this insert. Same friendly message.
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists. Try logging in.",
        )
    token = _open_session(db, user)
    set_session_cookie(response, token)
    return {"token": token, "user": _user_payload(user)}


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_auth),
):
    user = (
        db.query(User).filter(User.email == payload.email.lower()).first()
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password.",
        )

    token = _open_session(db, user)
    set_session_cookie(response, token)
    return {"token": token, "user": _user_payload(user)}


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
):
    raw = extract_raw_session_token(request, credentials)
    if raw:
        token_hash = hash_session_token(raw)
        db.query(UserSession).filter(UserSession.token == token_hash).delete()
        db.commit()
    clear_session_cookie(response)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _user_payload(current_user)
