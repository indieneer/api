import json

from flask import Blueprint, current_app, request
from math import ceil
import re

from lib.http_utils import respond_success
from app.services import get_services
import requests

search_controller = Blueprint('search', __name__, url_prefix='/search')


@search_controller.route('/', methods=["GET"])
def search():
    """
    Executes a search query on the products collection, applying pagination and retrieving additional details.

    :return: A list of matching products along with the pagination metadata.
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
                            'localField': 'genres',
                            'foreignField': '_id',
                            'as': 'genres'
                        }
                    },
                    {'$unset': 'genres._id'}
                ],
                # Take out of facet when problems start
                'count': [{'$count': "count"}]
            }
        },
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


@search_controller.route('/elasticsearch', methods=["GET"])
def search_elasticsearch():
    """
    Perform a search query on ElasticSearch.

    This endpoint handles GET requests to search in ElasticSearch using the provided query parameters.
    It constructs a search payload and sends it to the ElasticSearch service. If the search is successful,
    it returns the search results, otherwise, it logs an error and returns None.

    :param str query: The search query provided as a query parameter, defaults to an empty string.
    :param int size: The number of search results to return, defaults to 15.
    :return: The search results if the request is successful, otherwise None.
    :rtype: dict or None
    """
    query = request.args.get('query', '')
    size = request.args.get('size', 15, type=int)

    # TODO: Move to .env
    url = 'https://indieneer-es-15d49606cdd6.herokuapp.com/search'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'query': query,
        'size': size
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

