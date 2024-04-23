from typing import Optional
from bson import ObjectId
from dataclasses import dataclass
from slugify import slugify

from pymongo import ReturnDocument

from app.services import Database
from app.models.base import BaseDocument, Serializable

from .exceptions import NotFoundException


class Price(BaseDocument):
    currency: str
    value: float

    def __init__(
        self,
        currency: str,
        value: float,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.currency = currency
        self.value = value


@dataclass
class PriceCreate(Serializable):
    currency: str
    value: float


@dataclass
class PricePatch(Serializable):
    currency: Optional[str] = None
    value: Optional[float] = None


class PricesModel:
    db: Database
    collection: str = "prices"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, price_id: str):
        """
        Retrieve a price's details based on its ID.

        This method searches for a price in the database using the provided price_id.
        If found, it returns a Price object initialized with the price's details.
        Otherwise, it returns None, indicating that the price was not found.

        :param str price_id: The unique identifier of the price.
        :return: An instance of Price initialized with the found price's details, or None if the price is not found.
        :rtype: Price | None
        """

        price = self.db.connection[self.collection].find_one({"_id": ObjectId(price_id)})

        if price is not None:
            return Price(**price)

    def get_all(self):
        """
        Retrieve all prices from the database.

        This method fetches all prices from the database and returns them as a list of Price objects.
        If there are no prices found, it returns an empty list.

        :return: A list of Price objects representing all the prices in the database.
        :rtype: list[Price]
        """
        prices = [Price(**item) for item in self.db.connection[self.collection].find()]

        return prices if prices else []

    def create(self, input_data: PriceCreate):
        """
        Create a new price in the database.

        This method takes the input data for a new price and inserts the new price into the database.
        It then returns a Price object initialized with the newly created price's details.

        :param PriceCreate input_data: An object containing the data for the new price.
        :return: An instance of Price initialized with the newly created price's details.
        :rtype: Price
        """

        # Prepare price data for database insertion
        price_data = Price(**input_data.to_json()).to_bson()

        # Insert the new price into the database
        self.db.connection[self.collection].insert_one(price_data)

        return Price(**price_data)

    def put(self, input_data: Price):
        """
        Create a new price in the database with a new ID.

        This method creates a new price based on the provided input data.
        It converts the input data into JSON and inserts the new price into the database with a new ID.
        The method returns a Price object initialized with the newly created price's details, including the new ID.

        :param Price input_data: The data of the price to be created.
        :return: An instance of Price initialized with the newly created price's details, including the new ID.
        :rtype: Price
        """

        price_data = input_data.to_bson()

        # Insert the new price into the database
        inserted_id = self.db.connection[self.collection].insert_one(price_data).inserted_id
        price_data["_id"] = inserted_id

        return Price(**price_data)

    def patch(self, price_id: str, input_data: PricePatch):
        """
        Update a price in the database based on its ID.

        This method updates the price specified by the price_id using the provided input data.
        It selectively updates only the fields provided in the input_data while leaving other fields untouched.
        If the provided data is empty or invalid, it raises a ValueError.

        :param str price_id: The unique identifier of the price to be updated.
        :param PricePatch input_data: The data to update the price with.
        :return: The updated Price object, or raises a NotFoundException if the price is not found.
        :rtype: Price
        :raises ValueError: If no valid fields are provided for update.
        :raises NotFoundException: If the price with the given ID is not found.
        """

        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_price = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(price_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_price is not None:
            return Price(**updated_price)
        else:
            raise NotFoundException(Price.__name__)

    def delete(self, price_id: str):
        """
        Delete a price from the database based on its ID.

        This method locates and deletes a price in the database using the provided price_id.
        If the price is found and deleted, it returns a Price object initialized with the deleted price's details.
        If no price is found, it raises a NotFoundException.

        :param str price_id: The unique identifier of the price to be deleted.
        :return: An instance of Price initialized with the deleted price's details, or raises a NotFoundException if no price is found.
        :rtype: Price | None
        :raises NotFoundException: If the price with the given ID is not found.
        """

        price = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(price_id)}
        )

        if price is not None:
            return Price(**price)
        else:
            raise NotFoundException(Price.__name__)
