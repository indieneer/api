from __future__ import annotations
from typing import Optional, List, Dict, Union
from bson import ObjectId
from dataclasses import dataclass, field
from .utils import slugify

from app.services import Database
from app.models.base import BaseDocument, Serializable


@dataclass
class Screenshot:
    thumbnail_url: str
    full_url: str


@dataclass
class Format:
    res_480: str
    res_max: str


@dataclass
class Movie:
    name: str
    thumbnail_url: str
    formats: Dict[str, Format]


@dataclass
class Media:
    header_url: str
    background_url: str
    screenshots: List[Screenshot]
    movies: List[Movie]


@dataclass
class PlatformOsRequirements:
    minimum: Dict[str, str]
    recommended: Dict[str, str]


@dataclass
class Requirements:
    windows: PlatformOsRequirements
    mac: PlatformOsRequirements
    linux: PlatformOsRequirements


@dataclass
class Price:
    currency: str
    initial: int
    final: int
    final_formatted: str


@dataclass
class ReleaseDate:
    date: Optional[str]
    coming_soon: bool


class Product(BaseDocument):
    type: str
    name: str
    slug: str
    required_age: int
    short_description: str
    detailed_description: str
    is_free: bool
    platforms: Dict[str, str]
    price: Dict[str, Optional[Price]]
    supported_languages: List[str]
    media: Media
    requirements: Requirements
    developers: List[str]
    publishers: List[str]
    platforms_os: List[str]
    categories: List[ObjectId]
    genres: List[ObjectId]
    release_date: ReleaseDate

    def __init__(
            self,
            type: str,
            name: str,
            slug: str,
            required_age: int,
            short_description: str,
            detailed_description: str,
            is_free: bool,
            platforms: Dict[str, str],
            price: Dict[str, Optional[Price]],
            supported_languages: List[str],
            media: Media,
            requirements: Requirements,
            developers: List[str],
            publishers: List[str],
            platforms_os: List[str],
            categories: List[str],
            genres: List[str],
            release_date: ReleaseDate,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self.type = type
        self.name = name
        self.slug = slug
        self.required_age = required_age
        self.short_description = short_description
        self.detailed_description = detailed_description
        self.is_free = is_free
        self.platforms = platforms
        self.price = price
        self.supported_languages = supported_languages
        self.media = media
        self.requirements = requirements
        self.developers = developers
        self.publishers = publishers
        self.platforms_os = platforms_os
        self.genres = genres
        self.categories = categories
        self.release_date = release_date


@dataclass
class Media(Serializable):
    header_url: str
    background_url: str
    screenshots: List[Dict[str, str]]
    movies: List[Dict[str, Union[str, Dict[str, Dict[str, str]]]]]


@dataclass
class Requirements(Serializable):
    windows: Optional[Dict[str, Dict[str]]] = None
    mac: Optional[Dict[str, Dict[str]]] = None
    linux: Optional[Dict[str, Dict[str]]] = None


@dataclass
class ProductCreate(Serializable):
    type: str
    name: str
    slug: str
    required_age: int
    short_description: str
    detailed_description: str
    is_free: bool
    platforms: Dict[str, str]
    price: Dict[str, Optional[Price]]
    supported_languages: List[str]
    media: Media
    requirements: Requirements
    developers: List[str]
    publishers: List[str]
    platforms_os: List[str]
    categories: List[str]
    genres: List[str]
    release_date: ReleaseDate


@dataclass
class ProductPatch(Serializable):
    type: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    required_age: Optional[int] = None
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    is_free: Optional[bool] = None
    # A necessary measure to prevent mutability pitfall
    platforms: Optional[Dict[str, str]] = field(default_factory=dict)
    price: Optional[Dict[str, Optional[Price]]] = field(default_factory=dict)
    supported_languages: Optional[List[str]] = field(default_factory=list)
    media: Optional[Media] = None
    requirements: Optional[Requirements] = None
    developers: Optional[List[str]] = field(default_factory=list)
    publishers: Optional[List[str]] = field(default_factory=list)
    platforms_os: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    genres: Optional[List[str]] = field(default_factory=list)
    release_date: Optional[ReleaseDate] = field(default_factory=dict)


class ProductsModel:
    """
    Model class for handling product-related database operations.

    :param db: The database instance.
    :type db: Database
    """

    db: Database
    collection: str = "products"

    def __init__(self, db: Database) -> None:
        """
        Initialize the ProductsModel.

        :param db: The database instance.
        :type db: Database
        """
        self.db = db

    def get(self, product_id: str) -> Optional[Product]:
        """
        Retrieve a product by its ID.

        :param str product_id: The ID of the product to be retrieved.
        :return: The product data if found.
        :rtype: Optional[Product]
        """
        product_data = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(product_id)})

        if product_data:
            return Product(**product_data)
        return None

    def get_all(self):
        """
        Retrieve all products from the database.

        This method fetches all products from the database and returns them as a list of Product objects.
        If there are no products found, it returns an empty list.

        :return: A list of Product objects representing all the products in the database.
        :rtype: list[Product]
        """
        products = [Product(**item) for item in self.db.connection[self.collection].find()]

        return products if products else []

    def get_by_slug(self, product_slug: str) -> Optional[Product]:
        """
        Retrieve a product by its slug.

        This method fetches a product from the database based on its unique slug.
        A slug is a human-readable, URL-friendly identifier used to represent a product.

        :param str product_slug: The slug of the product to be retrieved.
        :return: The product data if found, otherwise None.
        :rtype: Optional[Product]
        """
        product_data = self.db.connection[self.collection].find_one(
            {"slug": product_slug})

        if product_data:
            return Product(**product_data)
        return None

    def create(self, input_data: ProductCreate) -> Product:
        """
        Create a new product in the database, including a slugified name.

        :param input_data: The product data to be created.
        :type input_data: ProductCreate
        :return: The created product data.
        :rtype: Product
        """
        product = Product(**input_data.to_json())

        self.db.connection[self.collection].insert_one(product.to_bson())

        return product

    def put(self, product: Product) -> Product:
        """
        Update a product in the database.

        :param product: The product data to be updated.
        :type product: Product
        :return: The updated product data.
        :rtype: Product
        """

        self.db.connection[self.collection].insert_one(product.to_bson())
        return product

    def patch(self, product_id: str, input_data: ProductPatch) -> Optional[Product]:
        """
        Update an existing product in the database.

        :param str product_id: The ID of the product to be updated.
        :param input_data: The product data updates.
        :type input_data: ProductPatch
        :return: The updated product data if the update was successful.
        :rtype: Optional[Product]
        """
        updates = {key: value for key, value in input_data.to_json(
        ).items() if value is not None}  # Filtering out None values
        self.db.connection[self.collection].update_one(
            {"_id": ObjectId(product_id)}, {"$set": updates})

        updated_product_data = self.db.connection[self.collection].find_one(
            {"_id": ObjectId(product_id)})
        if updated_product_data:
            return Product(**updated_product_data)
        return None

    def delete(self, product_id: str) -> int:
        """
        Delete a product by its ID.

        :param str product_id: The ID of the product to be deleted.
        :return: The number of products deleted.
        :rtype: int
        """
        deletion_result = self.db.connection[self.collection].delete_one(
            {"_id": ObjectId(product_id)}
        )
        return deletion_result.deleted_count
