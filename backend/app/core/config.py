from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[2] is the backend package root
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_DEFAULT_DB = _BACKEND_DIR / "albertaprep.db"

_DEFAULT_DEV_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
)


def _resolve_sqlite_url(url: str) -> str:
    """Keep the SQLite file in backend/ even when uvicorn is launched elsewhere."""
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        rel = url[len(prefix) :]
        abs_path = (_BACKEND_DIR / rel).resolve()
        return f"sqlite:///{abs_path.as_posix()}"
    return url


class Settings(BaseSettings):
    app_name: str = "ABDiploma Hub API"
    database_url: str = f"sqlite:///{_DEFAULT_DB.as_posix()}"
    admin_api_key: str | None = None
    # Comma-separated emails allowed to use the admin dashboard (e.g. you@example.com).
    admin_emails: str | None = None

    # Application signing secret (guest quiz HMAC fallback, future signed payloads).
    # Required in production — generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
    secret_key: str | None = None

    # Session lifetime (hours). Expired sessions are rejected and deleted.
    session_ttl_hours: int = 168  # 7 days

    # HttpOnly session cookie (same-origin SPA via reverse proxy / Vite proxy).
    auth_cookie_name: str = "albertaprep_session"
    # When None, Secure is True automatically if ENVIRONMENT=production.
    auth_cookie_secure: bool | None = None
    auth_cookie_samesite: str | None = None  # lax | strict | none; defaults to none in production, lax in development if unset

    # In-process rate limits (also configure at reverse proxy in production).
    rate_limit_enabled: bool = True
    rate_limit_auth_per_minute: int = 10
    rate_limit_public_per_minute: int = 30

    # OpenAPI /docs — off by default for production safety.
    enable_api_docs: bool = False

    # Comma-separated allowed browser origins for CORS (never "*").
    # Example: https://abdiplomahub.com,https://www.abdiplomahub.com
    frontend_url: str | None = None

    # Max JSON request body size in bytes (default 64 KiB).
    max_request_body_bytes: int = 65_536

    # Optional HMAC secret for guest quiz binding cookies (falls back to SECRET_KEY).
    guest_quiz_signing_secret: str | None = None

    # Observability
    environment: str = "development"  # development | production
    app_version: str = "1.0.0"
    sentry_dsn: str | None = None
    structured_logging: bool = False
    slow_request_threshold_ms: int = 1000

    # Backups (directory must not be web-served)
    backup_dir: str | None = None  # default: backend/backups
    backup_retention_days: int = 14

    # Enable HSTS only when True, or automatically in production.
    # Prefer terminating TLS at the reverse proxy; see SSL_SETUP.md.
    enable_hsts: bool | None = None

    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("auth_cookie_secure", "enable_hsts", mode="before")
    @classmethod
    def empty_optional_bool(cls, value):
        if value is None or value == "":
            return None
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"", "none", "null"}:
                return None
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        return _resolve_sqlite_url(value)

    @field_validator("auth_cookie_samesite", mode="before")
    @classmethod
    def normalize_samesite(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip().lower()
        if normalized in {"", "none", "null"}:
            return None
        allowed = {"lax", "strict", "none"}
        if normalized not in allowed:
            return "lax"
        return normalized

    @property
    def cookie_samesite(self) -> str:
        if self.auth_cookie_samesite is not None:
            return self.auth_cookie_samesite
        return "none" if self.is_production else "lax"

    @field_validator("session_ttl_hours", mode="before")
    @classmethod
    def normalize_ttl(cls, value) -> int:
        try:
            hours = int(value)
        except (TypeError, ValueError):
            return 168
        return max(1, hours)

    @field_validator("max_request_body_bytes", mode="before")
    @classmethod
    def normalize_body_limit(cls, value) -> int:
        try:
            size = int(value)
        except (TypeError, ValueError):
            return 65_536
        return max(1024, size)

    @field_validator("slow_request_threshold_ms", mode="before")
    @classmethod
    def normalize_slow_threshold(cls, value) -> int:
        try:
            ms = int(value)
        except (TypeError, ValueError):
            return 1000
        return max(50, ms)

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        env = str(value or "development").strip().lower()
        if env in {"prod", "production"}:
            return "production"
        return "development"

    @field_validator("backup_retention_days", mode="before")
    @classmethod
    def normalize_retention(cls, value) -> int:
        try:
            days = int(value)
        except (TypeError, ValueError):
            return 14
        return max(1, days)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cookie_secure(self) -> bool:
        """Secure cookies: on in production unless AUTH_COOKIE_SECURE is explicitly false."""
        if self.auth_cookie_secure is not None:
            return bool(self.auth_cookie_secure)
        return self.is_production

    @property
    def hsts_enabled(self) -> bool:
        if self.enable_hsts is not None:
            return bool(self.enable_hsts)
        return self.is_production

    def signing_secret(self) -> str | None:
        """Preferred signing material: GUEST_QUIZ_SIGNING_SECRET, else SECRET_KEY."""
        for candidate in (self.guest_quiz_signing_secret, self.secret_key):
            if candidate and str(candidate).strip():
                return str(candidate).strip()
        return None

    def cors_allow_origins(self) -> list[str]:
        """Explicit origins only — wildcards are rejected."""
        raw = (self.frontend_url or "").strip()
        if not raw:
            return list(_DEFAULT_DEV_ORIGINS)
        origins: list[str] = []
        for part in raw.split(","):
            origin = part.strip().rstrip("/")
            if not origin:
                continue
            if origin == "*":
                raise ValueError(
                    "FRONTEND_URL must not contain '*'. List explicit origins."
                )
            origins.append(origin)
        return origins or list(_DEFAULT_DEV_ORIGINS)


settings = Settings()

