from bson import ObjectId
from flask import Blueprint, request, current_app
from pymongo import ReturnDocument
from slugify import slugify

from app.middlewares import requires_auth, requires_role
from app.services import get_services
from app.models import exceptions as models_exceptions
from app.api import exceptions as handlers_exceptions
from app.models.platforms import Platform
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
    """
    Retrieve all game store platforms.

    This endpoint retrieves all records of game stores from the database.
    It requires authentication and admin role permission to access.

    :return: A list of dictionaries each containing the details of a gaming platform.
    :rtype: list[dict]
    """

    db_connection = get_services(current_app).db.connection
    platforms_collection = db_connection["platforms"].find()

    platforms = [
        {**platform, "_id": str(platform["_id"])}
        for platform in platforms_collection
    ]

    return respond_success(platforms)


@platforms_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_platform():
    """
    Create a new game store platform.

    This endpoint requires admin authorization and is used to add a new game store
    to the database.

    :return: A dictionary containing the data of the newly created platform.
    :rtype: dict
    """

    db = get_services(current_app).db.connection
    platforms = db["platforms"]

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in PLATFORM_FIELDS):
        raise handlers_exceptions.BadRequestException("Invalid data provided.")

    new_platform = {key: data[key] for key in PLATFORM_FIELDS}
    new_platform["slug"] = slugify(new_platform["name"])

    result = platforms.insert_one(new_platform)
    new_platform["_id"] = str(result.inserted_id)

    return respond_success(new_platform, None, 201)


@platforms_controller.route('/<string:profile_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_platform(profile_id: str):
    """
    Update a platform by its ID.

    This function requires admin privileges. The provided profile_id is used to update the specific platform's
    data in the database with the new data provided in the request's JSON body.

    :param str profile_id: The ID of the platform to be updated.
    :raises NotFoundException: If the platform was not found.
    :raises UnprocessableEntityException: If the request has alien keys.
    :return: A JSON response containing either the updated platform data or an error message.
    :rtype: Response
    """

    data = request.get_json()

    if not data:
        raise handlers_exceptions.InternalServerErrorException("Internal server error.")

    for key in data:
        if key not in PLATFORM_FIELDS:
            raise handlers_exceptions.UnprocessableEntityException(f'The key "{key}" is not allowed.')

    filter_criteria = {"_id": ObjectId(profile_id)}
    result = get_services(current_app).db.connection["platforms"].find_one_and_update(
        filter_criteria, {"$set": data}, return_document=ReturnDocument.AFTER
    )

    if result is None:
        raise models_exceptions.NotFoundException(Platform.__name__)

    result["_id"] = str(result["_id"])

    return respond_success(result)


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_platform(platform_id: str):
    """
    Delete a gaming platform by its ID.

    This endpoint allows admin users to delete a game store platform from the database.

    :param str platform_id: The ID of the game store platform to be deleted.
    :raises NotFoundException: If the platform was not found.
    :return: A success message if the deletion is successful, or an error message if the platform is not found.
    :rtype: dict
    """

    db = get_services(current_app).db.connection
    platforms = db["platforms"]

    if platforms.delete_one({"_id": ObjectId(platform_id)}).deleted_count == 0:
        raise models_exceptions.NotFoundException(Platform.__name__)

    return respond_success({"message": f"Platform id {platform_id} successfully deleted"})
