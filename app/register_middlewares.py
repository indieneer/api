import sys
import logging
from datetime import datetime, timedelta
from flask import Flask
from flask_cors import CORS

from app.middlewares.cors_middleware import CORSMiddleware

from lib.logger.middleware import LoggerMiddleware, LoggerOptions
from lib.logger.logger import Logger
from flask_http_middleware import MiddlewareManager
from app.middlewares.error_middleware import ErrorMiddleware


def register_middlewares(app: Flask):
    # Use the middleware manager, so that we can easily append middlewares
    app.wsgi_app = MiddlewareManager(app)

    ##
    # CORS
    ##
    origins = []
    match app.config.get("ENVIRONMENT"):
        case "development":
            origins = [
                "http://localhost:3000",
                "http://localhost:4000"
            ]
        case "staging":
            origins = [
                "http://staging.indieneer.com",
                "http://web-*.indieneer.com"
            ]
        case "production":
            origins = ["http://indieneer.com"]

    app.wsgi_app.add_middleware(CORSMiddleware, options=CORS(
        origins=origins,
        allow_headers=[
            "Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token",
            "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"
        ],
        expose_headers=["Content-Length", "Access-Control-Allow-Origin"],
        supports_credentials=True,
        max_age=timedelta(hours=12),
        methods=["POST", "GET", "PATCH", "PUT", "DELETE"]
    ))

    ##
    # Logger
    ##

    # Disable default logger
    logging.getLogger('werkzeug').level = logging.WARN
    # Add logger to non-test environments
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
        app.wsgi_app.add_middleware(
            LoggerMiddleware, logger=logger, options=logger_options)

    ##
    # Error
    ##
    app.wsgi_app.add_middleware(ErrorMiddleware)
