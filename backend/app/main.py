import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.error_buffer import record_error
from app.core.logging_config import configure_logging
from app.core.request_logging import RequestLoggingMiddleware, register_db_timing
from app.core.sentry_setup import capture_exception, init_sentry
from app.database.session import engine
from app.routes import (
    admin,
    answers,
    auth,
    courses,
    daily_practice,
    feedback,
    health,
    progress,
    quiz,
    weakness_map,
)

configure_logging(structured=settings.structured_logging or settings.environment == "production")
init_sentry()
register_db_timing(engine)

logger = logging.getLogger("albertaprep")

_docs_url = "/docs" if settings.enable_api_docs else None
_redoc_url = "/redoc" if settings.enable_api_docs else None
_openapi_url = "/openapi.json" if settings.enable_api_docs else None

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# Explicit origins only. Credentials require non-wildcard allowlist.
_cors_origins = settings.cors_allow_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Key"],
    expose_headers=["Retry-After"],
    max_age=600,
)

logger.info(
    "Runtime settings: environment=%s frontend_url=%s cors_origins=%s auth_cookie_name=%s cookie_secure=%s cookie_samesite=%s",
    settings.environment,
    settings.frontend_url,
    _cors_origins,
    settings.auth_cookie_name,
    settings.cookie_secure,
    settings.cookie_samesite,
)

app.add_middleware(RequestLoggingMiddleware)


@app.middleware("http")
async def limit_request_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            size = int(content_length)
        except ValueError:
            size = -1
        if size > settings.max_request_body_bytes:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body is too large."},
            )
    return await call_next(request)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Permissions-Policy",
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    )
    # HSTS only in production (or when ENABLE_HSTS=true). Set at the TLS
    # terminator as well; see SSL_SETUP.md. Never enable without HTTPS.
    if settings.hsts_enabled:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response


def _sanitize_validation_errors(errors: list) -> list[dict]:
    """Strip input/ctx that may contain passwords or other sensitive values."""
    safe: list[dict] = []
    for err in errors:
        item: dict = {
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "type": err.get("type"),
        }
        safe.append(item)
    return safe


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    if exc.status_code >= 500:
        logger.error(
            "http_error status=%s path=%s detail=%s",
            exc.status_code,
            request.url.path,
            exc.detail,
        )
        record_error(
            endpoint=request.url.path,
            status_code=exc.status_code,
            error_type="HTTPException",
            message=str(exc.detail),
        )
        capture_exception(exc, path=request.url.path, status=exc.status_code)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    safe = _sanitize_validation_errors(exc.errors())
    logger.info(
        "validation_error path=%s method=%s count=%s",
        request.url.path,
        request.method,
        len(safe),
    )
    return JSONResponse(status_code=422, content={"detail": safe})


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception(
        "unhandled_exception path=%s method=%s",
        request.url.path,
        request.method,
    )
    record_error(
        endpoint=request.url.path,
        status_code=500,
        error_type=type(exc).__name__,
        message=str(exc),
    )
    capture_exception(exc, path=request.url.path, method=request.method)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again."},
    )


# Root aliases for common load-balancer / k8s probes (same payloads).
app.add_api_route("/health", health.health_check, methods=["GET"], include_in_schema=False)
app.add_api_route("/ready", health.readiness_check, methods=["GET"], include_in_schema=False)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")
app.include_router(answers.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(weakness_map.router, prefix="/api/v1")
app.include_router(daily_practice.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

