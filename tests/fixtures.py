from dataclasses import dataclass
from app.models.profiles import Profile
from app.models.products import Product


@dataclass
class Fixtures:
    regular_user: Profile
    admin_user: Profile
    product: Product
