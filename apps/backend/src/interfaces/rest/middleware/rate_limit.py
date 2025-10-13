from typing import Callable, Awaitable
from time import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.config import settings


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    buckets: dict[str, list[float]] = {}

    def __init__(self, app, *, include_paths: list[str] | None = None):
        super().__init__(app)
        self.include_paths = include_paths or []

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable]):
        path = request.url.path
        if not any(path.startswith(p) for p in self.include_paths):
            return await call_next(request)

        key = f"{request.client.host}:{path}"
        now = time()
        window = settings.rate_limit_window_seconds
        max_req = settings.rate_limit_max_requests

        bucket = self.buckets.setdefault(key, [])
        # drop old
        cutoff = now - window
        while bucket and bucket[0] < cutoff:
            bucket.pop(0)

        if len(bucket) >= max_req:
            retry_after = int(bucket[0] + window - now) + 1
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests", "retry_after": retry_after})

        bucket.append(now)
        return await call_next(request)


