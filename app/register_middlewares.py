import sys
import os
import logging
from datetime import datetime
from flask import Flask

from lib.logger.middleware import LoggerMiddleware, LoggerOptions
from lib.logger.logger import Logger
from flask_http_middleware import MiddlewareManager
from app.middlewares.error_middleware import ErrorMiddleware

def register_middlewares(app: Flask):
    # Use the middleware manager, so that we can easily append middlewares
    app.wsgi_app = MiddlewareManager(app)

    # Add logger to non-test environments
    logging.getLogger('werkzeug').disabled = True
    if app.config["ENVIRONMENT"] != "test":
        logger = Logger(sys.stdout, app.config["ENVIRONMENT"] == "development")
        logger_options = LoggerOptions(
            with_request_body=lambda req: True,
            with_response_body=lambda req: True,
            with_request_id=True,
            custom_attributes={
                # TODO: extract rfc3339 format to a const
                "server.started_at": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "server.version": f"flask/{app.config.get('VERSION')}"
            }
        )
        app.wsgi_app.add_middleware(LoggerMiddleware, logger=logger, options=logger_options)

    app.wsgi_app.add_middleware(ErrorMiddleware)
