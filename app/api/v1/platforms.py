from flask import Blueprint, request, current_app
from app.services import get_services
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')


@platforms_controller.route('/', methods=["GET"])
def get_platforms():
    try:
        db = get_services(current_app).db.connection

        if request.args.get('enabled') == 'true':
            platforms = []
            for platform in db["platforms"].find({'enabled': True}):
                platform["_id"] = str(platform["_id"])
                platforms.append(platform)

            return respond_success(platforms, status_code=200)

        return respond_error("not found", 404)

    except Exception as e:
        return respond_error(str(e), 500)
