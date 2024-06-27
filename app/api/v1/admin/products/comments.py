from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.product_comments import ProductCommentPatch, ProductCommentCreate
from lib.http_utils import respond_success, respond_error
from lib.db_utils import to_json
from .router import products_controller


from flask import request


@products_controller.route('/<string:product_id>/comments', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_all_product_comments(product_id: str):
    """
    Retrieve all product comments for a specific product.

    This endpoint returns all product comments associated with a specific product ID.
    Requires authentication and admin privileges.

    Query Parameters:
    - limit: int (optional, default=15) - The maximum number of comments to return.
    - newest_first: bool (optional, default=True) - Determines the order of the comments.
    """
    limit = request.args.get('limit', 15, type=int)
    newest_first = request.args.get('newest_first', 'true').lower() == 'true'

    product_comments_model = get_models(current_app).product_comments
    all_product_comments = product_comments_model.get_all(product_id, limit=limit, newest_first=newest_first)
    return respond_success(to_json(all_product_comments))


@products_controller.route('/product_comments/<string:comment_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_comment_by_id(comment_id: str):
    """
    Retrieve a single product comment by ID.

    This endpoint returns the details of a specific product comment.
    Requires authentication and admin privileges.
    """
    product_comments_model = get_models(current_app).product_comments
    product_comment = product_comments_model.get(comment_id)
    if product_comment:
        return respond_success(product_comment.to_json())
    else:
        return respond_error(f'Product comment with ID {comment_id} not found', 404)


@products_controller.route('/product_comments', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_product_comment():
    """
    Create a new product comment.

    This endpoint creates a new product comment with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    product_comments_model = get_models(current_app).product_comments
    try:
        product_comment_data = ProductCommentCreate(**data)
        new_product_comment = product_comments_model.create(product_comment_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_product_comment.to_json(), status_code=201)


@products_controller.route('/product_comments/<string:comment_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_product_comment(comment_id: str):
    """
    Update an existing product comment.

    This endpoint updates a product comment's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    product_comment_patch_data = ProductCommentPatch(**data)
    product_comments_model = get_models(current_app).product_comments
    updated_product_comment = product_comments_model.patch(comment_id, product_comment_patch_data)

    if updated_product_comment:
        return respond_success(updated_product_comment.to_json())
    else:
        return respond_error(f'Product comment with ID {comment_id} not found', 404)


@products_controller.route('/product_comments/<string:comment_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_product_comment(comment_id: str):
    """
    Delete a product comment by ID.

    This endpoint removes a product comment from the database.
    Requires authentication and admin privileges.
    """
    product_comments_model = get_models(current_app).product_comments
    deleted_product_comment = product_comments_model.delete(comment_id)
    if deleted_product_comment:
        return respond_success({'message': f'Product comment {comment_id} successfully deleted'})
    else:
        return respond_error(f'Product comment with ID {comment_id} not found', 404)
