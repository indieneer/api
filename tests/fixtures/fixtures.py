from dataclasses import dataclass

from app.models.background_jobs import BackgroundJob
from app.models.profiles import Profile
from app.models.products import Product
from app.models.service_profiles import ServiceProfile
from app.models.tags import Tag
from app.models.platforms import Platform
from app.models.platform_products import PlatformProduct
from app.models.affiliate_platform_products import AffiliatePlatformProduct
from app.models.operating_systems import OperatingSystem
from app.models.affiliates import Affiliate
from app.models.affiliate_reviews import AffiliateReview


@dataclass
class Fixtures:

    affiliate: Affiliate
    affiliate_review: AffiliateReview
    regular_user: Profile
    admin_user: Profile
    product: Product
    platform: Platform
    platform_product: PlatformProduct
    affiliate_platform_product: AffiliatePlatformProduct
    operating_system: OperatingSystem
    tag: Tag
    background_job: BackgroundJob
    service_profile: ServiceProfile
