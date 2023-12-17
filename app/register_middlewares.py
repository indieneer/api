import sys
from flask import Flask

from lib.logger.middleware import LoggerMiddleware, LoggerOptions
from lib.logger.logger import Logger

def register_middlewares(app: Flask):
    logger = Logger(sys.stdout)
    logger_options = LoggerOptions()
    app.wsgi_app = LoggerMiddleware(app, logger, logger_options)