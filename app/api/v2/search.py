from dataclasses import dataclass, fields
import json
from math import ceil
from typing import List

from bson import ObjectId
from flask import Blueprint, request, current_app
import requests

from app.models import ProductsModel
from app.services import get_services
from lib.http_utils import respond_success, respond_error
from lib.db_utils import to_json

search_controller = Blueprint('search_v2', __name__, url_prefix='/search')


@dataclass
class Media:
    header_url: str


@dataclass
class SearchedProduct:
    _id: str
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


def filter_fields(cls, data):
    field_names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in field_names}


@search_controller.route('/', methods=["GET"])
def search():
    """
    Perform a search query on ElasticSearch and MongoDB with genre substitution.

    This endpoint handles POST requests to search in ElasticSearch using the provided JSON payload,
    then fetches product details from MongoDB and substitutes the genres tags.
    If the search is successful, it returns the search results with genres data, otherwise, it logs an error and returns None.

    :return: The search results with genres data if successful, otherwise an error message.
    :rtype: dict
    """
    page = request.args.get("page", 1, type=int)
    query = request.args.get("query", "")
    limit = request.args.get("limit", 24, type=int)

    payload = {
        "query": query,
        "size": limit,
        "from": limit * (page - 1),
    }

    if query is None:
        return {"error": "Invalid or missing 'query' in the query parameters"}, 400

    url = f'{current_app.config["ES_HOST"]}/search'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        return respond_error("Failed to fetch data from Elasticsearch.", response.status_code)

    response_json = response.json()

    product_ids = [hit["_id"] for hit in response_json['hits']['hits']]
    product_object_ids = [ObjectId(id_) for id_ in product_ids]

    db = get_services(current_app).db.connection
    products_collection = db[ProductsModel.collection]

    aggregation_pipeline = [
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

    count = response_json["hits"]["total"]["value"]
    result = list(products_collection.aggregate(aggregation_pipeline))

    for item in result:
        item["_id"] = str(item["_id"])

    meta = {
        "total_count": count,
        "items_per_page": limit,
        "items_on_page": len(result),
        "page_count": ceil(count / limit),
        "page": page
    }

    return respond_success(to_json(result), meta=meta)
