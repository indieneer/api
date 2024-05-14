from pymongo import ReturnDocument
from app.services import Database
from .exceptions import NotFoundException

from dataclasses import dataclass
from typing import Optional, List, Union
from bson import ObjectId
from app.models.base import BaseDocument, Serializable
from datetime import datetime


class ProductComment(BaseDocument):
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
class ProductCommentCreate(Serializable):
    profile_id: ObjectId
    text: str


@dataclass
class ProductCommentPatch(Serializable):
    text: Optional[str] = None


class ProductCommentsModel:
    db: Database
    collection: str = "product_comments"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, comment_id: str) -> Optional[ProductComment]:
        """
        Retrieve a product comment's details based on its comment ID.

        This method searches for a product comment in the database using the provided comment_id.
        If found, it returns a ProductComment object initialized with the comment's details.

        :param str comment_id: The unique identifier of the comment.
        :return: An instance of ProductComment initialized with the found comment's details, or None if the comment is not found.
        :rtype: Optional[ProductComment]
        """
        comment = self.db.connection[self.collection].find_one({"_id": ObjectId(comment_id)})
        return ProductComment(**comment) if comment else None

    def get_all(self, product_id: str) -> List[ProductComment]:
        """
        Retrieve all product comments for a specific product from the database.

        This method fetches all product comments associated with the specified product_id from the database and returns them as a list of ProductComment objects.
        If there are no product comments found, it returns an empty list.

        :param str product_id: The unique identifier of the product whose product comments are to be retrieved.
        :return: A list of ProductComment objects representing all the product comments associated with the specified product.
        :rtype: list[ProductComment]
        """
        comments = [ProductComment(**item) for item in self.db.connection[self.collection].find({"product_id": ObjectId(product_id)})]
        return comments if comments else []

    def create(self, product_id: Union[str, None], input_data: ProductCommentCreate) -> ProductComment:
        """
        Create a new product comment associated with a specific product in the database.

        This method takes the input data for a new product comment, including the optional product_id, and inserts the new product comment into the database.
        It then returns a ProductComment object initialized with the newly created product comment's details.

        :param Union[str, None] product_id: The unique identifier of the product that the product comment is optionally assigned to.
        :param ProductCommentCreate input_data: An object containing the data for the new product comment, including the profile_id and text.
        :return: An instance of ProductComment initialized with the newly created product comment's details.
        :rtype: ProductComment
        """
        input_data.product_id = ObjectId(product_id)
        comment_data = ProductComment(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(comment_data)
        return ProductComment(**comment_data)

    def put(self, comment: ProductComment) -> ProductComment:
        """
        Update a product comment in the database.

        This method directly inserts a product comment (assumed pre-existing) into the database, effectively replacing any existing comment with the same ID.
        It returns the ProductComment object initialized with the updated product comment's details.

        :param ProductComment comment: The product comment data to be updated.
        :return: The updated product comment data.
        :rtype: ProductComment
        """
        self.db.connection[self.collection].insert_one(comment.to_bson())
        return comment

    def patch(self, comment_id: str, input_data: ProductCommentPatch) -> ProductComment:
        """
        Update a product comment in the database based on its comment ID.

        This method updates the product comment specified by the comment_id using the provided input data.
        Only the fields provided in the input_data are updated; others are left untouched.

        :param str comment_id: The unique identifier of the product comment to be updated.
        :param ProductCommentPatch input_data: The data to update the product comment with.
        :return: The updated ProductComment object, or raises NotFoundException if the product comment is not found.
        :rtype: ProductComment
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}
        updated_comment = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(comment_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if not updated_comment:
            raise NotFoundException(ProductComment.__name__)
        return ProductComment(**updated_comment)

    def delete(self, comment_id: str) -> Optional[ProductComment]:
        """
        Delete a product comment from the database based on its comment ID.

        This method locates a product comment in the database using the provided comment_id and deletes it.
        If the product comment is found and deleted, it returns a ProductComment object initialized with the deleted product comment's details.
        If no product comment is found, it returns None.

        :param str comment_id: The unique identifier of the product comment to be deleted.
        :return: An instance of ProductComment initialized with the deleted product comment's details, or None if no product comment is found.
        :rtype: Optional[ProductComment]
        """
        comment = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(comment_id)}
        )
        return ProductComment(**comment) if comment else None