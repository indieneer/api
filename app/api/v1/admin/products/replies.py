from flask import Blueprint, request, current_app

from app.api.exceptions import UnprocessableEntityException, BadRequestException
from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.models.product_replies import ProductReplyPatch, ProductReplyCreate
from lib.http_utils import respond_success, respond_error
from .router import comments_controller


@comments_controller.route('/<string:comment_id>/product_replies', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_replies(comment_id: str):
    """
    Retrieve all product replies.

    This endpoint returns a list of all product replies from the database.
    Requires authentication and admin privileges.
    """
    product_replies_model = get_models(current_app).product_replies
    product_replies_list = product_replies_model.get_all(comment_id)
    return respond_success([product_reply.to_json() for product_reply in product_replies_list])


# TODO: discuss removing comment_id from the URL
@comments_controller.route('/<string:comment_id>/product_replies/<string:reply_id>', methods=["GET"])
@requires_auth
@requires_role('admin')
def get_product_reply_by_id(comment_id: str, reply_id: str):
    """
    Retrieve a single product reply by ID.

    This endpoint returns the details of a specific product reply.
    Requires authentication and admin privileges.
    """
    product_comments_model = get_models(current_app).product_comments
    product_comment = product_comments_model.get(comment_id)

    if not product_comment:
        return respond_error(f'The reply is attached to a nonexistent comment with ID {comment_id}', 404)

    product_replies_model = get_models(current_app).product_replies
    product_reply = product_replies_model.get(reply_id)
    if product_reply:
        return respond_success(product_reply.to_json())
    else:
        return respond_error(f'Product reply with ID {reply_id} not found', 404)


@comments_controller.route('/<string:comment_id>/product_replies', methods=["POST"])
@requires_auth
@requires_role('admin')
def create_product_reply(comment_id: str):
    """
    Create a new product reply.

    This endpoint creates a new product reply with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()

    if len(data["text"]) <= 0:
        return respond_error("`text` can't be empty", 400)

    product_replies_model = get_models(current_app).product_replies
    try:
        product_reply_data = ProductReplyCreate(comment_id=comment_id, **data)
        new_product_reply = product_replies_model.create(product_reply_data)
    except TypeError:
        raise UnprocessableEntityException("Invalid data provided.")
    return respond_success(new_product_reply.to_json(), status_code=201)


@comments_controller.route('/<string:comment_id>/product_replies/<string:reply_id>', methods=["PATCH"])
@requires_auth
@requires_role('admin')
def update_product_reply(comment_id: str, reply_id: str):
    """
    Update an existing product reply.

    This endpoint updates a product reply's details with the provided data.
    Requires authentication and admin privileges.
    """
    data = request.get_json()

    if len(data["text"]) <= 0:
        return respond_error("`text` can't be empty", 400)

    product_reply_patch_data = ProductReplyPatch(**data)
    product_replies_model = get_models(current_app).product_replies
    updated_product_reply = product_replies_model.patch(reply_id, product_reply_patch_data)

    if updated_product_reply:
        return respond_success(updated_product_reply.to_json())
    else:
        return respond_error(f'Product reply with ID {reply_id} not found', 404)


@comments_controller.route('/<string:comment_id>/product_replies/<string:reply_id>', methods=["DELETE"])
@requires_auth
@requires_role('admin')
def delete_product_reply(comment_id: str, reply_id: str):
    """
    Delete a product reply by ID.

    This endpoint removes a product reply from the database.
    Requires authentication and admin privileges.
    """
    product_replies_model = get_models(current_app).product_replies
    deleted_product_reply = product_replies_model.delete(reply_id)
    if deleted_product_reply:
        return respond_success({'message': f'Product reply {reply_id} successfully deleted'})
    else:
        return respond_error(f'Product reply with ID {reply_id} not found', 404)
