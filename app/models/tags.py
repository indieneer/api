from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from . import BaseDocument, Serializable
from .exceptions import NotFoundException


class Tag(BaseDocument):
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
class TagCreate(Serializable):
    name: str


@dataclass
class TagPatch(Serializable):
    name: Optional[str] = None


class TagsModel:
    db: Database
    collection: str = "tags"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, tag_id: str):
        """
        Retrieve a tag based on its ID.

        This method searches for a tag in the database using its unique ID.
        If found, it returns the Tag object corresponding to the tag ID.

        :param str tag_id: The unique identifier of the tag.
        :return: A Tag object if the tag is found.
        :rtype: Tag
        :raises: NotFoundException if the tag is not found.
        """
        tag = self.db.connection[self.collection].find_one({"_id": ObjectId(tag_id)})

        if tag is not None:
            return Tag(**tag)
        else:
            return None

    def get_all(self):
        """
        Retrieve all tags from the database.

        This method fetches all tags from the database and returns them as a list of Tag objects.
        If there are no tags found, it returns an empty list.

        :return: A list of Tag objects representing all the tags in the database.
        :rtype: list[Tag]
        """
        tags = [Tag(**item) for item in self.db.connection[self.collection].find()]

        return tags if tags else []

    def create(self, input_data: TagCreate):
        """
        Create a new tag in the database.

        This method creates a new tag based on the provided input data.
        It first converts the input data into JSON, then creates a Tag object,
        which is subsequently inserted into the database.

        :param TagCreate input_data: The data for creating the new tag.
        :return: The created Tag object.
        :rtype: Tag
        """
        tag_data = input_data.to_json()
        tag = Tag(**tag_data)
        self.db.connection[self.collection].insert_one(tag.to_json())

        return tag

    def put(self, input_data: Tag):
        """
        Create a new tag in the database with a new ID.

        :param input_data: The tag data to be created.
        :type input_data: Tag
        :return: The created tag data with a new ID.
        :rtype: Tag
        """
        tag_data = input_data.to_json()
        del tag_data["_id"]

        inserted_id = self.db.connection[self.collection].insert_one(tag_data).inserted_id
        tag_data["_id"] = inserted_id

        return Tag(**tag_data)

    def patch(self, tag_id: str, input_data: TagPatch):
        """
        Update a tag in the database based on its ID.

        This method updates the tag specified by the tag ID using the provided input data.
        It performs a find and update operation in the database and returns the updated tag.

        :param str tag_id: The unique identifier of the tag to be updated.
        :param TagPatch input_data: The data to update the tag with.
        :return: The updated Tag object.
        :rtype: Tag
        :raises: NotFoundException if the tag is not found.
        """
        updated_tag = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(tag_id)},
            {"$set": input_data.to_json()},
            return_document=ReturnDocument.AFTER
        )

        if updated_tag is not None:
            return Tag(**updated_tag)
        else:
            raise NotFoundException

    def delete(self, tag_id: str):
        """
        Delete a tag from the database based on its ID.

        This method finds and deletes the tag specified by the tag ID from the database.
        If the tag is found and deleted, it returns the deleted Tag object.

        :param str tag_id: The unique identifier of the tag to be deleted.
        :return: The deleted Tag object, if found and deleted successfully.
        :rtype: Tag
        :raises: NotFoundException if the tag is not found.
        """
        tag = self.db.connection[self.collection].find_one_and_delete({"_id": ObjectId(tag_id)})

        if tag is not None:
            return Tag(**tag)
        else:
            return None

