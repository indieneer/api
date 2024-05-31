from typing import cast

from flask import Flask

from .affiliate_reviews import AffiliateReviewsModel
from .affiliates import AffiliatesModel
from .daily_guess_games import DailyGuessGamesModel
from .game_guesses import GameGuessesModel
from .guess_games import GuessGamesModel
from .product_comments import ProductCommentsModel
from .platforms import PlatformsModel
from .platform_products import PlatformProductsModel
from .affiliate_platform_products import AffiliatePlatformProductsModel
from .operating_systems import OperatingSystemsModel
from .profiles import ProfilesModel
from .logins import LoginsModel
from .products import ProductsModel
from .tags import TagsModel
from .background_jobs import BackgroundJobsModel
from .service_profiles import ServiceProfilesModel


class ModelsExtension:
    """
    Models as injectable part of a Flask application
    """

    KEY = "models"

    profiles: ProfilesModel
    products: ProductsModel
    guess_games: GuessGamesModel
    daily_guess_games: DailyGuessGamesModel
    game_guesses: GameGuessesModel
    platforms: PlatformsModel
    platform_products: PlatformProductsModel
    affiliate_platform_products: AffiliatePlatformProductsModel
    operating_systems: OperatingSystemsModel
    logins: LoginsModel
    tags: TagsModel
    background_jobs: BackgroundJobsModel
    service_profiles: ServiceProfilesModel
    product_comments: ProductCommentsModel
    affiliates: AffiliatesModel
    affiliate_reviews: AffiliateReviewsModel

    def __init__(
        self,
        product_comments: ProductCommentsModel,
        affiliates: AffiliatesModel,
        affiliate_reviews: AffiliateReviewsModel,
        products: ProductsModel,
        guess_games: GuessGamesModel,
        daily_guess_games: DailyGuessGamesModel,
        game_guesses: GameGuessesModel,
        profiles: ProfilesModel,
        platforms: PlatformsModel,
        platform_products: PlatformProductsModel,
        affiliate_platform_products: AffiliatePlatformProductsModel,
        operating_systems: OperatingSystemsModel,
        logins: LoginsModel,
        tags: TagsModel,
        background_jobs: BackgroundJobsModel,
        service_profiles: ServiceProfilesModel
    ) -> None:
        self.product_comments = product_comments
        self.affiliates = affiliates
        self.affiliate_reviews = affiliate_reviews
        self.products = products
        self.guess_games = guess_games
        self.daily_guess_games = daily_guess_games
        self.game_guesses = game_guesses
        self.profiles = profiles
        self.platforms = platforms
        self.platform_products = platform_products
        self.affiliate_platform_products = affiliate_platform_products
        self.operating_systems = operating_systems
        self.logins = logins
        self.tags = tags
        self.background_jobs = background_jobs
        self.service_profiles = service_profiles

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
