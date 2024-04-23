from dataclasses import dataclass

from .background_jobs import BackgroundJobsFactory
from .profiles import ProfilesFactory
from .products import ProductsFactory
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
    platforms: PlatformsFactory
    platform_products: PlatformProductsFactory
    affiliate_platform_products: AffiliatePlatformProductsFactory
    operating_systems: OperatingSystemsFactory
    tags: TagsFactory
    background_jobs: BackgroundJobsFactory
    logins: LoginsFactory
    service_profiles: ServiceProfilesFactory
