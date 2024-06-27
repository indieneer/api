from pprint import pprint

from pymongo import ReturnDocument
from app.services import Database
from .affiliates import Affiliate
from .exceptions import NotFoundException


from dataclasses import dataclass
from typing import Optional, List, Union, Dict
from bson import ObjectId
from app.models.base import BaseDocument, Serializable
from datetime import datetime

from .price import Price
from .promotions import Promotion
from .products import Product

from .affiliates import AffiliatesModel
from .products import ProductsModel


class AffiliatePlatformProduct(BaseDocument):
    affiliate_id: ObjectId
    platform_product_id: ObjectId
    product_id: ObjectId
    buy_page_url: str
    prices: List[Price]
    promotions: List[Promotion]
    affiliate: Optional[Affiliate] = None
    product: Optional[Product] = None

    def __init__(
        self,
        affiliate_id: str,
        platform_product_id: str,
        product_id: str,
        buy_page_url: str,
        prices: List[Price],
        promotions: List[Promotion],
        affiliate: Optional[Dict] = None,
        product: Optional[Dict] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.affiliate_id = ObjectId(affiliate_id)
        self.affiliate = Affiliate(**affiliate) if affiliate else None
        self.platform_product_id = ObjectId(platform_product_id)
        self.product_id = ObjectId(product_id)
        self.product = Product(**product) if product else None
        self.buy_page_url = buy_page_url
        self.prices = prices
        self.promotions = promotions

    def to_bson(self, ignore: Optional[List[str]] = None):
        return super().to_bson(ignore=["affiliate", "product"])


class AffiliatePlatformProductCreate(Serializable):
    affiliate_id: ObjectId
    platform_product_id: ObjectId
    product_id: ObjectId
    buy_page_url: str
    prices: List[Price]
    promotions: List[Promotion]

    def __init__(
        self,
        affiliate_id: ObjectId,
        platform_product_id: ObjectId,
        product_id: ObjectId,
        buy_page_url: str,
        prices: List[Price],
        promotions: List[Promotion],
        **kwargs
    ) -> None:
        self.affiliate_id = affiliate_id
        self.platform_product_id = platform_product_id
        self.product_id = product_id
        self.buy_page_url = buy_page_url
        self.prices = prices
        self.promotions = promotions


@dataclass
class AffiliatePlatformProductPatch(Serializable):
    affiliate_id: Optional[ObjectId] = None
    platform_product_id: Optional[ObjectId] = None
    product_id: Optional[ObjectId] = None
    buy_page_url: Optional[str] = None
    prices: Optional[List[Price]] = None
    promotions: Optional[List[Promotion]] = None


class AffiliatePlatformProductsModel:
    db: Database
    collection: str = "affiliate_platform_products"

    def __init__(self, db: Database) -> None:
        """
        Initializes the AffiliatePlatformProductsModel with a database instance.

        :param Database db: The database instance used to interact with the affiliate_platform_products collection.
        """
        self.db = db

    def get(self, affiliate_platform_product_id: str):
        """
        Retrieve an affiliate platform product's details based on its ID using MongoDB's aggregation pipeline.

        This method performs a join with the Affiliates and Products collections to retrieve all necessary details
        in one go.

        :param str affiliate_platform_product_id: The unique identifier of the affiliate platform product.
        :return: An instance of AffiliatePlatformProduct initialized with the found details, or None if not found.
        :rtype: AffiliatePlatformProduct | None
        """
        pipeline = [
            {"$match": {"_id": ObjectId(affiliate_platform_product_id)}},
            {"$lookup": {
                "from": AffiliatesModel.collection,
                "localField": "affiliate_id",
                "foreignField": "_id",
                "as": "affiliate"
            }},
            {"$lookup": {
                "from": ProductsModel.collection,
                "localField": "product_id",
                "foreignField": "_id",
                "as": "product"
            }},
            {"$unwind": "$affiliate"},
            {"$unwind": "$product"}
        ]

        result = self.db.connection[self.collection].aggregate(pipeline)

        if result is None:
            return None

        try:
            affiliate_platform_product = list(result)[0]
        except IndexError:
            return None

        try:
            # Construct the full affiliate platform product object including the nested affiliate and product
            affiliate_platform_product_object = AffiliatePlatformProduct(
                **affiliate_platform_product
            )
        except Exception as e:
            print(f"Error constructing AffiliatePlatformProduct: {e}")
            return None

        return affiliate_platform_product_object

    def get_all(self) -> List[AffiliatePlatformProduct]:
        """
        Retrieve all affiliate platform products from the database along with
        their related Affiliate and Product details.

        :return: A list of AffiliatePlatformProduct objects representing all the items in the database with affiliate and product data.
        :rtype: list[AffiliatePlatformProduct]
        """
        affiliate_platform_products = self.db.connection[self.collection].find()

        results = []
        for item in affiliate_platform_products:
            item = AffiliatePlatformProduct(**item)
            affiliate_id = item.affiliate_id
            product_id = item.product_id

            affiliate = self.db.connection[AffiliatesModel.collection].find_one({"_id": ObjectId(affiliate_id)})
            product = self.db.connection[ProductsModel.collection].find_one({"_id": ObjectId(product_id)})

            if affiliate and product:
                try:
                    item.affiliate = Affiliate(**affiliate)
                    item.product = Product(**product)
                except:
                    print(f'<WARN>: Some of the referenced objects are invalid for AffiliatePlatformProduct with _id {item._id}')

            results.append(item)

        return results if results else []

    def create(self, input_data: AffiliatePlatformProductCreate) -> AffiliatePlatformProduct:
        """
        Create a new affiliate platform product in the database.

        :param AffiliatePlatformProductCreate input_data: Data for the new item.
        :return: An instance of AffiliatePlatformProduct initialized with the newly created details.
        :rtype: AffiliatePlatformProduct
        """
        affiliate_platform_product_data = AffiliatePlatformProduct(**input_data.to_json()).to_bson()
        self.db.connection[self.collection].insert_one(affiliate_platform_product_data)
        return AffiliatePlatformProduct(**affiliate_platform_product_data)

    def put(self, affiliate_platform_product: AffiliatePlatformProduct) -> AffiliatePlatformProduct:
        """
        Update an affiliate platform product in the database.

        :param affiliate_platform_product: The data to be updated.
        :type affiliate_platform_product: AffiliatePlatformProduct
        :return: The updated data.
        :rtype: AffiliatePlatformProduct
        """
        self.db.connection[self.collection].insert_one(affiliate_platform_product.to_bson())
        return affiliate_platform_product

    def patch(self, affiliate_platform_product_id: str, input_data: AffiliatePlatformProductPatch) -> AffiliatePlatformProduct:
        """
        Update an affiliate platform product based on its ID.

        :param str affiliate_platform_product_id: The identifier of the item to be updated.
        :param AffiliatePlatformProductPatch input_data: Data to update the item with.
        :return: The updated AffiliatePlatformProduct object.
        :rtype: AffiliatePlatformProduct
        :raises NotFoundException: If the item is not found.
        """
        update_data = {k: v for k, v in input_data.to_json().items() if v is not None}

        if not update_data:
            raise ValueError("No valid fields provided for update.")

        updated_affiliate_platform_product = self.db.connection[self.collection].find_one_and_update(
            {"_id": ObjectId(affiliate_platform_product_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )

        if updated_affiliate_platform_product:
            return AffiliatePlatformProduct(**updated_affiliate_platform_product)
        else:
            raise NotFoundException(AffiliatePlatformProduct.__name__)

    def delete(self, affiliate_platform_product_id: str) -> Optional[AffiliatePlatformProduct]:
        """
        Delete an affiliate platform product from the database.

        :param str affiliate_platform_product_id: The identifier of the item to be deleted.
        :return: An instance of AffiliatePlatformProduct initialized with the deleted details, or None if not found.
        :rtype: AffiliatePlatformProduct | None
        :raises NotFoundException: If the item is not found.
        """
        affiliate_platform_product = self.db.connection[self.collection].find_one_and_delete(
            {"_id": ObjectId(affiliate_platform_product_id)}
        )

        if affiliate_platform_product:
            return AffiliatePlatformProduct(**affiliate_platform_product)
        else:
            raise NotFoundException(AffiliatePlatformProduct.__name__)
