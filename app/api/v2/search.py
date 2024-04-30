import json

from bson import ObjectId
from flask import Blueprint, request, current_app
import requests

from app.models.products import Product
from app.services import get_services
from lib.http_utils import respond_success, respond_error
from lib.db_utils import to_json

search_controller = Blueprint('search_v2', __name__, url_prefix='/search')


@search_controller.route('/', methods=["POST"])
def search():
    """
    Perform a search query on ElasticSearch and MongoDB with genre substitution.

    This endpoint handles POST requests to search in ElasticSearch using the provided JSON payload,
    then fetches product details from MongoDB and substitutes the genres tags.
    If the search is successful, it returns the search results with genres data, otherwise, it logs an error and returns None.

    :return: The search results with genres data if successful, otherwise an error message.
    :rtype: dict
    """
    data = request.get_json()

    if not data or 'query' not in data:
        return {"error": "Invalid or missing 'query' in the request body"}, 400

    # TODO: we should get it from .env
    url = 'https://your-es-instance-url.com/search'
    # url = 'http://127.0.0.1:60019/search' # uncomment for localhost
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        return respond_error("Failed to fetch data from Elasticsearch.", response.status_code)

    product_ids = response.json()
    product_object_ids = [ObjectId(id_) for id_ in product_ids]

    db = get_services(current_app).db.connection
    products_collection = db["products"]

    aggregation_pipeline = [
        {'$match': {'_id': {'$in': product_object_ids}}},
        {'$lookup': {
            'from': 'tags',
            'localField': 'genres',
            'foreignField': '_id',
            'as': 'genres'
        }},
        {'$unset': 'genres._id'}
    ]

    products_cursor = products_collection.aggregate(aggregation_pipeline)

    # Create Product instances from the documents and convert to JSON
    products = to_json(products_cursor)

    return respond_success(products)
