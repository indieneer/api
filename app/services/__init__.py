from typing import cast

from flask import Flask

from .database import Database
from .firebase import Firebase


class ServicesExtension:
    """Services as injectable part of a Flask application"""

    KEY = "services"

    firebase: Firebase
    db: Database

    def __init__(
        self,
        firebase: Firebase,
        db: Database
    ) -> None:
        self.firebase = firebase
        self.db = db

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self


def get_services(app: Flask):
    """
    Retrieves the Services extension from a Flask app

    Args:
        app (Flask): flask application

    Returns:
        ServicesExtension: services
    """

    return cast(ServicesExtension, app.extensions[ServicesExtension.KEY])
