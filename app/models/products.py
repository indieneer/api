from typing import Optional, List, Dict, Union
from bson import ObjectId
from dataclasses import dataclass, field

from app.services import Database
from . import BaseDocument, Serializable


class Product(BaseDocument):
    type: str
    name: str
    required_age: int
    detailed_description: str
    short_description: str
    supported_languages: List[str]
    media: Dict[str, Union[str, List[Dict[str, str]]]]
    requirements: Dict[str, Dict[str, str]]
    developers: List[str]
    publishers: List[str]
    platforms: List[str]
    genres: List[ObjectId]
    release_date: str

    def __init__(
            self,
            type: str,
            name: str,
            required_age: int,
            detailed_description: str,
            short_description: str,
            supported_languages: List[str],
            media: Dict[str, Union[str, List[Dict[str, str]]]],
            requirements: Dict[str, Dict[str, str]],
            developers: List[str],
            publishers: List[str],
            platforms: List[str],
            genres: List[ObjectId],
            release_date: str,
            _id: Optional[ObjectId] = None,
            **kwargs
    ) -> None:
        super().__init__(_id)
        self.type = type
        self.name = name
        self.required_age = required_age
        self.detailed_description = detailed_description
        self.short_description = short_description
        self.supported_languages = supported_languages
        self.media = media
        self.requirements = requirements
        self.developers = developers
        self.publishers = publishers
        self.platforms = platforms
        self.genres = genres
        self.release_date = release_date

        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class Media:
    header_url: str
    background_url: str
    screenshots: List[Dict[str, str]]
    movies: List[Dict[str, Union[str, Dict[str, Dict[str, str]]]]]


@dataclass
class Requirements:
    pc: Optional[Dict[str, str]] = None
    mac: Optional[Dict[str, str]] = None
    linux: Optional[Dict[str, str]] = None


@dataclass
class ProductCreate(Serializable):
    type: str
    name: str
    required_age: int
    detailed_description: str
    short_description: str
    supported_languages: List[str]
    media: Media
    requirements: Requirements
    developers: List[str]
    publishers: List[str]
    platforms: List[str]
    genres: List[ObjectId]
    release_date: str


@dataclass
class ProductPatch(Serializable):
    type: Optional[str] = None
    name: Optional[str] = None
    required_age: Optional[int] = None
    detailed_description: Optional[str] = None
    short_description: Optional[str] = None
    supported_languages: Optional[List[str]] = field(default_factory=list) # A necessary measure to prevent mutability pitfall
    media: Optional[Media] = None
    requirements: Optional[Requirements] = None
    developers: Optional[List[str]] = field(default_factory=list)
    publishers: Optional[List[str]] = field(default_factory=list)
    platforms: Optional[List[str]] = field(default_factory=list)
    genres: Optional[List[ObjectId]] = field(default_factory=list)
    release_date: Optional[str] = None


class ProductsModel:
    db: Database
    collection: str = "products"

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, product_id: str) -> Optional[Product]:
        """
        Retrieve a product by its ID.
        """
        product_data = self.db.connection[self.collection].find_one({"_id": ObjectId(product_id)})

        if product_data:
            return Product(**product_data)
        return None

    def create(self, input_data: ProductCreate) -> Product:
        """
        Create a new product in the database.
        """
        product_data = input_data.to_json()
        inserted_id = self.db.connection[self.collection].insert_one(product_data).inserted_id
        product_data["_id"] = inserted_id

        return Product(**product_data)

    def patch(self, product_id: str, input_data: ProductPatch) -> Optional[Product]:
        """
        Update an existing product.
        """
        updates = {key: value for key, value in input_data.to_json().items() if value is not None}  # Filtering out None values
        self.db.connection[self.collection].update_one({"_id": ObjectId(product_id)}, {"$set": updates})

        updated_product_data = self.db.connection[self.collection].find_one({"_id": ObjectId(product_id)})
        if updated_product_data:
            return Product(**updated_product_data)
        return None

    def delete(self, product_id: str) -> int:
        """
        Delete a product by its ID.
        """
        deletion_result = self.db.connection[self.collection].delete_one({"_id": ObjectId(product_id)})
        return deletion_result.deleted_count
