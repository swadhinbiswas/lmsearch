"""Request-ID + timing middleware with structured logs."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = logging.getLogger("lmsearch.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        t0 = time.time()
        response = await call_next(request)
        ms = int((time.time() - t0) * 1000)
        response.headers["X-Request-ID"] = rid
        log.info(
            "request method=%s path=%s status=%s latency_ms=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            ms,
            rid,
        )
        return response
