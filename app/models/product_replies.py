from pymongo import ReturnDocument
from app.services import Database
from .exceptions import NotFoundException

from dataclasses import dataclass
from typing import Optional, List, Union
from bson import ObjectId
from app.models.base import BaseDocument, Serializable


class ProductReply(BaseDocument):
    profile_id: ObjectId
    comment_id: ObjectId
    text: str

    def __init__(
        self,
        profile_id: Union[ObjectId, str],
        comment_id: Union[ObjectId, str],
        text: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.profile_id = ObjectId(profile_id)
        self.comment_id = ObjectId(comment_id)
        self.text = text


@dataclass
class ProductReplyCreate(Serializable):
    profile_id: Union[ObjectId, str]
    comment_id: Union[ObjectId, str]
    text: str


@dataclass
class ProductReplyPatch(Serializable):
    text: Optional[str] = None


class ProductRepliesModel:
    db: Database
    collection: str = "product_replies"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, reply_id: str) -> Optional[ProductReply]:
        """
        Retrieve a product reply's details based on its reply ID.

        This method searches for a product reply in the database using the provided reply_id.
        If found, it returns a ProductReply object initialized with the reply's details.

        :param str reply_id: The unique identifier of the reply.
        :return: An instance of ProductReply initialized with the found reply's details, or None if the reply is not found.
        :rtype: Optional[ProductReply]
        """
        reply = self.db.connection[self.collection].find_one({"_id": ObjectId(reply_id)})
        return ProductReply(**reply) if reply else None

    def get_all(self, comment_id: str) -> List[ProductReply]:
        """
        Retrieve all product replies for a specific comment from the database.

        This method fetches all product replies associated with the specified comment_id from the database and returns them as a list of ProductReply objects.
        If there are no product replies found, it returns an empty list.

        :param str comment_id: The unique identifier of the comment whose replies are to be retrieved.
        :return: A list of ProductReply objects representing all the replies associated with the specified comment.
        :rtype: list[ProductReply]
        """
        replies = [ProductReply(**item) for item in self.db.connection[self.collection].find({"comment_id": ObjectId(comment_id)})]
        return replies if replies else []

    def create(self, input_data: ProductReplyCreate) -> ProductReply:
        """
        Create a new product reply associated with a specific comment in the database.

        This method takes the input data for a new product reply, including the optional comment_id, and inserts the new reply into the database.
        It then returns a ProductReply object initialized with the newly created reply's details.

        :param ProductReplyCreate input_data: An object containing the data for the new product reply, including the profile_id and text.
        :return: An instance of ProductReply initialized with the newly created reply's details.
        :rtype: ProductReply
        """
        reply_data = ProductReply(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(reply_data)
        return ProductReply(**reply_data)

    def put(self, reply: ProductReply) -> ProductReply:
        """
        Update a product reply in the database.

        This method directly inserts a product reply (assumed pre-existing) into the database, effectively replacing any existing reply with the same ID.
        It returns the ProductReply object initialized with the updated reply's details.

        :param ProductReply reply: The product reply data to be updated.
        :return: The updated product reply data.
        :rtype: ProductReply
        """
        self.db.connection[self.collection].insert_one(reply.to_bson())
        return reply

    def patch(self, reply_id: str, input_data: ProductReplyPatch) -> ProductReply:
        """
        Update a product reply in the database based on its reply ID.

        This method updates the product reply specified by the reply_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str reply_id: The unique identifier of the product reply to be updated.
        :param ProductReplyPatch input_data: The data to update the product reply with.
        :return: The updated ProductReply object, or raises NotFoundException if the product reply is not found.
        :rtype: ProductReply
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_reply = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(reply_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_reply:
            raise NotFoundException(ProductReply.__name__)
        return ProductReply(**updated_reply)

    def delete(self, reply_id: str) -> Optional[ProductReply]:
        """
        Delete a product reply from the database based on its reply ID.

        This method locates a product reply in the database using the provided reply_id and deletes it.
        If the product reply is found and deleted, it returns a ProductReply object initialized with the deleted reply's details.
        If no product reply is found, it returns None.

        :param str reply_id: The unique identifier of the product reply to be deleted.
        :return: An instance of ProductReply initialized with the deleted reply's details, or None if no product reply is found.
        :rtype: Optional[ProductReply]
        """
        reply = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(reply_id)}
        )

        if reply is None:
            raise NotFoundException(model_name=ProductReply.__name__)

        return ProductReply(**reply)
