from flask import Blueprint, request
from services.database import Database as dbs
from tools.http_utils import respond_success, respond_not_found

platforms_controller = Blueprint('platforms', __name__, url_prefix='/platforms')


@platforms_controller.route('/', methods=["GET"])
def get_platforms():
    db = dbs.client.get_database("indieneer")

    if request.args.get('enabled') == 'true':
        platforms = []
        for p in db["platforms"].find({'enabled': True}):
            platform = p
            platform["_id"] = str(platform["_id"])
            platforms.append(platform)

        return respond_success(platforms, status_code=200)

    return respond_not_found("not found", 404)
