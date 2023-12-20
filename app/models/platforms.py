from typing import Optional
from bson import ObjectId
from dataclasses import dataclass
from slugify import slugify

from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable

from .exceptions import NotFoundException


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
        _id: Optional[ObjectId] = None,
        **kwargs
    ) -> None:
        super().__init__(_id)

        self.name = name
        self.slug = slug
        self.enabled = enabled
        self.icon_url = icon_url
        self.base_url = base_url


@dataclass
class PlatformCreate(Serializable):
    name: str
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
        """
        Retrieve a platform's details based on its ID.

        This method searches for a platform in the database using the provided platform_id.
        If found, it returns a Platform object initialized with the platform's details.

        :param str platform_id: The unique identifier of the platform.
        :return: An instance of Platform initialized with the found platform's details,
                 or None if the platform is not found.
        :rtype: Platform | None
        """
        platform = self.db.connection[self.collection].find_one({"_id": ObjectId(platform_id)})

        if platform is not None:
            return Platform(**platform)

    def get_all(self):
        """
        Retrieve all platforms from the database.

        This method fetches all platforms from the database and returns them as a list of Platform objects.
        If there are no platforms found, it returns an empty list.

        :return: A list of Platform objects representing all the platforms in the database.
        :rtype: list[Platform]
        """
        platforms = [Platform(**item) for item in self.db.connection[self.collection].find()]

        return platforms if platforms else []

    def create(self, input_data: PlatformCreate):
        """
        Create a new platform in the database.

        This method takes the input data for a new platform, generates a slug from the platform's name,
        and inserts the new platform into the database. It then returns a Platform object initialized
        with the newly created platform's details.

        :param PlatformCreate input_data: An object containing the data for the new platform.
        :return: An instance of Platform initialized with the newly created platform's details.
        :rtype: Platform
        """
        # Generate a slug from the platform's name
        input_data.slug = slugify(input_data.name)

        # Prepare platform data for database insertion
        platform_data = Platform(**input_data.to_json()).to_json()

        # Insert the new platform into the database
        self.db.connection[self.collection].insert_one(platform_data)

        return Platform(**platform_data)

    def patch(self, platform_id: str, input_data: PlatformPatch):
        """
        Update a platform in the database based on its ID.

        This method updates the platform specified by the platform ID using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str platform_id: The unique identifier of the platform to be updated.
        :param PlatformPatch input_data: The data to update the platform with.
        :return: The updated Platform object.
        :rtype: Platform
        :raises: NotFoundException if the platform is not found.
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_platform = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(platform_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        updated_platform["slug"] = slugify(updated_platform["name"])

        if updated_platform is not None:
            return Platform(**updated_platform)
        else:
            raise NotFoundException(Platform.__name__)

    def delete(self, platform_id: str):
        """
        Delete a platform from the database based on its ID.

        This method locates a platform in the database using the provided platform_id and deletes it.
        If the platform is found and deleted, it returns a Platform object initialized with the
        deleted platform's details. If no platform is found, it returns None.

        :param str platform_id: The unique identifier of the platform to be deleted.
        :return: An instance of Platform initialized with the deleted platform's details,
                 or None if no platform is found.
        :rtype: Platform | None
        """
        platform = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(platform_id)}
        )

        if platform is not None:
            return Platform(**platform)