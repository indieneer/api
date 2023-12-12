from dataclasses import dataclass
from .profiles import ProfilesFactory
from .products import ProductsFactory
from .tags import TagsFactory


@dataclass
class Factory:
    profiles: ProfilesFactory
    products: ProductsFactory
    tags: TagsFactory
