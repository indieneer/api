from flask import Blueprint, request, current_app

from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.api import exceptions as handlers_exceptions
from app.models.platforms import PlatformCreate, PlatformPatch
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')

PLATFORM_FIELDS = [
    "name",
    "enabled",
    "icon_url",
    "base_url"
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
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms
    platforms = [platform.as_json() for platform in platforms_model.get_all()]

    return respond_success(platforms)


@platforms_controller.route('/<string:platform_id>', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_platform_by_id(platform_id: str):
    """
    Retrieve a specific game store platform by its ID.

    This endpoint fetches details of a particular game store platform from the database, identified by the platform_id.
    It requires authentication and admin role permission to access.

    :param str platform_id: The unique identifier of the game store platform to be retrieved.
    :raises NotFoundException: If no platform is found with the given platform_id.
    :return: A dictionary containing the details of the requested game store platform.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms
    platform = platforms_model.get(platform_id)

    if not platform:
        return respond_error(f'The platform with ID {platform_id} was not found.', 404)

    return respond_success(platform.as_json())



@platforms_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_platform():
    """
    Create a new game store platform.

    This endpoint requires admin authorization and is used to add a new game store
    to the database.

    :return: A dictionary containing the data of the newly created platform.
    :rtype: Response
    """

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in PLATFORM_FIELDS):
        raise handlers_exceptions.BadRequestException("Invalid data provided.")

    new_platform = {key: data[key] for key in PLATFORM_FIELDS}

    platforms_model = get_models(current_app).platforms
    created_platform = platforms_model.create(PlatformCreate(**new_platform))

    return respond_success(created_platform.as_json(), None, 201)


@platforms_controller.route('/<string:platform_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_platform(platform_id: str):
    """
    Update a platform by its ID.

    This function requires admin privileges. The provided platform_id is used to update the specific platform's
    data in the database with the new data provided in the request's JSON body.

    :param str platform_id: The ID of the platform to be updated.
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

    platforms_model = get_models(current_app).platforms
    result = platforms_model.patch(platform_id, PlatformPatch(**data))

    return respond_success(result.as_json())


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_platform(platform_id: str):
    """
    Delete a gaming platform by its ID.

    This endpoint allows admin users to delete a game store platform from the database.

    :param str platform_id: The ID of the game store platform to be deleted.
    :return: A success message if the deletion is successful.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms
    deleted_platform = platforms_model.delete(platform_id)

    return respond_success({"message": f"Platform id {platform_id} successfully deleted", "deleted_platform": deleted_platform.as_json()})
