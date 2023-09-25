from typing import cast

from flask import Flask

from .base import BaseDocument, Serializable
from .profiles import ProfilesModel


class ModelsExtension():
    """Models as injectable part of a Flask application
    """

    KEY = "models"

    profiles: ProfilesModel

    def __init__(
        self,
        profiles: ProfilesModel
    ) -> None:
        self.profiles = profiles

    def init_app(self, app: Flask):
        app.extensions[self.KEY] = self


def get_models(app: Flask):
    """Retrieves the Models extension from a Flask app

    Args:
        app (Flask): flask application

    Returns:
        ModelsExtension: services
    """

    return cast(ModelsExtension, app.extensions[ModelsExtension.KEY])
