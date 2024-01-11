from flask import Blueprint, request, current_app

from app.models import get_models
from app.services import get_services
from lib import db_utils
from lib.http_utils import respond_success, respond_error

tags_controller = Blueprint(
    'tags', __name__, url_prefix='/tags')


@tags_controller.route('/', methods=["GET"])
def get_tags():
    """
    Retrieve tags from the database.

    The function fetches tags from the database.

    :return: A list of tags or an error message.
    :rtype: Response
    """
    tags = get_models(current_app).tags.get_all()

    return respond_success(db_utils.to_json(tags))
