from bson import ObjectId
from flask import Blueprint, request

from middlewares import requires_auth
from services.database import Database as dbs
from slugify import slugify
from tools.http_utils import respond_success, respond_error

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
    try:
        db = dbs.client.get_default_database()

        platforms = []
        for platform in db["platforms"].find():
            platform["_id"] = str(platform["_id"])
            platforms.append(platform)

        return respond_success(platforms, status_code=200)

    except Exception as e:
        return respond_error(str(e), 500)


@platforms_controller.route('/', methods=["POST"])
@requires_auth
def create_platform():
    try:
        db = dbs.client.get_default_database()
        platforms = db["platforms"]

        data = request.get_json()

        new_platform = {key: data.get(key) for key in PLATFORM_FIELDS}
        new_platform["slug"] = slugify(new_platform["name"])

        result = platforms.insert_one(new_platform)
        new_platform["_id"] = str(result.inserted_id)

        return respond_success(new_platform, None, 201)

    except Exception as e:
        return respond_error(str(e), 500)


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
def delete_platform(platform_id):
    try:
        db = dbs.client.get_default_database()
        platforms = db["platforms"]

        if platforms.delete_one({"_id": ObjectId(platform_id)}).deleted_count == 0:
            return respond_error("not found", 404)

        return respond_success(f"platform id {platform_id} successfully deleted")

    except Exception as e:
        return respond_error(str(e), 500)
