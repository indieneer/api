from dataclasses import dataclass
from .profiles import ProfilesFactory


@dataclass
class Factory:
    profiles: ProfilesFactory
