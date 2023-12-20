from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from app.services import Database
from . import BaseDocument, Serializable


class Platform(BaseDocument):
    name: str
    slug: str
    enabled: bool
    icon_url: str
    base_url: str

    def __init__(
        self,
        name: str,
        slug: str,
        enabled: bool,
        icon_url: str,
        base_url: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.name = name
        self.slug = slug
        self.enabled = enabled
        self.icon_url = icon_url
        self.base_url = base_url


@dataclass
class PlatformCreate(Serializable):
    name: str
    slug: str
    enabled: bool
    icon_url: str
    base_url: str


@dataclass
class PlatformPatch(Serializable):
    name: Optional[str] = None
    slug: Optional[str] = None
    enabled: Optional[bool] = None
    icon_url: Optional[str] = None
    base_url: Optional[str] = None


class PlatformsModel:
    db: Database
    collection: str = "platforms"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, platform_id: str):
        platform = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(platform_id)}
        )

        if platform is not None:
            return Platform(**platform)

    def create(self, input_data: PlatformCreate):
        platform = Platform(**input_data.to_json())

        self.db.connection[self.collection].insert_one(platform.to_bson())

        return platform

    def patch(self, user_id: str, input_data: PlatformCreate):
        raise Exception("not implemented")

    def delete(self, platform_id: str):
        platform = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(platform_id)}
        )

        if platform is not None:
            platform = Platform(**platform)
            return platform
