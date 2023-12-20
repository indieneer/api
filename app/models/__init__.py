from typing import cast

from flask import Flask

from .platforms import PlatformsModel
from .platforms_os import PlatformsOSModel
from .profiles import ProfilesModel
from .logins import LoginsModel
from .products import ProductsModel
from .tags import TagsModel
from .background_jobs import BackgroundJobsModel


class ModelsExtension:
    """
    Models as injectable part of a Flask application
    """

    KEY = "models"

    profiles: ProfilesModel
    products: ProductsModel
    platforms: PlatformsModel
    platforms_os: PlatformsOSModel
    logins: LoginsModel
    tags: TagsModel
    background_jobs: BackgroundJobsModel

    def __init__(
        self,
        products: ProductsModel,
        profiles: ProfilesModel,
        platforms: PlatformsModel,
        platforms_os: PlatformsOSModel,
        logins: LoginsModel,
        tags: TagsModel,
        background_jobs: BackgroundJobsModel
    ) -> None:
        self.products = products
        self.profiles = profiles
        self.platforms = platforms
        self.platforms_os = platforms_os
        self.logins = logins
        self.tags = tags
        self.background_jobs = background_jobs

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
