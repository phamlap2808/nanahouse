from typing import Callable, Awaitable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.security import verify_token


class JwtAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, exclude_paths: list[str] | None = None):
        super().__init__(app)
        self.exclude_paths = set(exclude_paths or [])

    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable]):
        path = request.url.path

        for exclude in self.exclude_paths:
            if path.startswith(exclude):
                return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header.removeprefix("Bearer ").strip()
        email = verify_token(token)
        if not email:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        # Expose email to downstream handlers if needed
        request.state.user_email = email
        return await call_next(request)


