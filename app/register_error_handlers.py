import traceback

from flask import Flask

from lib.http_utils import respond_error
from app.middlewares import AuthError
from app.models import exceptions as models_exceptions
from app.api import exceptions as handlers_exceptions


def handle_auth_error(e: AuthError):
    return respond_error(e.error["description"], e.status_code)


# Models exceptions
def handle_not_found_exception(e: models_exceptions.NotFoundException):
    return respond_error(str(e), 404)


def handle_forbidden_exception(e: models_exceptions.ForbiddenException):
    return respond_error(str(e), 403)


# Handlers exceptions
def handle_bad_request_exception(e: handlers_exceptions.BadRequestException):
    return respond_error(str(e), 400)


def handle_unprocessable_entity_exception(e: handlers_exceptions.UnprocessableEntityException):
    return respond_error(str(e), 422)


def handle_internal_server_error_exception(e: handlers_exceptions.InternalServerErrorException):
    return respond_error(str(e), 500)


def handle_uncaught_exceptions(e: Exception):
    return respond_error(f'{e.__class__.__name__}: {str(e)}', 500)


def register_error_handlers(app: Flask):
    app.register_error_handler(AuthError, handle_auth_error)
    app.register_error_handler(
        models_exceptions.NotFoundException, handle_not_found_exception)
    app.register_error_handler(
        models_exceptions.ForbiddenException, handle_forbidden_exception)
    app.register_error_handler(
        handlers_exceptions.BadRequestException, handle_bad_request_exception)
    app.register_error_handler(
        handlers_exceptions.UnprocessableEntityException, handle_unprocessable_entity_exception)
    app.register_error_handler(
        handlers_exceptions.InternalServerErrorException, handle_internal_server_error_exception)
    app.register_error_handler(Exception, handle_uncaught_exceptions)
