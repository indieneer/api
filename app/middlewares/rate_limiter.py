from datetime import datetime, timedelta
from typing import Any, Callable, Dict

from flask_http_middleware import BaseHTTPMiddleware
from flask import Request, Response, make_response

from lib.http_utils import respond_error


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware for Flask
    """

    LIMIT_PER_MINUTE = 100
    storage: Dict[str, Dict[str, Any]] = {}

    def __init__(self):
        super().__init__()

    def before_request(self):
        pass

    def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        response = call_next(request)

        ip_address = request.remote_addr
        endpoint = request.endpoint
        identifier = f"{ip_address}_{endpoint}"

        current_time = datetime.now()
        record = self.storage.get(identifier)

        if record and current_time >= record["reset_time"]:
            record["count"] = 0
            record["reset_time"] = current_time + timedelta(minutes=1)

        if record and record["count"] >= self.LIMIT_PER_MINUTE:
            return make_response(respond_error("Rate limit exceeded", 429))

        if not record:
            self.storage[identifier] = {"count": 1, "reset_time": current_time + timedelta(minutes=1)}
        else:
            record["count"] += 1

        return response
