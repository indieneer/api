from flask import Blueprint, request, current_app

from app.middlewares import requires_auth, requires_role
from app.models import get_models
from app.api import exceptions as handlers_exceptions
from app.models.platforms import PlatformCreate, PlatformPatch
from lib import db_utils
from lib.http_utils import respond_success, respond_error

platforms_controller = Blueprint(
    'platforms', __name__, url_prefix='/platforms')

PLATFORM_FIELDS = [
    "name",
    "enabled",
    "icon_url",
    "base_url"
]

IGNORED_FIELDS = [
    "slug"
]


@platforms_controller.route('/', methods=["GET"])
@requires_auth
@requires_role("admin")
def get_platforms():
    """
    Retrieve all game store platforms.

    This endpoint retrieves all records of game store platforms from the database. It is accessible only to users with authentication and admin role permissions. The function gathers data from the platforms model and returns it in a structured format.

    :return: A list of dictionaries, each containing the details of a gaming platform.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms

    return respond_success(db_utils.to_json(platforms_model.get_all()))


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

    return respond_success(platform.to_json())


@platforms_controller.route('/', methods=["POST"])
@requires_auth
@requires_role("admin")
def create_platform():
    """
    Create a new game store platform.

    This endpoint is used to add a new game store platform to the database.
    It requires admin authorization and expects a JSON payload with necessary platform details.
    The endpoint validates the incoming data against predefined platform fields.

    :raises BadRequestException: If the provided data is invalid or incomplete.
    :return: A dictionary containing the details of the newly created game store platform along with the status code.
    :rtype: Response
    """

    data = request.get_json()

    # Validate incoming data
    if not data or not all(key in data for key in PLATFORM_FIELDS):
        raise handlers_exceptions.BadRequestException("Invalid data provided.")

    new_platform = {key: data[key] for key in PLATFORM_FIELDS}

    platforms_model = get_models(current_app).platforms
    created_platform = platforms_model.create(PlatformCreate(**new_platform))

    return respond_success(created_platform.to_json(), None, 201)


@platforms_controller.route('/<string:platform_id>', methods=["PATCH"])
@requires_auth
@requires_role("admin")
def update_platform(platform_id: str):
    """
    Update a game store platform by its ID.

    This endpoint allows admin users to modify an existing game store platform's details in the database.
    It requires a valid platform_id and a JSON payload containing the updated platform details.
    The function validates the incoming data, ensuring that only specified fields are updated and ignoring any alien keys.

    :param str platform_id: The unique identifier of the game store platform to be updated.
    :raises UnprocessableEntityException: If the provided data contains keys not allowed in PLATFORM_FIELDS.
    :return: A dictionary representing the updated details of the game store platform.
    :rtype: Response
    """

    data = request.get_json()

    if not data:
        raise handlers_exceptions.InternalServerErrorException("Internal server error.")

    for key in data:
        if key in IGNORED_FIELDS:
            continue
        if key not in PLATFORM_FIELDS:
            raise handlers_exceptions.UnprocessableEntityException(f'The key "{key}" is not allowed.')

    platforms_model = get_models(current_app).platforms
    result = platforms_model.patch(platform_id, PlatformPatch(**data))

    return respond_success(result.to_json())


@platforms_controller.route('/<string:platform_id>', methods=["DELETE"])
@requires_auth
@requires_role("admin")
def delete_platform(platform_id: str):
    """
    Delete a game store platform by its ID.

    This endpoint facilitates the deletion of a game store platform from the database using the provided platform_id.
    The function checks the existence of the platform before attempting deletion. It is restricted to users with admin roles.

    :param str platform_id: The unique identifier of the game store platform to be deleted.
    :return: A success message confirming the deletion if the platform exists, otherwise an error response.
    :rtype: Response
    """

    platforms_model = get_models(current_app).platforms
    deleted_platform = platforms_model.delete(platform_id)

    if deleted_platform is None:
        return respond_error(f'The platform with ID {platform_id} was not found.', 404)

    return respond_success({"message": f"Platform id {platform_id} successfully deleted", "deleted_platform": deleted_platform.to_json()})
