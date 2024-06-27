import dataclasses

from flask import Blueprint, current_app, request

from app.api import exceptions
from app.middlewares import requires_auth, requires_role
from app.models import exceptions as models_exceptions
from app.models import get_models
from app.models.products import Product, ProductCreate, ProductPatch
from lib.db_utils import to_json
from lib.http_utils import respond_error, respond_success
from .router import products_controller


@products_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_products():
    product_model = get_models(current_app).products
    products = product_model.get_all()

    if products is None:
        raise models_exceptions.NotFoundException(Product.__name__)

    return respond_success(to_json(products))


@products_controller.route('/<string:product_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_by_id(product_id):
    product_model = get_models(current_app).products
    product = product_model.get(product_id)

    if product is None:
        raise models_exceptions.NotFoundException(Product.__name__)

    return respond_success(product.to_json())


@products_controller.route('/slug/<string:slug>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_by_slug(slug):
    product_model = get_models(current_app).products
    product = product_model.get_by_slug(slug)

    if product is None:
        raise models_exceptions.NotFoundException(Product.__name__)

    return respond_success(product.to_json())


@products_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_product():
    data = request.get_json()
    product_model = get_models(current_app).products
    product_create_fields = dataclasses.fields(ProductCreate)

    # convert categories and genres to tags

    if data is None or not all(field.name in data for field in product_create_fields):
        raise exceptions.BadRequestException("Not all required fields are present")

    try:
        created_product = product_model.create(ProductCreate(**data))

        return respond_success(created_product.to_json(), status_code=201)
    except TypeError:
        raise exceptions.BadRequestException("Bad request.")


@products_controller.route('/<string:product_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_product(product_id):
    data = request.get_json()
    product_model = get_models(current_app).products
    product_update_fields = [field.name for field in dataclasses.fields(ProductPatch)]

    # convert categories and genres to tags

    if data is None:
        raise exceptions.BadRequestException("The request body is empty.")
    for key in data:
        if key not in product_update_fields:
            return respond_error(f'The key "{key}" is not allowed.', 422)

    try:
        product = product_model.patch(product_id, ProductPatch(**data))
        if product is None:
            raise models_exceptions.NotFoundException(Product.__name__)

        return respond_success(product.to_json())
    except TypeError:
        raise exceptions.BadRequestException("Bad request.")


@products_controller.route('/<string:product_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_product(product_id):
    product_model = get_models(current_app).products
    result = product_model.delete(product_id)

    if result == 0:
        return respond_error(f'The product with id {product_id} was not found.', 404)

    return respond_success([f'Successfully deleted the product with id {product_id}.'])
