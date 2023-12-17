from dataclasses import dataclass
from typing import Callable, Optional
import time
import math
from datetime import datetime

from flask import Flask
from flask.wrappers import Response
from werkzeug.wrappers import Request
from .logger import Logger


@dataclass
class LoggerOptions:
    with_response_body: Optional[bool] = None
    with_request_body: Optional[bool] = None
    with_request_id: Optional[bool] = None
    
REQUEST_BODY_MAX_SIZE = 64 * 1024 # KB
RESPONSE_BODY_MAX_SIZE = 64 * 1024 # KB

class LoggerMiddleware:
    app: Flask
    wsgi_app: Callable
    logger: Logger
    options: LoggerOptions
    
    def __init__(self, app: Flask, logger: Logger, options: LoggerOptions):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.logger = logger
        self.options = options

    def __call__(self, environ, start_response):
        request = Request(environ)
        attributes = {}

        attributes["request.method"] = request.method
        attributes["request.path"] = request.path
        attributes["request.started_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        self.logger.info('path: %s, url: %s' % (request.path, request.url))

        start_time = time.time()
        response = self.wsgi_app(environ, start_response)
        latency = (time.time() - start_time) * 1000

        attributes["request.finished_at"] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        attributes["latency"] = math.floor(latency)

        body = b"".join(response)
        attributes["response.body"] = body[:RESPONSE_BODY_MAX_SIZE].decode("utf8").replace("\n", "")
        attributes["response.length"] = len(body)

        self.logger.info(" ".join([f"{attribute}={value}" for (attribute, value) in attributes.items()]))

        return [body]