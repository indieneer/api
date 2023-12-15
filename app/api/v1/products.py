from flask import Blueprint, current_app

from app.models.products import Product
from lib.http_utils import respond_success

from app.models import get_models, exceptions as models_exceptions

products_controller = Blueprint('products', __name__, url_prefix='/products')


@products_controller.route('/<string:product_id>', methods=["GET"])
def get_product(product_id: str):
    """
    Retrieve a product by its ID.

    :param str product_id: The ID of the product to retrieve.
    :return: The requested product in JSON format.
    :raises NotFoundException: If the product with the given ID does not exist.
    :rtype: dict
    """

    product_model = get_models(current_app).products
    product = product_model.get(product_id)

    if product is None:
        raise models_exceptions.NotFoundException(Product.__name__)

    return respond_success(product.as_json())


@products_controller.route('/', methods=["GET"])
def get_products():
    """
    Retrieve all products.

    This endpoint is responsible for fetching all products available in the system.
    Each product is represented in a JSON format.

    :return: A success response containing a list of products.
    :rtype: Response
    """

    products_model = get_models(current_app).products
    products = [product.as_json() for product in products_model.get_all()]

    return respond_success(products)


@products_controller.route('/slug/<string:product_slug>', methods=["GET"])
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

    return respond_success(product.as_json())

