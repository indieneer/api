from dataclasses import dataclass

from .background_jobs import BackgroundJobsFactory
from .profiles import ProfilesFactory
from .products import ProductsFactory
from .tags import TagsFactory


@dataclass
class Factory:
    profiles: ProfilesFactory
    products: ProductsFactory
    tags: TagsFactory
    background_jobs: BackgroundJobsFactory
