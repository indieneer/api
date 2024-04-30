from flask import Blueprint, current_app, request
from math import ceil
import re

from lib.http_utils import respond_success
from app.services import get_services

search_controller = Blueprint('search', __name__, url_prefix='/search')


@search_controller.route('/', methods=["GET"])
def search():
    """
    Execute a search query on the products collection with pagination and aggregation.

    This endpoint performs a search operation on the products collection based on a query parameter.
    It supports pagination and applies an aggregation pipeline for retrieving product details along with their associated genres.
    The search is case-insensitive and matches any part of the product name.
    Pagination details such as page number, limit per page, and total count are included in the response metadata.

    :param int page: The page number for pagination, defaults to 1 if not specified.
    :param str query: The search query string, defaults to an empty string if not specified.
    :param int limit: The number of items per page, defaults to 15 if not specified.
    :return: A dictionary containing the list of matching products and pagination metadata.
    :rtype: dict
    """

    page = request.args.get("page", 1, type=int)
    query = request.args.get("query", "")
    limit = request.args.get("limit", 15, type=int)

    db = get_services(current_app).db.connection
    products = db["products"]

    aggregation_pipeline = [
        {
            '$match': {
                'name': {'$regex': re.compile(f'(?i)({query})')}
            }
        },
        {
            '$facet': {
                'items': [
                    {'$skip': (page - 1) * limit},
                    {'$limit': limit},
                    {
                        '$lookup': {
                            'from': 'tags',
                            'let': {'genreIds': '$genres'},
                            'pipeline': [
                                {'$match': {'$expr': {'$in': ['$_id', '$$genreIds']}}},
                                {'$project': {'name': 1, '_id': 0}}
                            ],
                            'as': 'genres'
                        }
                    },
                    {
                        '$lookup': {
                            'from': 'tags',
                            'let': {'categoryIds': '$categories'},
                            'pipeline': [
                                {'$match': {'$expr': {'$in': ['$_id', '$$categoryIds']}}},
                                {'$project': {'name': 1, '_id': 0}}
                            ],
                            'as': 'categories'
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
                            },
                            'categories': {
                                '$reduce': {
                                    'input': '$categories',
                                    'initialValue': [],
                                    'in': {'$concatArrays': ['$$value', ['$$this.name']]}
                                }
                            }
                        }
                    }
                ],
                'count': [{'$count': "count"}]
            }
        }
    ]

    result = (*products.aggregate(aggregation_pipeline),)

    data, count = result[0].values()
    count = count[0].get("count", 0) if len(count) != 0 else 0

    for item in data:
        item["_id"] = str(item["_id"])

    meta = {
        "total_count": count,
        "items_per_page": limit,
        "items_on_page": len(data),
        "page_count": ceil(count / limit),
        "page": page
    }

    return respond_success(data, meta=meta)


