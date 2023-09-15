from bson import ObjectId
from flask import Blueprint, request
from pymongo import ReturnDocument
from validator import rules as R, validate

from middlewares import requires_auth, requires_role
from tools.http_utils import respond_error, respond_success

from services.database import Database as dbs

products_controller = Blueprint('products', __name__, url_prefix='/products')

PRODUCT_FIELDS = [
    "type",
    "name",
    "required_age",
    "detailed_description",
    "short_description",
    "supported_languages",
    "developers",
    "publishers",
    "platforms",
    "genres",
    "release_date",
    "media",
    "requirements"
]


@products_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_product():
    try:
        data = request.get_json()

        fields = data.keys()

        # validation rules for the request body
        rules = {
            "type": R.Required(),
            "name": R.Required(),
            "required_age": R.Required(),
            "detailed_description": R.Required(),
            "short_description": R.Required(),
            "supported_languages": R.Required(),
            "developers": [R.Required(), R.List()],
            "publishers": [R.Required(), R.List()],
            "platforms": R.Required(),
            "genres": R.Required(),
            "release_date": R.Required(),
            "media": R.Dict(),
            "requirements": R.Dict()
        }

        validation_result, data, errors = validate(data, rules, return_info=True)

        if any([x not in rules.keys() for x in fields]):
            validation_result = False

        if not validation_result:
            return respond_error(f'Bad request.', 400)

        db = dbs.client.get_default_database()

        db.products.insert_one(data)

        data["_id"] = str(data["_id"])

        return respond_success(data)
    except Exception as e:
        return respond_error(f'Internal server error. {e}', 500)


@products_controller.route('/<string:product_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_product(product_id):
    try:
        data = request.get_json()

        for key in data:
            if key not in PRODUCT_FIELDS:
                return respond_error(f'The key "{key}" is not allowed.', 422)

        filter_criteria = {"_id": ObjectId(product_id)}

        result = dbs.client.indieneer.products.find_one_and_update(filter_criteria, {"$set": data}, return_document=ReturnDocument.AFTER)

        if result is None:
            return respond_error(f'The product with id {product_id} was not found.', 404)

        result["_id"] = str(result["_id"])

        return respond_success(result)

    except Exception as e:
        return respond_error(f'Internal server error. {e}', 500)


@products_controller.route('/<string:product_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_product(product_id):
    try:
        filter_criteria = {"_id": ObjectId(product_id)}

        result = dbs.client.indieneer.products.find_one_and_delete(filter_criteria)

        if result is None:
            return respond_error(f'The product with id {product_id} was not found.', 404)

        return respond_success([f'Successfully deleted the product with id {result["_id"]}.'])

    except Exception as e:
        return respond_error(str(e), 500)