from pymongo import ReturnDocument
from app.services import Database
from .exceptions import NotFoundException

from dataclasses import dataclass
from typing import Optional, List, Union
from bson import ObjectId
from app.models.base import BaseDocument, Serializable
from datetime import datetime


class Comment(BaseDocument):
    profile_id: ObjectId
    product_id: ObjectId
    text: str

    def __init__(
        self,
        profile_id: ObjectId,
        product_id: ObjectId,
        text: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.profile_id = ObjectId(profile_id)
        self.product_id = ObjectId(product_id)
        self.text = text


@dataclass
class CommentCreate(Serializable):
    profile_id: ObjectId
    text: str
    product_id: Optional[ObjectId] = None  # If specified, overwrites the URL param


@dataclass
class CommentPatch(Serializable):
    profile_id: Optional[ObjectId] = None
    product_id: Optional[ObjectId] = None
    text: Optional[str] = None


class CommentsModel:
    db: Database
    collection: str = "comments"

    def __init__(self, db: Database) -> None:
        """
        Initializes the CommentsModel with a database instance to manage comments within a specific collection.

        :param Database db: The database instance used to interact with the comments collection.
        """
        self.db = db

    def get(self, product_id: str, comment_id: str) -> Optional[Comment]:
        """
        Retrieve a comment's details based on its product ID and comment ID.

        This method searches for a comment in the database using the provided product_id and comment_id.
        If found, it returns a Comment object initialized with the comment's details.

        :param str product_id: The unique identifier of the product associated with the comment.
        :param str comment_id: The unique identifier of the comment.
        :return: An instance of Comment initialized with the found comment's details, or None if the comment is not found.
        :rtype: Optional[Comment]
        """
        comment = self.db.connection[self.collection].find_one({"_id": ObjectId(comment_id)})
        print(comment_id, product_id, comment)  # FIXME: different product_id in fixtures and DB
        return Comment(**comment) if comment else None

    def get_all(self, product_id: str) -> List[Comment]:
        """
        Retrieve all comments for a specific product from the database.

        This method fetches all comments associated with the specified product_id from the database and returns them as a list of Comment objects.
        If there are no comments found, it returns an empty list.

        :param str product_id: The unique identifier of the product whose comments are to be retrieved.
        :return: A list of Comment objects representing all the comments associated with the specified product.
        :rtype: list[Comment]
        """
        comments = [Comment(**item) for item in self.db.connection[self.collection].find({"product_id": ObjectId(product_id)})]
        return comments if comments else []

    def create(self, product_id: Union[str, None], input_data: CommentCreate) -> Comment:
        """
        Create a new comment associated with a specific product in the database.

        This method takes the input data for a new comment, including the product_id, and inserts the new comment into the database.
        It then returns a Comment object initialized with the newly created comment's details.

        :param str product_id: The unique identifier of the product that the comment is assigned to.
        :param CommentCreate input_data: An object containing the data for the new comment, including the product_id.
        :return: An instance of Comment initialized with the newly created comment's details.
        :rtype: Comment
        """
        if input_data.product_id is None:
            input_data.product_id = ObjectId(product_id)
        comment_data = Comment(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(comment_data)
        return Comment(**comment_data)

    def put(self, comment: Comment) -> Comment:
        """
        Update a comment in the database.

        :param comment: The comment data to be updated.
        :type comment: Comment
        :return: The updated comment data.
        :rtype: Comment
        """
        self.db.connection[self.collection].insert_one(comment.to_bson())
        return comment

    def patch(self, product_id: str, comment_id: str, input_data: CommentPatch) -> Comment:
        """
        Update a comment in the database based on its product ID and comment ID.

        This method updates the comment specified by the product_id and comment_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str product_id: The unique identifier of the product associated with the comment.
        :param str comment_id: The unique identifier of the comment to be updated.
        :param CommentPatch input_data: The data to update the comment with.
        :return: The updated Comment object, or raises NotFoundException if the comment is not found.
        :rtype: Comment
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        if not update_data:
            raise ValueError("No valid fields provided for update.")
        updated_comment = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(comment_id), "product_id": ObjectId(product_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if not updated_comment:
            raise NotFoundException(Comment.__name__)

        return Comment(**updated_comment)

    def delete(self, product_id: str, comment_id: str) -> Optional[Comment]:
        """
        Delete a comment from the database based on its product ID and comment ID.

        This method locates a comment in the database using the provided product_id and comment_id and deletes it.
        If the comment is found and deleted, it returns a Comment object initialized with the deleted comment's details.
        If no comment is found, it returns None.

        :param str product_id: The unique identifier of the product associated with the comment.
        :param str comment_id: The unique identifier of the comment to be deleted.
        :return: An instance of Comment initialized with the deleted comment's details, or None if no comment is found.
        :rtype: Optional[Comment]
        """
        comment = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(comment_id), "product_id": ObjectId(product_id)}
        )
        return Comment(**comment) if comment else None
