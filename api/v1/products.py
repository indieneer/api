from flask import Blueprint

from tools.http_utils import respond_success, respond_error

products_controller = Blueprint('products', __name__, url_prefix='/products')

@products_controller.route('/', methods=["GET"])
def get_products():
    fetched = [
        {
            "_id": "jsfdjksdfjksdf",
            "name": "Fortnite",
        },

        {
            "_id": "fsdjsjfdsdf",
            "name": "Mainokrafto",
        }
    ]

    return respond_success(fetched)
    # TODO: implement real functionality


@products_controller.route('/<string:product_id>', methods=["GET"])
def get_product_by_id(product_id):
    try:
        return respond_success([])
    except Exception as e:
        return respond_error(str(e), 500)