from flask import Blueprint, request, current_app

from app.models import get_models
from app.services import get_services
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')


@platforms_controller.route('/', methods=["GET"])
def get_platforms():
    """
    Retrieve platforms from the database.

    The function fetches platforms that are enabled from the database.

    :return: A list of enabled platforms or an error message.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms
    all_platforms = platforms_model.get_all()

    return respond_success(all_platforms)
