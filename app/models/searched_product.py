from dataclasses import dataclass
from typing import List

from bson import ObjectId

from app.models.base import BaseDocument
from app.services import Database


@dataclass
class Media:
    header_url: str


class SearchedProduct(BaseDocument):
    name: str
    slug: str
    short_description: str
    genres: List[str]
    publishers: List[str]
    price: dict
    is_free: bool
    developers: List[str]
    media: Media
    platforms_os: List[str]

    def __init__(self,
                 name: str,
                 slug: str,
                 short_description: str,
                 genres: List[str],
                 publishers: List[str],
                 price: dict,
                 is_free: bool,
                 developers: List[str],
                 media: Media,
                 platforms_os: List[str],
                 **kwargs
                 ) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.slug = slug
        self.short_description = short_description
        self.genres = genres
        self.publishers = publishers
        self.price = price
        self.is_free = is_free
        self.developers = developers
        self.media = media
        self.platforms_os = platforms_os


class SearchedProductModel:
    """
    Model class for handling searched products.

    :param db: The database service instance.
    :type db: Database
    """

    db: Database
    collection: str = "products"

    def get_aggregation_pipeline(self, product_object_ids: List[ObjectId]) -> List[dict]:
        return [
            {'$match': {'_id': {'$in': product_object_ids}}},
            {'$addFields': {'__order': {'$indexOfArray': [product_object_ids, '$_id']}}},
            {
                '$lookup': {
                    'from': 'tags',
                    'localField': 'genres',
                    'foreignField': '_id',
                    'as': 'genres'
                }
            },
            {
                '$addFields': {
                    'genres': {
                        '$reduce': {
                            'input': '$genres',
                            'initialValue': [],
                            'in': {'$concatArrays': ['$$value', ['$$this.name']]}
                        }
                    }
                }
            },
            {'$sort': {'__order': 1}},
            {
                '$project': {
                    '_id': 1,
                    'name': 1,
                    'slug': 1,
                    'short_description': 1,
                    'publishers': 1,
                    'genres': 1,
                    'price': 1,
                    'is_free': 1,
                    'developers': 1,
                    'media': {
                        'header_url': '$media.header_url'
                    },
                    'platforms_os': 1,
                }
            }
        ]

    def __init__(self, db: Database) -> None:
        """
        Initialize the SearchedProductModel with the provided database service.

        :param db: The database service instance.
        :type db: Database
        """

        self.db = db

    def search_products(self, product_object_ids: List[ObjectId]) -> List[SearchedProduct]:
        """
        Search for products based on their object IDs.

        This method performs a search for products based on the provided object IDs.

        :param product_object_ids: The list of product object IDs to search for.
        :type product_object_ids: List[str]
        :return: A dictionary containing the search results and metadata.
        :rtype: dict
        """

        products = [SearchedProduct(**item) for item in
                  self.db.connection[self.collection].aggregate(self.get_aggregation_pipeline(product_object_ids))]

        return products if products else []
