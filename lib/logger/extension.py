from typing import cast

from flask import Flask
from .logger import Logger

class LoggerExtension:
    """
    Logger as injectable part of a Flask application
    """

    KEY = "logger"

    logger: Logger

    def __init__(
            self,
            logger: Logger
    ) -> None:
        self.logger = logger

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self


def get_logger(app: Flask):
    """Retrieves the Logger extension from a Flask app

    Args:
        app (Flask): flask application

    Returns:
        ModelsExtension: services
    """

    return cast(LoggerExtension, app.extensions[LoggerExtension.KEY])