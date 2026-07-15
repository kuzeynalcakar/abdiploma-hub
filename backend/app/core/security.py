"""Password hashing and session token helpers.



Uses only the standard library: PBKDF2-HMAC-SHA256 for passwords and

secrets for opaque session tokens. No JWT — sessions are stored in the

database so logout can revoke them immediately.



Session secrets are never stored plaintext: only SHA-256 hashes are

persisted. Clients hold the raw token (HttpOnly cookie and/or Bearer).

"""



from __future__ import annotations



import hashlib

import hmac

import secrets

from datetime import datetime, timedelta, timezone



_ALGORITHM = "pbkdf2_sha256"

_ITERATIONS = 200_000





def hash_password(password: str) -> str:

    salt = secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(

        "sha256", password.encode(), salt.encode(), _ITERATIONS

    ).hex()

    return f"{_ALGORITHM}${_ITERATIONS}${salt}${digest}"





def verify_password(password: str, stored: str) -> bool:

    try:

        algorithm, iterations, salt, digest = stored.split("$")

        if algorithm != _ALGORITHM:

            return False

        candidate = hashlib.pbkdf2_hmac(

            "sha256", password.encode(), salt.encode(), int(iterations)

        ).hex()

        return hmac.compare_digest(candidate, digest)

    except (ValueError, AttributeError):

        return False





def generate_session_token() -> str:

    """Return a high-entropy opaque token for the client (never store as-is)."""

    return secrets.token_urlsafe(32)





def hash_session_token(token: str) -> str:

    """One-way hash for database storage. SHA-256 is sufficient for

    high-entropy random tokens (this is not a password hash)."""

    return hashlib.sha256(token.encode("utf-8")).hexdigest()





def tokens_match(raw_token: str, stored_hash: str) -> bool:

    """Constant-time compare of client token against stored hash."""

    if not raw_token or not stored_hash:

        return False

    return hmac.compare_digest(hash_session_token(raw_token), stored_hash)





def utcnow() -> datetime:

    return datetime.now(timezone.utc)





def session_expiry(ttl_hours: int) -> datetime:

    return utcnow() + timedelta(hours=ttl_hours)


