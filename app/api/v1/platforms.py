from flask import Blueprint, request, current_app
from app.services import get_services
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')


@platforms_controller.route('/', methods=["GET"])
def get_platforms():
    """
    Retrieve platforms from the database.

    The function fetches platforms that are enabled from the database.
    If the 'enabled' parameter is not provided or is not 'true',
    it returns a "not found" error.

    :return: A list of enabled platforms or an error message.
    :rtype: Response
    """

    db = get_services(current_app).db.connection

    if request.args.get('enabled') == 'true':
        platforms = [
            {**platform, "_id": str(platform["_id"])}
            for platform in db["platforms"].find({'enabled': True})
        ]

        return respond_success(platforms)

    return respond_error("not found", 404)
