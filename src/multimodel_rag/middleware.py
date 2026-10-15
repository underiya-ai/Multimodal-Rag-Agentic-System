import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Adds an X-Request-ID header to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    