from dataclasses import dataclass
from app.models.profiles import Profile

@dataclass
class Fixtures:
    regular_user: Profile
    admin_user: Profile
