from flask import Blueprint, current_app

from app.models import get_models
from lib.http_utils import respond_success

tags_controller = Blueprint(
    'tags', __name__, url_prefix='/tags')


@tags_controller.route('/', methods=["GET"])
def get_tags():
    """
    Retrieve all tags.

    This endpoint requires authentication and is accessible only to users with an 'admin' role.
    It retrieves all tags from the database.

    :return: A success response with the list of all tags.
    :rtype: dict
    """
    tags_model = get_models(current_app).tags
    tags = [tag.as_json() for tag in tags_model.get_all()]

    return respond_success(tags)
