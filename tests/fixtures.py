from dataclasses import dataclass
from app.models.profiles import Profile
from app.models.products import Product
from app.models.tags import Tag
from app.models.platforms import Platform
from app.models.operating_systems import OperatingSystem


@dataclass
class Fixtures:
    regular_user: Profile
    admin_user: Profile
    product: Product
    platform: Platform
    operating_system: OperatingSystem
    tag: Tag
