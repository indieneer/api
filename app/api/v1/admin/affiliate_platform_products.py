from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.affiliate_platform_products import AffiliatePlatformProductPatch, AffiliatePlatformProductCreate
from lib.http_utils import respond_success, respond_error

affiliate_platform_products_controller = Blueprint('affiliate_platform_products', __name__, url_prefix='/affiliate_platform_products')


@affiliate_platform_products_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliate_platform_products():
    """
    Retrieve all affiliate platform products.

    This endpoint returns a list of all affiliate platform products from the database.
    Requires authentication and admin privileges.
    """
    affiliate_platform_products_model = get_models(current_app).affiliate_platform_products
    affiliate_platform_products_list = affiliate_platform_products_model.get_all()
    return respond_success([affiliate_platform_product.to_json() for affiliate_platform_product in affiliate_platform_products_list])


@affiliate_platform_products_controller.route('/<string:affiliate_platform_product_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliate_platform_product_by_id(affiliate_platform_product_id):
    """
    Retrieve a single affiliate platform product by ID.

    This endpoint returns the details of a specific affiliate platform product.
    Requires authentication and admin privileges.
    """
    affiliate_platform_products_model = get_models(current_app).affiliate_platform_products
    affiliate_platform_product = affiliate_platform_products_model.get(affiliate_platform_product_id)
    if affiliate_platform_product:
        return respond_success(affiliate_platform_product.to_json())
    else:
        return respond_error(f'Affiliate platform product with ID {affiliate_platform_product_id} not found', 404)


@affiliate_platform_products_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_affiliate_platform_product():
    """
    Create a new affiliate platform product.

    This endpoint creates a new affiliate platform product with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    affiliate_platform_products_model = get_models(current_app).affiliate_platform_products
    try:
        affiliate_platform_product_data = AffiliatePlatformProductCreate(**data)
        new_affiliate_platform_product = affiliate_platform_products_model.create(affiliate_platform_product_data)
        return respond_success(new_affiliate_platform_product.to_json(), status_code=201)
    except TypeError as e:
        print(e)
        raise UnprocessableEntityException("Invalid data provided.")


@affiliate_platform_products_controller.route('/<string:affiliate_platform_product_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_affiliate_platform_product(affiliate_platform_product_id):
    """
    Update an existing affiliate platform product.

    This endpoint updates an affiliate platform product's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    affiliate_platform_product_patch_data = AffiliatePlatformProductPatch(**data)
    affiliate_platform_products_model = get_models(current_app).affiliate_platform_products
    updated_affiliate_platform_product = affiliate_platform_products_model.patch(affiliate_platform_product_id, affiliate_platform_product_patch_data)

    if updated_affiliate_platform_product:
        return respond_success(updated_affiliate_platform_product.to_json())
    else:
        return respond_error(f'Affiliate platform product with ID {affiliate_platform_product_id} not found', 404)


@affiliate_platform_products_controller.route('/<string:affiliate_platform_product_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_affiliate_platform_product(affiliate_platform_product_id):
    """
    Delete an affiliate platform product by ID.

    This endpoint removes an affiliate platform product from the database.
    Requires authentication and admin privileges.
    """
    affiliate_platform_products_model = get_models(current_app).affiliate_platform_products
    deleted_affiliate_platform_product = affiliate_platform_products_model.delete(affiliate_platform_product_id)
    if deleted_affiliate_platform_product:
        return respond_success({'message': f'Affiliate platform product {affiliate_platform_product_id} successfully deleted'})
    else:
        return respond_error(f'Affiliate platform product with ID {affiliate_platform_product_id} not found', 404)
