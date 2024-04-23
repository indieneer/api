from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.platform_products import PlatformProductPatch, PlatformProductCreate
from lib.http_utils import respond_success, respond_error

platform_products_controller = Blueprint('platform_products', __name__, url_prefix='/platform_products')


@platform_products_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_platform_products():
    """
    Retrieve all platform products.

    This endpoint returns a list of all platform products from the database.
    Requires authentication and admin privileges.
    """
    platform_products_model = get_models(current_app).platform_products
    platform_products_list = platform_products_model.get_all()
    return respond_success([platform_product.to_json() for platform_product in platform_products_list])


@platform_products_controller.route('/<string:platform_product_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_platform_product_by_id(platform_product_id):
    """
    Retrieve a single platform product by ID.

    This endpoint returns the details of a specific platform product.
    Requires authentication and admin privileges.
    """
    platform_products_model = get_models(current_app).platform_products
    platform_product = platform_products_model.get(platform_product_id)
    if platform_product:
        return respond_success(platform_product.to_json())
    else:
        return respond_error(f'Platform product with ID {platform_product_id} not found', 404)


@platform_products_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_platform_product():
    """
    Create a new platform product.

    This endpoint creates a new platform product with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    platform_products_model = get_models(current_app).platform_products
    try:
        platform_product_data = PlatformProductCreate(**data)
        new_platform_product = platform_products_model.create(platform_product_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_platform_product.to_json(), status_code=201)


@platform_products_controller.route('/<string:platform_product_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_platform_product(platform_product_id):
    """
    Update an existing platform product.

    This endpoint updates a platform product's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    platform_product_patch_data = PlatformProductPatch(**data)
    platform_products_model = get_models(current_app).platform_products
    updated_platform_product = platform_products_model.patch(platform_product_id, platform_product_patch_data)

    if updated_platform_product:
        return respond_success(updated_platform_product.to_json())
    else:
        return respond_error(f'Platform product with ID {platform_product_id} not found', 404)


@platform_products_controller.route('/<string:platform_product_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_platform_product(platform_product_id):
    """
    Delete a platform product by ID.

    This endpoint removes a platform product from the database.
    Requires authentication and admin privileges.
    """
    platform_products_model = get_models(current_app).platform_products
    deleted_platform_product = platform_products_model.delete(platform_product_id)
    if deleted_platform_product:
        return respond_success({'message': f'Platform product {platform_product_id} successfully deleted'})
    else:
        return respond_error(f'Platform product with ID {platform_product_id} not found', 404)

