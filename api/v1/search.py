from bson import ObjectId
from flask import Blueprint, request


import re
from math import ceil

from tools.http_utils import respond_success, respond_error
from services.database import Database as dbs

search_controller = Blueprint('search', __name__, url_prefix='/search')


@search_controller.route('/', methods=["GET"])
def search():
    try:
        page = request.args.get("page", 1, type=int)
        query = request.args.get("query", "")

        db = dbs.client.get_default_database()
        products = db["products"]

        ITEMS_PER_PAGE = 15

        data = (*products.aggregate([
            {
                '$match': {
                    'name': {'$regex': re.compile(f'(?i)({query})')}
                }
            },
            {
                '$skip': (page - 1) * ITEMS_PER_PAGE
            },
            {
                '$limit': ITEMS_PER_PAGE
            },
            {
                '$lookup': {
                    'from': 'tags',
                    'localField': 'genres',
                    'foreignField': '_id',
                    'as': 'genres'
                }
            },
            {
                '$unset': 'genres._id'
            }
        ]),)

        count = (*products.aggregate([
            {
                '$match': {
                    'name': {'$regex': re.compile(f'(?i)({query})')}
                }
            },
            {
                '$count': "count"
            }
        ]),)

        print("DEBUG MESSAGE REAL: ", data, count)

        item_count = count[0].get("count", 0)

        for d in data:
            d["_id"] = str(d["_id"])

        meta = {
            "total_count": item_count,
            "items_per_page": ITEMS_PER_PAGE,
            "items_on_page": len(data),
            "page_count": ceil(item_count / ITEMS_PER_PAGE),
            "page": page
        }

        return respond_success(data, meta=meta)

    except Exception as e:
        return respond_error(f'Internal Server Error. {e}', 500)
