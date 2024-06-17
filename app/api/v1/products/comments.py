from flask import Blueprint, request, g, current_app

from app.middlewares import requires_auth
from config import app_config
from lib.http_utils import respond_error, respond_success
from lib.db_utils import to_json

from app.models import get_models, exceptions as models_exceptions
from app.models.product_comments import ProductComment, ProductCommentCreate, ProductCommentPatch
from .router import products_controller


from flask import request


@products_controller.route('/<string:product_id>/comments', methods=["GET"])
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
    newest_first = request.args.get('newest_first', True, type=bool)

    product_comments_model = get_models(current_app).product_comments
    all_product_comments = product_comments_model.get_all(product_id, limit=limit, newest_first=newest_first)
    return respond_success(to_json(all_product_comments))


@products_controller.route('/<string:product_id>/comments', methods=["POST"])
@requires_auth
def create_product_comment(product_id: str):
    """
    Create a new product comment.

    This endpoint is responsible for creating a new product comment.
    It expects a JSON payload containing the necessary product comment information.

    :return: The created product comment in JSON format along with a status code indicating successful creation.
    :rtype: dict
    :status 201: Product comment created successfully.
    """
    data = request.get_json()
    product_comment_model = get_models(current_app).product_comments

    # Validate nonempty fields
    if data is None or not all(key in data and len(data[key]) > 0 for key in ['text']):
        return respond_error("Bad Request.", 400)

    # Validate text length < 8000
    if len(data.get("text")) > 8000:
        return respond_error("Text too long.", 400)

    product_comment_data = ProductCommentCreate(
        text=data.get("text"),
        product_id=product_id,
        profile_id=g.get("payload").get(f'{app_config["FB_NAMESPACE"]}/profile_id')
    )

    product_comment = product_comment_model.create(product_comment_data)

    return respond_success(product_comment.to_json(), None, 201)


@products_controller.route('/<string:product_id>/comments/<string:comment_id>', methods=["PATCH"])
@requires_auth
def update_product_comment(product_id: str, comment_id: str):
    """
    Update an existing product comment.

    This endpoint updates the content of an existing product comment based on the provided product comment ID.

    :param str comment_id: The unique identifier of the product comment to be updated.
    :raises NotFoundException: If the product comment with the given ID does not exist.
    :return: The updated product comment in JSON format.
    :rtype: dict
    """
    data = request.get_json()
    product_comment_model = get_models(current_app).product_comments

    # Validate nonempty fields
    if data is None or not all(key in data and len(data[key]) > 0 for key in ['text']):
        return respond_error("Bad Request.", 400)

    # Validate text length shouldn't exceed 8000 characters
    if len(data.get("text")) > 8000:
        return respond_error("Text too long.", 400)

    product_comment = product_comment_model.get(comment_id)

    invoker_id = g.get("payload").get(f'{app_config["FB_NAMESPACE"]}/profile_id')

    if invoker_id != str(product_comment.profile_id):  # Converted to string because profile_id is ObjectId
        raise models_exceptions.ForbiddenException

    if product_comment is None:
        raise models_exceptions.NotFoundException(ProductComment.__name__)

    patch_data = ProductCommentPatch()
    if 'text' in data:
        patch_data = ProductCommentPatch(text=data["text"])

    updated_product_comment = product_comment_model.patch(comment_id, patch_data)

    return respond_success(updated_product_comment.to_json())


@products_controller.route('/<string:product_id>/comments/<string:comment_id>', methods=["DELETE"])
@requires_auth
def delete_product_comment(product_id: str, comment_id: str):
    """
    Delete a product comment.

    This endpoint deletes a product comment based on the provided product comment ID.

    :param str product_comment_id: The unique identifier of the product comment to be deleted.
    :raises NotFoundException: If the product comment with the given ID does not exist.
    :return: A success response with acknowledgment if the product comment is deleted successfully.
    :rtype: dict
    """
    product_comment_model = get_models(current_app).product_comments

    product_comment = product_comment_model.get(comment_id)

    invoker_id = g.get("payload").get(f'{app_config["FB_NAMESPACE"]}/profile_id')

    if invoker_id != str(product_comment.profile_id):  # Converted to string because profile_id is ObjectId
        raise models_exceptions.ForbiddenException

    product_comment = product_comment_model.delete(comment_id)

    if product_comment is None:
        raise models_exceptions.NotFoundException(ProductComment.__name__)

    return respond_success(product_comment.to_json())
