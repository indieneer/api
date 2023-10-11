from typing import cast

from flask import Flask

from .base import BaseDocument, Serializable
from .profiles import ProfilesModel
from .logins import LoginsModel
from .products import ProductsModel


class ModelsExtension:
    """
    Models as injectable part of a Flask application
    """

    KEY = "models"

    profiles: ProfilesModel
    logins: LoginsModel

    def __init__(
        self,
        products: ProductsModel,
        profiles: ProfilesModel,
        logins: LoginsModel
    ) -> None:
        self.products = products
        self.profiles = profiles
        self.logins = logins

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
