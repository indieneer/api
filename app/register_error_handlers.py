from flask import Flask

from lib.http_utils import respond_error
from app.middlewares import AuthError
from app.models import exceptions


def handle_auth_error(e: AuthError):
    return respond_error(e.error["description"], e.status_code)


def handle_not_found_exception(e: exceptions.NotFoundException):
    return respond_error(str(e), e.status_code)


def handle_uncaught_exceptions(e: Exception):
    return respond_error(f'{e.__class__.__name__}: {str(e)}', 500)


def register_error_handlers(app: Flask):
    app.register_error_handler(AuthError, handle_auth_error)
    app.register_error_handler(
        exceptions.NotFoundException, handle_not_found_exception)
    app.register_error_handler(Exception, handle_uncaught_exceptions)
