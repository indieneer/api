from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument
from validator import rules as R, validate

from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.products import ProductCreate
from app.services import get_services
from lib.http_utils import respond_error, respond_success


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


@products_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_products():
    db = get_services(current_app).db.connection

    data = (*db.products.aggregate([
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

    for d in data:
        d["_id"] = str(d["_id"])

    return respond_success(data)


@products_controller.route('/<string:product_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_by_id(product_id):
    try:
        db = get_services(current_app).db.connection

        data = (*db.products.aggregate([
            {
                '$match': {
                    '_id': ObjectId(product_id)
                }
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
        ]),)[0]

        data["_id"] = str(data["_id"])

        return respond_success(data)

    except IndexError as e:
        return respond_error(f'The product with ID {product_id} was not found.', 404)
    except Exception as e:
        return respond_error(f'Internal server error. {e}', 500)


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

        if any([x not in rules.keys() for x in fields]):
            return respond_error(f'Bad request.', 400)

        validation_result = validate(data, rules, return_info=True)
        if isinstance(validation_result, bool):
            if not validation_result:
                return respond_error(f'Bad request.', 400)
        else:
            _, data, errors = validation_result
            if errors:
                return respond_error(f'Bad request. {errors}', 400)

        products_model = get_models(current_app).products
        created_product = products_model.create(ProductCreate(**data))

        return respond_success(created_product.to_json())
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

        result = get_services(current_app).db.connection["products"].find_one_and_update(
            filter_criteria, {"$set": data}, return_document=ReturnDocument.AFTER)

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

        result = get_services(current_app).db.connection["products"].find_one_and_delete(
            filter_criteria)

        if result is None:
            return respond_error(f'The product with id {product_id} was not found.', 404)

        return respond_success([f'Successfully deleted the product with id {result["_id"]}.'])

    except Exception as e:
        return respond_error(str(e), 500)
