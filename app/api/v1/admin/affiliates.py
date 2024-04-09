from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.affiliates import AffiliatePatch, AffiliateCreate
from lib.http_utils import respond_success, respond_error

affiliates_controller = Blueprint('affiliates', __name__, url_prefix='/affiliates')


@affiliates_controller.route('/', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliates():
    """
    Retrieve all affiliates.

    This endpoint returns a list of all affiliates from the database.
    Requires authentication and admin privileges.
    """
    affiliates_model = get_models(current_app).affiliates
    affiliates_list = affiliates_model.get_all()
    return respond_success([affiliate.to_json() for affiliate in affiliates_list])


@affiliates_controller.route('/<string:affiliate_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_affiliate_by_id(affiliate_id):
    """
    Retrieve a single affiliate by ID.

    This endpoint returns the details of a specific affiliate.
    Requires authentication and admin privileges.
    """
    affiliates_model = get_models(current_app).affiliates
    affiliate = affiliates_model.get(affiliate_id)
    if affiliate:
        return respond_success(affiliate.to_json())
    else:
        return respond_error(f'Affiliate with ID {affiliate_id} not found', 404)


@affiliates_controller.route('/', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_affiliate():
    """
    Create a new affiliate.

    This endpoint creates a new affiliate with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    affiliates_model = get_models(current_app).affiliates
    try:
        affiliate_data = AffiliateCreate(**data)
        new_affiliate = affiliates_model.create(affiliate_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_affiliate.to_json(), status_code=201)


@affiliates_controller.route('/<string:affiliate_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_affiliate(affiliate_id):
    """
    Update an existing affiliate.

    This endpoint updates an affiliate's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    affiliate_patch_data = AffiliatePatch(**data)
    affiliates_model = get_models(current_app).affiliates
    updated_affiliate = affiliates_model.patch(affiliate_id, affiliate_patch_data)

    if updated_affiliate:
        return respond_success(updated_affiliate.to_json())
    else:
        return respond_error(f'Affiliate with ID {affiliate_id} not found', 404)


@affiliates_controller.route('/<string:affiliate_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_affiliate(affiliate_id):
    """
    Delete an affiliate by ID.

    This endpoint removes an affiliate from the database.
    Requires authentication and admin privileges.
    """
    affiliates_model = get_models(current_app).affiliates
    deleted_affiliate = affiliates_model.delete(affiliate_id)
    if deleted_affiliate:
        return respond_success({'message': f'Affiliate {affiliate_id} successfully deleted'})
    else:
        return respond_error(f'Affiliate with ID {affiliate_id} not found', 404)
