from dataclasses import fields
import json
from math import ceil

from bson import ObjectId
from flask import Blueprint, request, current_app
import requests

from app.models import get_models
from lib.http_utils import respond_success, respond_error
from lib.db_utils import to_json

search_controller = Blueprint('search_v2', __name__, url_prefix='/search')


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
    product_object_ids = [ObjectId(_id) for _id in product_ids]
    searched_product_model = get_models(current_app).searched_product
    searched_products = searched_product_model.search_products(product_object_ids)

    count = response_json["hits"]["total"]["value"]

    meta = {
        "total_count": count,
        "items_per_page": limit,
        "items_on_page": len(searched_products),
        "page_count": ceil(count / limit),
        "page": page
    }

    return respond_success(to_json(searched_products), meta=meta)
