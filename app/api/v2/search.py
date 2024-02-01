import json
from flask import Blueprint, request
import requests

from lib.http_utils import respond_success, respond_error

search_controller = Blueprint('search_v2', __name__, url_prefix='/search')


@search_controller.route('/', methods=["POST"])
def search():
    """
    Perform a search query on ElasticSearch.

    This endpoint handles POST requests to search in ElasticSearch using the provided JSON payload.
    The client sends a JSON object conforming to the ElasticSearch query DSL.
    If the search is successful, it returns the search results, otherwise, it logs an error and returns None.

    :return: The search results if the request is successful, otherwise an error message.
    :rtype: dict
    """
    # Expecting a JSON payload with the query and size
    data = request.get_json()

    if not data or 'query' not in data:
        return {"error": "Invalid or missing 'query' in the request body"}, 400

    # TODO: should get it from .env
    url = 'https://indieneer-es-15d49606cdd6.herokuapp.com/search'
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return respond_success(response.json())
    else:
        return respond_error("Failed to fetch data from Elasticsearch", response.status_code)

