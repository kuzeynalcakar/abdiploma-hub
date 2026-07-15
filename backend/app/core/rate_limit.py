"""Simple in-process rate limiting for auth and public abuse surfaces.



Designed for single-process uvicorn. Multi-worker / multi-host deploys

should also rate-limit at the reverse proxy (shared counter).

"""



from __future__ import annotations



import threading

import time

from collections import defaultdict, deque



from fastapi import HTTPException, Request



from app.core.config import settings



_lock = threading.Lock()

_buckets: dict[str, deque[float]] = defaultdict(deque)





def reset_rate_limits() -> None:

    """Test helper — clears all buckets."""

    with _lock:

        _buckets.clear()





def _client_ip(request: Request) -> str:

    # Prefer first X-Forwarded-For hop when behind a trusted proxy.

    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:

        return forwarded.split(",")[0].strip() or "unknown"

    if request.client and request.client.host:

        return request.client.host

    return "unknown"





def enforce_rate_limit(request: Request, *, scope: str, limit: int, window_seconds: int) -> None:

    if not settings.rate_limit_enabled:

        return

    if limit <= 0:

        return



    key = f"{scope}:{_client_ip(request)}"

    now = time.monotonic()

    cutoff = now - window_seconds



    with _lock:

        bucket = _buckets[key]

        while bucket and bucket[0] < cutoff:

            bucket.popleft()

        if len(bucket) >= limit:

            raise HTTPException(

                status_code=429,

                detail="Too many requests. Please wait a moment and try again.",

                headers={"Retry-After": str(window_seconds)},

            )

        bucket.append(now)





def rate_limit_auth(request: Request) -> None:

    enforce_rate_limit(

        request,

        scope="auth",

        limit=settings.rate_limit_auth_per_minute,

        window_seconds=60,

    )





def rate_limit_public(request: Request) -> None:

    enforce_rate_limit(

        request,

        scope="public",

        limit=settings.rate_limit_public_per_minute,

        window_seconds=60,

    )


