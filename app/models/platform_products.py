from typing import Optional, List
from bson import ObjectId
from dataclasses import dataclass

from pymongo import ReturnDocument

from app.services import Database
from app.models.base import BaseDocument, Serializable

from .price import Price
from .exceptions import NotFoundException


class PlatformProduct(BaseDocument):
    platform_id: int
    prices: List[Price]
    product_page_url: str

    def __init__(
        self,
        platform_id: int,
        prices: List[Price],
        product_page_url: str,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.platform_id = platform_id
        self.prices = prices
        self.product_page_url = product_page_url


@dataclass
class PlatformProductCreate(Serializable):
    platform_id: int
    prices: List[Price]
    product_page_url: str


@dataclass
class PlatformProductPatch(Serializable):
    platform_id: Optional[int] = None
    prices: Optional[List[Price]] = None
    product_page_url: Optional[str] = None


class PlatformProductsModel:
    db: Database
    collection: str = "platform_products"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, platform_product_id: str):
        """
        Retrieve a platform product's details based on its ID.

        This method searches for a platform product in the database using the provided platform_product_id.
        If found, it returns a PlatformProduct object initialized with the platform product's details.
        Otherwise, it returns None, indicating that the platform product was not found.

        :param str platform_product_id: The unique identifier of the platform product.
        :return: An instance of PlatformProduct initialized with the found platform product's details, or None if the platform product is not found.
        :rtype: PlatformProduct | None
        """

        platform_product = self.db.connection[self.collection].find_one({"_id": ObjectId(platform_product_id)})

        if platform_product is not None:
            return PlatformProduct(**platform_product)

    def get_all(self):
        """
        Retrieve all platform products from the database.

        This method fetches all platform products from the database and returns them as a list of PlatformProduct objects.
        If there are no platform products found, it returns an empty list.

        :return: A list of PlatformProduct objects representing all the platform products in the database.
        :rtype: list[PlatformProduct]
        """
        platform_products = [PlatformProduct(**item) for item in self.db.connection[self.collection].find()]

        return platform_products if platform_products else []

    def create(self, input_data: PlatformProductCreate):
        """
        Create a new platform product in the database.

        This method takes the input data for a new platform product and inserts the new platform product into the database. It then returns a PlatformProduct object initialized
        with the newly created platform product's details.

        :param PlatformProductCreate input_data: An object containing the data for the new platform product.
        :return: An instance of PlatformProduct initialized with the newly created platform product's details.
        :rtype: PlatformProduct
        """

        # Prepare platform product data for database insertion
        platform_product_data = PlatformProduct(**input_data.to_json()).to_bson()

        # Insert the new platform product into the database
        self.db.connection[self.collection].insert_one(platform_product_data)

        return PlatformProduct(**platform_product_data)

    def put(self, input_data: PlatformProduct):
        """
        Create a new platform product in the database with a new ID.

        This method creates a new platform product based on the provided input data.
        It converts the input data into JSON and inserts the new platform product into the database with a new ID.
        The method returns a PlatformProduct object initialized with the newly created platform product's details.

        :param PlatformProduct input_data: The data of the platform product to be created.
        :return: An instance of PlatformProduct initialized with the newly created platform product's details, including the new ID.
        :rtype: PlatformProduct
        """

        platform_product_data = input_data.to_bson()

        # Insert the new platform product into the database
        inserted_id = self.db.connection[self.collection].insert_one(platform_product_data).inserted_id
        platform_product_data["_id"] = inserted_id

        return PlatformProduct(**platform_product_data)

    def patch(self, platform_product_id: str, input_data: PlatformProductPatch):
        """
        Update a platform product in the database based on its ID.

        This method updates the platform product specified by the platform_product_id using the provided input data.
        It selectively updates only the fields provided in the input_data while leaving other fields untouched.
        If the provided data is empty or invalid, it raises a ValueError.

        :param str platform_product_id: The unique identifier of the platform product to be updated.
        :param PlatformProductPatch input_data: The data to update the platform product with.
        :return: The updated PlatformProduct object, or raises a NotFoundException if the platform product is not found.
        :rtype: PlatformProduct
        :raises ValueError: If no valid fields are provided for update.
        :raises NotFoundException: If the platform product with the given ID is not found.
        """

        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_platform_product = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(platform_product_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_platform_product is not None:
            return PlatformProduct(**updated_platform_product)
        else:
            raise NotFoundException(PlatformProduct.__name__)

    def delete(self, platform_product_id: str):
        """
        Delete a platform product from the database based on its ID.

        This method locates and deletes a platform product in the database using the provided platform_product_id.
        If the platform product is found and deleted, it returns a PlatformProduct object initialized with the deleted platform product's details.
        If no platform product is found, it raises a NotFoundException.

        :param str platform_product_id: The unique identifier of the platform product to be deleted.
        :return: An instance of PlatformProduct initialized with the deleted platform product's details, or raises a NotFoundException if no platform product is found.
        :rtype: PlatformProduct | None
        :raises NotFoundException: If the platform product with the given ID is not found.
        """

        platform_product = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(platform_product_id)}
        )

        if platform_product is not None:
            return PlatformProduct(**platform_product)
        else:
            raise NotFoundException(PlatformProduct.__name__)
