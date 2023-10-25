from flask import Blueprint, current_app, request
from math import ceil
import re

from lib.http_utils import respond_success
from app.services import get_services


search_controller = Blueprint('search', __name__, url_prefix='/search')

# Constant values definition.
ITEMS_PER_PAGE = 15


@search_controller.route('/', methods=["GET"])
def search():
    """
    Executes a search query on the products collection, applying pagination and retrieving additional details.

    :return: A list of matching products along with the pagination metadata.
    :rtype: dict
    """

    page = request.args.get("page", 1, type=int)
    query = request.args.get("query", "")

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
                    {'$skip': (page - 1) * ITEMS_PER_PAGE},
                    {'$limit': ITEMS_PER_PAGE},
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
                'count': [{'$count': "count"}]  # Take out of facet when problems start
            }
        },
    ]

    result = (*products.aggregate(aggregation_pipeline),)

    data, count = result[0].values()
    item_count = count[0].get("count", 0)

    for item in data:
        item["_id"] = str(item["_id"])

    meta = {
        "total_count": item_count,
        "items_per_page": ITEMS_PER_PAGE,
        "items_on_page": len(data),
        "page_count": ceil(item_count / ITEMS_PER_PAGE),
        "page": page
    }

    return respond_success(data, meta=meta)
