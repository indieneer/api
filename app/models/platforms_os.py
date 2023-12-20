from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable

from .exceptions import NotFoundException


class PlatformOS(BaseDocument):
    name: str

    def __init__(
        self,
        name: str,
        _id: Optional[ObjectId] = None,
        **kwargs
    ) -> None:
        super().__init__(_id)

        self.name = name


@dataclass
class PlatformOSCreate(Serializable):
    name: str


@dataclass
class PlatformOSPatch(Serializable):
    name: Optional[str] = None


class PlatformsOSModel:
    db: Database
    collection: str = "platforms_os"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, platform_os_id: str):
        platform_os = self.db.connection[self.collection].find_one({"_id": ObjectId(platform_os_id)})

        if platform_os is not None:
            return PlatformOS(**platform_os)

    def get_all(self):
        platforms_os = [PlatformOS(**item) for item in self.db.connection[self.collection].find()]

        return platforms_os if platforms_os else []

    def create(self, input_data: PlatformOSCreate):
        # Prepare platform_os data for database insertion
        platform_data = PlatformOS(**input_data.to_json()).to_json()

        # Insert the new platform_os into the database
        self.db.connection[self.collection].insert_one(platform_data)

        return PlatformOS(**platform_data)

    def patch(self, platform_os_id: str, input_data: PlatformOSPatch):
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_platform_os = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(platform_os_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_platform_os is not None:
            return PlatformOS(**updated_platform_os)
        else:
            raise NotFoundException(PlatformOS.__name__)

    def delete(self, platform_os_id: str):
        platform_os = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(platform_os_id)}
        )

        if platform_os is not None:
            return PlatformOS(**platform_os)

