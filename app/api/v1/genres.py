from flask import Blueprint, request, current_app
from app.services import get_services
from lib.http_utils import respond_success, respond_error

genres_controller = Blueprint(
    'genres', __name__, url_prefix='/genres')


@genres_controller.route('/', methods=["GET"])
def get_genres():
    """
    Retrieve genres from the database.

    The function fetches genres from the database.

    :return: A list of genres or an error message.
    :rtype: Response
    """

    db = get_services(current_app).db.connection

    tags = []
    for tag in db["tags"].find({}):
        tag["_id"] = str(tag["_id"])
        tags.append(tag)

    if tags:
        return respond_success(tags, status_code=200)

    return respond_error("not found", 404)
