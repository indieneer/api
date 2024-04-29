from typing import Optional, Union
from datetime import datetime
from bson import ObjectId
from dataclasses import dataclass
from slugify import slugify

from pymongo import ReturnDocument

from app.services import Database
from app.models.base import BaseDocument, Serializable

from .exceptions import NotFoundException


class Promotion(BaseDocument):
    currency: str
    value: float
    expires_at: Optional[datetime] = None

    def __init__(
        self,
        currency: str,
        value: float,
        expires_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.currency = currency
        self.value = value
        self.expires_at = expires_at


@dataclass
class PromotionCreate(Serializable):
    currency: str
    value: float
    expires_at: Optional[datetime] = None


@dataclass
class PromotionPatch(Serializable):
    currency: Optional[str] = None
    value: Optional[float] = None
    expires_at: Optional[datetime] = None


class PromotionsModel:
    db: Database
    collection: str = "promotions"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, promotion_id: str):
        """
        Retrieve a promotion's details based on its ID.

        This method searches for a promotion in the database using the provided promotion_id.
        If found, it returns a Promotion object initialized with the promotion's details.
        Otherwise, it returns None, indicating that the promotion was not found.

        :param str promotion_id: The unique identifier of the promotion.
        :return: An instance of Promotion initialized with the found promotion's details, or None if the promotion is not found.
        :rtype: Promotion | None
        """

        promotion = self.db.connection[self.collection].find_one({"_id": ObjectId(promotion_id)})

        if promotion is not None:
            return Promotion(**promotion)

    def get_all(self):
        """
        Retrieve all promotions from the database.

        This method fetches all promotions from the database and returns them as a list of Promotion objects.
        If there are no promotions found, it returns an empty list.

        :return: A list of Promotion objects representing all the promotions in the database.
        :rtype: list[Promotion]
        """
        promotions = [Promotion(**item) for item in self.db.connection[self.collection].find()]

        return promotions if promotions else []

    def create(self, input_data: PromotionCreate):
        """
        Create a new promotion in the database.

        This method takes the input data for a new promotion and inserts the new promotion into the database.
        It then returns a Promotion object initialized with the newly created promotion's details.

        :param PromotionCreate input_data: An object containing the data for the new promotion.
        :return: An instance of Promotion initialized with the newly created promotion's details.
        :rtype: Promotion
        """

        # Prepare promotion data for database insertion
        promotion_data = Promotion(**input_data.to_json()).to_bson()

        # Insert the new promotion into the database
        self.db.connection[self.collection].insert_one(promotion_data)

        return Promotion(**promotion_data)

    def put(self, input_data: Promotion):
        """
        Create a new promotion in the database with a new ID.

        This method creates a new promotion based on the provided input data.
        It converts the input data into JSON and inserts the new promotion into the database with a new ID.
        The method returns a Promotion object initialized with the newly created promotion's details, including the new ID.

        :param Promotion input_data: The data of the promotion to be created.
        :return: An instance of Promotion initialized with the newly created promotion's details, including the new ID.
        :rtype: Promotion
        """

        promotion_data = input_data.to_bson()

        # Insert the new promotion into the database
        inserted_id = self.db.connection[self.collection].insert_one(promotion_data).inserted_id
        promotion_data["_id"] = inserted_id

        return Promotion(**promotion_data)

    def patch(self, promotion_id: str, input_data: PromotionPatch):
        """
        Update a promotion in the database based on its ID.

        This method updates the promotion specified by the promotion_id using the provided input data.
        It selectively updates only the fields provided in the input_data while leaving other fields untouched.
        If the provided data is empty or invalid, it raises a ValueError.

        :param str promotion_id: The unique identifier of the promotion to be updated.
        :param PromotionPatch input_data: The data to update the promotion with.
        :return: The updated Promotion object, or raises a NotFoundException if the promotion is not found.
        :rtype: Promotion
        :raises ValueError: If no valid fields are provided for update.
        :raises NotFoundException: If the promotion with the given ID is not found.
        """

        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_promotion = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(promotion_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_promotion is not None:
            return Promotion(**updated_promotion)
        else:
            raise NotFoundException(Promotion.__name__)

    def delete(self, promotion_id: str):
        """
        Delete a promotion from the database based on its ID.

        This method locates and deletes a promotion in the database using the provided promotion_id.
        If the promotion is found and deleted, it returns a Promotion object initialized with the deleted promotion's details.
        If no promotion is found, it raises a NotFoundException.

        :param str promotion_id: The unique identifier of the promotion to be deleted.
        :return: An instance of Promotion initialized with the deleted promotion's details, or raises a NotFoundException if no promotion is found.
        :rtype: Promotion | None
        :raises NotFoundException: If the promotion with the given ID is not found.
        """

        promotion = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(promotion_id)}
        )

        if promotion is not None:
            return Promotion(**promotion)
        else:
            raise NotFoundException(Promotion.__name__)
