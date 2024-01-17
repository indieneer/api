from dataclasses import dataclass

from .background_jobs import BackgroundJobsFactory
from .profiles import ProfilesFactory
from .products import ProductsFactory
from .operating_systems import OperatingSystemsFactory
from .tags import TagsFactory
from .platforms import PlatformsFactory


@dataclass
class Factory:
    profiles: ProfilesFactory
    products: ProductsFactory
    platforms: PlatformsFactory
    operating_systems: OperatingSystemsFactory
    tags: TagsFactory
    background_jobs: BackgroundJobsFactory
