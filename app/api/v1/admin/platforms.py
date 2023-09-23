from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument
from slugify import slugify

from app.middlewares import requires_auth, requires_role
from app.services import get_services
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')

PLATFORM_FIELDS = [
    "slug",
    "name",
    "enabled",
    "icon_url",
    "url"
]


@platforms_controller.route('/', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_platforms():
    try:
        db = get_services(current_app).db.connection

        platforms = []
        for platform in db["platforms"].find():
            platform["_id"] = str(platform["_id"])
            platforms.append(platform)

        return respond_success(platforms, status_code=200)

    except Exception as e:
        return respond_error(str(e), 500)


@platforms_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_platform():
    try:
        db = get_services(current_app).db.connection
        platforms = db["platforms"]

        data = request.get_json()

        new_platform = {key: data.get(key) for key in PLATFORM_FIELDS}
        new_platform["slug"] = slugify(new_platform["name"])

        result = platforms.insert_one(new_platform)
        new_platform["_id"] = str(result.inserted_id)

        return respond_success(new_platform, None, 201)

    except Exception as e:
        return respond_error(str(e), 500)


@platforms_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_platform(profile_id):
    try:
        data = request.get_json()

        if len(data) == 0:
            return respond_error(f'The request body is empty.', 422)

        for key in data:
            if key not in PLATFORM_FIELDS:
                return respond_error(f'The key "{key}" is not allowed.', 422)

        filter_criteria = {"_id": ObjectId(profile_id)}
        result = get_services(current_app).db.connection["platforms"].find_one_and_update(filter_criteria, {"$set": data},
                                                                                          return_document=ReturnDocument.AFTER)
        if result is None:
            return respond_error(f'The platform with id {profile_id} was not found.', 404)

        result["_id"] = str(result["_id"])

        return respond_success(result)

    except Exception as e:
        return respond_error(str(e), 500)


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_platform(platform_id):
    try:
        db = get_services(current_app).db.connection
        platforms = db["platforms"]

        if platforms.delete_one({"_id": ObjectId(platform_id)}).deleted_count == 0:
            return respond_error("not found", 404)

        return respond_success(f"platform id {platform_id} successfully deleted")

    except Exception as e:
        return respond_error(str(e), 500)
