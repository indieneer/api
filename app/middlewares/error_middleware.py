from typing import Any, Callable

from flask_http_middleware import BaseHTTPMiddleware
from flask import Request, Response, make_response

from lib.http_utils import respond_error
from app.middlewares import AuthError
from app.models import exceptions as models_exceptions
from app.api import exceptions as handlers_exceptions


class ErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        return call_next(request)

    def error_handler(self, e: Exception):
        if isinstance(e, AuthError):
            return make_response(respond_error(e.error.get("description", "Unauthorized"), e.status_code))
        elif isinstance(e, models_exceptions.NotFoundException):
            return make_response(respond_error(str(e), 404))
        elif isinstance(e, models_exceptions.ForbiddenException):
            return make_response(respond_error(str(e), 403))
        elif isinstance(e, handlers_exceptions.BadRequestException):
            return make_response(respond_error(str(e), 400))
        elif isinstance(e, handlers_exceptions.UnprocessableEntityException):
            return make_response(respond_error(str(e), 422))
        else:
            return make_response(respond_error(str(e), 500))
