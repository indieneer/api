from dataclasses import dataclass

from .background_jobs import BackgroundJobsFactory
from .product_comments import ProductCommentsFactory
from .profiles import ProfilesFactory
from .products import ProductsFactory
from .guess_games import GuessGamesFactory
from .daily_guess_games import DailyGuessGamesFactory
from .game_guesses import GameGuessesFactory
from .operating_systems import OperatingSystemsFactory
from .tags import TagsFactory
from .platforms import PlatformsFactory
from .platform_products import PlatformProductsFactory
from .affiliate_platform_products import AffiliatePlatformProductsFactory
from .logins import LoginsFactory
from .service_profiles import ServiceProfilesFactory
from .affiliates import AffiliatesFactory
from .affiliate_reviews import AffiliateReviewsFactory


@dataclass
class Factory:
    affiliates: AffiliatesFactory
    affiliate_reviews: AffiliateReviewsFactory
    profiles: ProfilesFactory
    products: ProductsFactory
    guess_games: GuessGamesFactory
    daily_guess_games: DailyGuessGamesFactory
    game_guesses: GameGuessesFactory
    product_comments: ProductCommentsFactory
    platforms: PlatformsFactory
    platform_products: PlatformProductsFactory
    affiliate_platform_products: AffiliatePlatformProductsFactory
    operating_systems: OperatingSystemsFactory
    tags: TagsFactory
    background_jobs: BackgroundJobsFactory
    logins: LoginsFactory
    service_profiles: ServiceProfilesFactory
