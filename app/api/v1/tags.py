from flask import Blueprint, current_app

from app.models import get_models
from lib import db_utils
from lib.http_utils import respond_success

tags_controller = Blueprint(
    'tags', __name__, url_prefix='/tags')


@tags_controller.route('/', methods=["GET"])
def get_tags():
    """
    Retrieve all tags.

    It retrieves all tags from the database.

    :return: A success response with the list of all tags.
    :rtype: dict
    """
    tags = get_models(current_app).tags.get_all()

    return respond_success(db_utils.to_json(tags))