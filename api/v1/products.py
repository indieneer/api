from bson import ObjectId
from flask import Blueprint

from tools.http_utils import respond_success, respond_error
from services.database import Database as dbs

products_controller = Blueprint('products', __name__, url_prefix='/products')


@products_controller.route('/', methods=["GET"])
def get_products():
    try:
        db = dbs.client.get_default_database()

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

    except Exception as e:
        return respond_error(f'Internal server error. {e}', 500)


@products_controller.route('/<string:product_id>', methods=["GET"])
def get_product_by_id(product_id):
    try:
        db = dbs.client.get_default_database()

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