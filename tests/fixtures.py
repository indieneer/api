from dataclasses import dataclass
from app.models.profiles import Profile
from app.models.products import Product
from app.models.tags import Tag


@dataclass
class Fixtures:
    regular_user: Profile
    admin_user: Profile
    product: Product
    tag: Tag
