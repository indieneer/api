from flask import Blueprint, current_app

from app.models.products import Product
from lib.http_utils import respond_success

from app.models import get_models, exceptions as models_exceptions

products_controller = Blueprint('products', __name__, url_prefix='/products')


@products_controller.route('/<string:product_slug>', methods=["GET"])
def get_product_by_slug(product_slug: str):
    """
    Retrieve a product by its slug.

    This endpoint is used for fetching a product based on its unique slug.
    A slug is a human-readable, URL-friendly unique identifier for a product.

    :param str product_slug: The slug of the product to retrieve.
    :return: The requested product in JSON format.
    :raises NotFoundException: If the product with the given slug does not exist.
    :rtype: dict
    """

    product_model = get_models(current_app).products
    product = product_model.get_by_slug(product_slug)

    if product is None:
        raise models_exceptions.NotFoundException(Product.__name__)

    return respond_success(product.to_json())

