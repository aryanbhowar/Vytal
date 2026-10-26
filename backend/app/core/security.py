"""HTTP protections: security headers, request size limit and a simple rate limiter.

These are sensible defaults for a single-server deployment. A public deployment
should ALSO sit behind HTTPS and a reverse proxy with its own limits
(see docs/deployment/DEPLOYMENT.md); an in-process limiter alone is not enough
against a determined attacker, and it resets when the server restarts.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# The app loads no third-party scripts, fonts or images, so everything can be
# restricted to its own origin. 'unsafe-inline' for styles allows React's style
# attributes. /docs (Swagger UI) loads from a CDN, so it gets a separate policy.
APP_CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; "
    "frame-ancestors 'none'"
)
DOCS_CSP = (
    "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; img-src 'self' data: https://fastapi.tiangolo.com; "
    "frame-ancestors 'none'"
)
DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = response.headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "no-referrer"
        headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        headers["Content-Security-Policy"] = DOCS_CSP if request.url.path.startswith(DOCS_PATHS) else APP_CSP
        if request.url.path.startswith("/api/assessment"):
            # Health answers and results must not be stored by browsers or proxies.
            headers["Cache-Control"] = "no-store"
            headers["Pragma"] = "no-cache"
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject bodies over the limit before they are read into memory."""

    def __init__(self, app, max_bytes: int):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            declared = request.headers.get("content-length")
            if declared is None:
                return JSONResponse({"detail": "A Content-Length header is required."}, status_code=411)
            if not declared.isdigit() or int(declared) > self.max_bytes:
                return JSONResponse({"detail": "Request body is too large."}, status_code=413)
        return await call_next(request)


class SlidingWindowRateLimiter:
    """At most `limit` requests per client in any 60-second window (thread-safe, in memory)."""

    WINDOW_SECONDS = 60.0

    def __init__(self, limit: int):
        self.limit = limit
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, client: str, now: float | None = None) -> bool:
        if self.limit <= 0:
            return True
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits[client]
            while hits and now - hits[0] >= self.WINDOW_SECONDS:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True
