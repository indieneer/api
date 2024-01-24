from typing import Callable, cast
from flask_http_middleware import BaseHTTPMiddleware
from flask import Flask, Request, Response
from flask_cors import CORS

CORSHandler = Callable[[Response], Response]


def create_cors_handler(options: CORS) -> CORSHandler:
    """Creates a CORS response handler from the passed options
    """

    # create a temporary app for handler extraction
    app = Flask("tmp")

    # register after request handler and extract it
    options.init_app(app)
    cors_handler = app.after_request_funcs.setdefault(None, []).pop()

    return cast(CORSHandler, cors_handler)


class CORSMiddleware(BaseHTTPMiddleware):
    cors_handler: CORSHandler

    def __init__(self, options: CORS):
        super().__init__()

        self.cors_handler = create_cors_handler(options)

    def dispatch(self, request: Request, call_next: Callable[..., Response]) -> Response:
        response = call_next(request)

        return self.cors_handler(response)
