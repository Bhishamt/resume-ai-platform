"""Request ID middleware — injects a correlation ID into every request.

The X-Request-ID header is:
  - Taken from the incoming request if already present (for distributed tracing)
  - Generated as a new UUID if absent

The ID is attached to:
  - The response header X-Request-ID
  - A request-scoped state variable (request.state.request_id)
  - The logging context via a ContextVar
"""

import logging
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every HTTP request and response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Make available via request.state
        request.state.request_id = request_id

        # Inject into logging context
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            return record

        logging.setLogRecordFactory(record_factory)

        try:
            response = await call_next(request)
        finally:
            logging.setLogRecordFactory(old_factory)

        response.headers["X-Request-ID"] = request_id
        return response
