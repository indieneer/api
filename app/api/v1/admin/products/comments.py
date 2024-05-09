from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.comments import CommentPatch, CommentCreate
from lib.http_utils import respond_success, respond_error
from .router import products_controller


@products_controller.route('/<string:product_id>/comments', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_comments(product_id):
    """
    Retrieve all comments.

    This endpoint returns a list of all comments from the database.
    Requires authentication and admin privileges.
    """
    comments_model = get_models(current_app).comments
    comments_list = comments_model.get_all(product_id)
    return respond_success([comment.to_json() for comment in comments_list])


@products_controller.route('/<string:product_id>/comments/<string:comment_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_comment_by_id(product_id, comment_id):
    """
    Retrieve a single comment by ID.

    This endpoint returns the details of a specific comment.
    Requires authentication and admin privileges.
    """
    comments_model = get_models(current_app).comments
    comment = comments_model.get(product_id, comment_id)
    if comment:
        return respond_success(comment.to_json())
    else:
        return respond_error(f'Comment with ID {comment_id} not found', 404)


@products_controller.route('/<string:product_id>/comments', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_comment(product_id):
    """
    Create a new comment.

    This endpoint creates a new comment with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    comments_model = get_models(current_app).comments
    try:
        comment_data = CommentCreate(**data)
        new_comment = comments_model.create(product_id, comment_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_comment.to_json(), status_code=201)


@products_controller.route('/<string:product_id>/comments/<string:comment_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_comment(product_id, comment_id):
    """
    Update an existing comment.

    This endpoint updates a comment's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()
    comment_patch_data = CommentPatch(**data)
    comments_model = get_models(current_app).comments
    updated_comment = comments_model.patch(product_id, comment_id, comment_patch_data)

    if updated_comment:
        return respond_success(updated_comment.to_json())
    else:
        return respond_error(f'Comment with ID {comment_id} not found', 404)


@products_controller.route('/<string:product_id>/comments/<string:comment_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_comment(product_id, comment_id):
    """
    Delete a comment by ID.

    This endpoint removes a comment from the database.
    Requires authentication and admin privileges.
    """
    comments_model = get_models(current_app).comments
    deleted_comment = comments_model.delete(product_id, comment_id)
    if deleted_comment:
        return respond_success({'message': f'Comment {comment_id} successfully deleted'})
    else:
        return respond_error(f'Comment with ID {comment_id} not found', 404)
