from dataclasses import dataclass
from .profiles import ProfilesFactory
from .products import ProductsFactory


@dataclass
class Factory:
    profiles: ProfilesFactory
    products: ProductsFactory
