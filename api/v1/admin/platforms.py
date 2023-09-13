from bson import ObjectId
from flask import Blueprint, request
from pymongo.errors import ServerSelectionTimeoutError

from middlewares import requires_auth
from services.database import Database as dbs
from slugify import slugify
from tools.http_utils import respond_success, respond_error, respond_not_found

platforms_controller = Blueprint('platforms', __name__, url_prefix='/platforms')

PLATFORM_FIELDS = [
    "slug",
    "name",
    "enabled",
    "icon_url",
    "url"
]


@platforms_controller.route('/', methods=["GET"])
@requires_auth
def get_platforms():
    db = dbs.client.get_database("indieneer")

    platforms = []
    for p in db["platforms"].find():
        platform = p
        platform["_id"] = str(platform["_id"])
        platforms.append(platform)

    return respond_success(platforms, status_code=200)


@platforms_controller.route('/', methods=["POST"])
@requires_auth
def create_platform():
    db = dbs.client.get_database("indieneer")
    platforms = db["platforms"]

    data = request.get_json()

    new_platform = {key: data.get(key) for key in PLATFORM_FIELDS}
    new_platform["slug"] = slugify(new_platform["name"])

    try:
        result = platforms.insert_one(new_platform)
    except ServerSelectionTimeoutError as e:
        return respond_error(str(e), 500)

    new_platform["_id"] = str(result.inserted_id)

    return respond_success(new_platform, None, 201)


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
def delete_platform(platform_id):
    try:
        db = dbs.client.get_database("indieneer")
        platforms = db["platforms"]

        if platforms.delete_one({"_id": ObjectId(platform_id)}).deleted_count == 0:
            return respond_not_found("platform not found", 404)

        return respond_success(f"platform id {platform_id} successfully deleted")

    except Exception as e:
        return respond_error(str(e), 500)
