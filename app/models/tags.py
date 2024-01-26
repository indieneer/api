from typing import Optional
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from app.models.base import BaseDocument, Serializable
from .exceptions import NotFoundException


class Tag(BaseDocument):
    name: str

    def __init__(
        self,
        name: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

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
        If the tag is found, it returns the corresponding Tag object; otherwise, it returns None, indicating the tag does not exist.

        :param str tag_id: The unique identifier of the tag.
        :return: A Tag object if the tag is found, otherwise None.
        :rtype: Tag or None
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

        This method adds a new tag to the database based on the provided input data.
        It converts the input data into a Tag object before inserting it into the database.
        The created Tag object is then returned.

        :param TagCreate input_data: The data used for creating the new tag.
        :return: The newly created Tag object.
        :rtype: Tag
        """

        tag = Tag(**input_data.to_json())

        self.db.connection[self.collection].insert_one(tag.to_bson())

        return tag

    def put(self, tag: Tag):
        """
        Create a new tag in the database.

        This method adds a new tag to the database using the provided Tag object.
        The tag is inserted into the database and returned with its new ID.

        :param Tag tag: The Tag object containing data for the new tag.
        :return: The newly created Tag object with its assigned ID.
        :rtype: Tag
        """

        self.db.connection[self.collection].insert_one(tag.to_bson())
        return tag

    def patch(self, tag_id: str, input_data: TagPatch):
        """
        Update a tag in the database based on its ID.

        This method updates an existing tag, identified by the tag ID, using the provided input data.
        The tag is located and updated in the database, and the updated Tag object is returned.
        If the tag is not found, a NotFoundException is raised.

        :param str tag_id: The unique identifier of the tag to be updated.
        :param TagPatch input_data: The data used to update the tag.
        :return: The updated Tag object, if the tag is found.
        :rtype: Tag
        :raises NotFoundException: If the tag with the specified ID is not found.
        """

        updated_tag = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(tag_id)},
            {"$set": input_data.to_json()},
            return_document=ReturnDocument.AFTER
        )

        if updated_tag is not None:
            return Tag(**updated_tag)
        else:
            raise NotFoundException(Tag.__name__)

    def delete(self, tag_id: str):
        """
        Delete a tag from the database based on its ID.

        This method removes a tag from the database using the provided tag ID.
        If the tag is found and successfully deleted, the method returns the deleted Tag object.
        If the tag is not found, a NotFoundException is raised.

        :param str tag_id: The unique identifier of the tag to be deleted.
        :return: The deleted Tag object, if the tag is found and deleted.
        :rtype: Tag
        :raises NotFoundException: If the tag with the specified ID is not found.
        """

        tag = self.db.connection[self.collection].find_one_and_delete({"_id": ObjectId(tag_id)})

        if tag is not None:
            return Tag(**tag)
        else:
            raise NotFoundException(Tag.__name__)

